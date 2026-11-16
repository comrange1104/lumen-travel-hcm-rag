from concurrent.futures import Future
import time
import unittest
from unittest.mock import patch
from streamlit.testing.v1 import AppTest
from config import ROOT
from recording import DemoRun, Scene, scenes, subtitles, timestamp


def response(kind):
    return {'answer': 'Ngô Viết Thụ [G02]' if kind == 'positive' else 'Mình không có thông tin này trong cẩm nang.',
            'source_ids': ['G02'] if kind == 'positive' else [], 'retrieved_entries': [],
            'status': 'answered' if kind == 'positive' else 'unknown'}


class RecordingTests(unittest.TestCase):
    def test_script_timeline_has_required_parts(self):
        data = scenes(ROOT/'docs/VIDEO_SCRIPT.md')
        self.assertEqual(len(data), 13)
        self.assertEqual(sum(s.seconds for s in data), 266)
        self.assertTrue(all(s.speech for s in data))

    def test_waits_for_real_result_and_allows_reading_after_arrival(self):
        job = Future()
        run = DemoRun([Scene('ask_positive', 1, 'Ask', 'Ask'),
                       Scene('positive_result', 2, 'Result', 'Read')], 0, countdown=0)
        run.tick(0, lambda _: job)
        run.tick(1, lambda _: self.fail('Must not submit twice'))
        run.tick(30, lambda _: self.fail('Must not submit twice'))
        self.assertFalse(run.complete)
        self.assertIsNone(run.events[-1]['speech_at'])
        job.set_result(response('positive'))
        run.tick(31, lambda _: None)
        self.assertFalse(run.complete)
        run.tick(33, lambda _: None)
        self.assertTrue(run.complete)
        self.assertEqual(run.events[-1]['speech_at'], 31)

    def test_wrong_model_answer_halts_instead_of_replacing_it(self):
        job = Future()
        job.set_result({'answer': 'Sai', 'source_ids': [], 'status': 'unknown'})
        run = DemoRun([Scene('ask_positive', 1, 'Ask', 'Ask'),
                       Scene('positive_result', 1, 'Answer', 'Read')], 0, 0)
        run.tick(0, lambda _: job)
        run.tick(1, lambda _: job)
        run.tick(2, lambda _: job)
        self.assertIsNotNone(run.error)
        self.assertEqual(run.results['positive']['answer'], 'Sai')
        self.assertFalse(run.complete)

    def test_sign_out_discards_live_history(self):
        run = DemoRun([Scene('intro', 1, 'Intro', 'Hello'),
                       Scene('logout', 1, 'Logout', 'Bye')], 0, 0)
        run.tick(0, lambda _: None)
        run.results['positive'] = response('positive')
        run.tick(1, lambda _: None)
        self.assertTrue(run.signed_out)
        self.assertEqual(run.results, {})
        self.assertEqual(run.jobs, {})

    def test_subtitles_use_observed_timing_and_skip_unfinished_events(self):
        self.assertEqual(timestamp(61.125), '00:01:01,125')
        result = subtitles([{'speech': 'Xin chào Trần Hải Thiên', 'speech_at': 3, 'end': 6},
                            {'speech': 'Not ready', 'speech_at': None, 'end': None}])
        self.assertIn('00:00:03,000 --> 00:00:06,000', result)
        self.assertNotIn('Not ready', result)

    def test_recording_page_keeps_authentication_gate(self):
        app = AppTest.from_file(str(ROOT/'record_demo.py')).run()
        self.assertFalse(app.exception)
        self.assertEqual([i.label for i in app.text_input], ['Email', 'Mật khẩu'])
        self.assertEqual(len(app.chat_input), 0)
        self.assertFalse(any('Bắt đầu' in b.label for b in app.button))

    def test_every_presentation_scene_renders(self):
        scene_list = scenes(ROOT/'docs/VIDEO_SCRIPT.md')
        for position, scene in enumerate(scene_list):
            with self.subTest(scene=scene.key):
                now = time.monotonic()
                run = DemoRun(scene_list, now, 0)
                run.position = position
                run.entered = now
                run.results = {'positive': response('positive'), 'negative': response('negative')}
                run.events = [{'key': scene.key, 'title': scene.title, 'start': 0,
                               'end': None, 'speech_at': 0, 'speech': scene.speech}]
                if scene.key in ('logout', 'tests', 'closing'):
                    run.signed_out = True
                    run.results.clear()
                app = AppTest.from_file(str(ROOT/'record_demo.py'))
                if not run.signed_out:
                    app.session_state['user'] = {'email': 'demo@example.test', 'uid': 'test',
                                                 'expires_at': now+time.time()+3600,
                                                 'id_token': 'test', 'refresh_token': 'test'}
                app.session_state['record_run'] = run
                app.run()
                self.assertFalse(app.exception)

    def test_complete_sequence_submits_each_question_once(self):
        scene_list = scenes(ROOT/'docs/VIDEO_SCRIPT.md')
        run = DemoRun(scene_list, 0, 0)
        calls = []
        def submit(question):
            calls.append(question)
            job = Future()
            job.set_result(response('positive' if len(calls) == 1 else 'negative'))
            return job
        for now in range(300):
            run.tick(now, submit)
            if run.complete:
                break
        self.assertTrue(run.complete)
        self.assertEqual(len(calls), 2)
        self.assertTrue(run.signed_out)
        self.assertEqual(run.results, {})
        self.assertTrue(all(e['end'] is not None for e in run.events))

    def test_authenticated_preparation_does_not_start_questions(self):
        app = AppTest.from_file(str(ROOT/'record_demo.py'))
        app.session_state['user'] = {'email': 'demo@example.test', 'uid': 'test',
                                     'expires_at': time.time()+3600, 'id_token': 'test', 'refresh_token': 'test'}
        app.run()
        with patch('rag.build_index', return_value=([], [])), patch('rag.answer_question') as answer:
            app.button[0].click().run()
            self.assertFalse(app.exception)
            self.assertTrue(any('Bắt đầu' in b.label for b in app.button))
            answer.assert_not_called()


if __name__ == '__main__':
    unittest.main()
