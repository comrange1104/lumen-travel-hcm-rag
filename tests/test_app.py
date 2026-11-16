import time
import unittest
from unittest.mock import patch
from streamlit.testing.v1 import AppTest
from config import ROOT
from firebase_client import FirebaseError


class AppTests(unittest.TestCase):
    def user(self, email='a@example.test'):
        return {'uid': email, 'email': email, 'expires_at': time.time()+3600,
                'id_token': 'test', 'refresh_token': 'test'}

    def test_logged_out_has_no_chat(self):
        app = AppTest.from_file(str(ROOT/'app.py')).run()
        self.assertFalse(app.exception)
        self.assertEqual(len(app.chat_input), 0)
        self.assertEqual(len(app.text_input), 2)

    def test_login_logout_and_session_isolation(self):
        first = AppTest.from_file(str(ROOT/'app.py')).run()
        first.text_input[0].set_value('a@example.test')
        first.text_input[1].set_value('test-password')
        with patch('firebase_client.sign_in', return_value=self.user()):
            first.button[0].click().run()
        self.assertFalse(first.exception)
        self.assertEqual(len(first.chat_input), 1)
        second = AppTest.from_file(str(ROOT/'app.py')).run()
        self.assertEqual(len(second.chat_input), 0)
        first.session_state['messages'] = [{'role': 'user', 'content': 'Lịch sử riêng'}]
        first.run()
        first.sidebar.button[0].click().run()
        self.assertEqual(len(first.chat_input), 0)
        self.assertNotIn('user', first.session_state)
        self.assertNotIn('messages', first.session_state)

    def test_bad_login_does_not_unlock_chat(self):
        app = AppTest.from_file(str(ROOT/'app.py')).run()
        app.text_input[0].set_value('a@example.test')
        app.text_input[1].set_value('bad')
        with patch('firebase_client.sign_in', side_effect=FirebaseError('Email hoặc mật khẩu chưa đúng.')):
            app.button[0].click().run()
        self.assertEqual(len(app.chat_input), 0)
        self.assertEqual(len(app.error), 1)


if __name__ == '__main__':
    unittest.main()
