"""Timed recording controller. All live answers come from the real RAG pipeline."""
from dataclasses import dataclass
from concurrent.futures import Future
from pathlib import Path
import re
import textwrap
import logging

logger = logging.getLogger('lumen.recording')


QUESTIONS = {
    'positive': 'Dinh Độc Lập do ai thiết kế?',
    'negative': 'Giá vé máy bay từ TP.HCM đi Tokyo ngày mai là bao nhiêu?',
}


@dataclass(frozen=True)
class Scene:
    key: str
    seconds: int
    title: str
    speech: str


def scenes(script_path):
    paragraphs = [' '.join(line[2:] for line in part.splitlines() if line.startswith('> '))
                  for part in re.split(r'(?m)^## ', Path(script_path).read_text(encoding='utf-8'))[1:]]
    voice = [p for p in paragraphs if p]
    if len(voice) != 11:
        raise ValueError('Kịch bản cần 11 đoạn lời thoại. Kiểm tra docs/VIDEO_SCRIPT.md.')
    return [
        Scene('intro', 10, 'Lumen Travel', voice[0]),
        Scene('auth', 8, 'Đăng nhập', 'Ứng dụng dùng Firebase Authentication để xác thực tài khoản. Trang chat chỉ được mở sau khi đăng nhập thành công.'),
        Scene('ask_positive', 3, 'Câu hỏi về Dinh Độc Lập', 'Em hỏi: Dinh Độc Lập do ai thiết kế?'),
        Scene('positive_result', 16, 'Câu trả lời và nguồn', voice[2]),
        Scene('ask_negative', 3, 'Câu hỏi ngoài cẩm nang', 'Tiếp theo là câu hỏi ngoài cẩm nang.'),
        Scene('negative_result', 14, 'Khi cẩm nang thiếu dữ kiện', voice[3]),
        Scene('logout', 7, 'Đăng xuất', voice[4]),
        Scene('abstraction', 26, 'Abstraction', voice[5]),
        Scene('decomposition', 31, 'Decomposition', voice[6]),
        Scene('pattern', 28, 'Pattern recognition', voice[7]),
        Scene('algorithm', 38, 'Algorithm design', voice[8]),
        Scene('tests', 34, 'Kết quả kiểm thử', voice[9]),
        Scene('closing', 10, 'Hạn chế và kết thúc', voice[10]),
    ]


class DemoRun:
    """Clock and future state only; no Streamlit calls from worker threads."""
    def __init__(self, scene_list, now, countdown=8):
        self.version = 2
        self.scenes = scene_list
        self.epoch = now + countdown
        self.position = -1
        self.entered = self.epoch
        self.jobs: dict[str, Future] = {}
        self.results = {}
        self.events = []
        self.error = None
        self.complete = False
        self.signed_out = False
        self.error_kind = None

    def _fail(self, message, kind, exc=None):
        self.error_kind = kind
        detail = getattr(exc, 'public_message', '') if exc else ''
        self.error = message + ('\n\n' + detail if detail else '')
        if exc:
            logger.error('Recording question failed: %s', type(exc).__name__, exc_info=(type(exc), exc, exc.__traceback__))

    def retry(self, now, submit):
        kind = self.error_kind
        if self.signed_out or kind not in QUESTIONS:
            return False
        old_job = self.jobs.get(kind)
        if old_job is not None and not old_job.done():
            return False
        try:
            self.jobs[kind] = submit(QUESTIONS[kind])
        except Exception as exc:
            self._fail('Chưa thể gửi lại câu hỏi.', kind, exc)
            return False
        self.results.pop(kind, None)
        self.error = None
        self.error_kind = None
        self.entered = now
        self.events[-1]['speech_at'] = None if self.scene.key.endswith('_result') else round(now-self.epoch, 3)
        return True

    @property
    def scene(self):
        return self.scenes[self.position] if self.position >= 0 else None

    def _enter(self, position, now, submit):
        self.position, self.entered = position, now
        scene = self.scene
        waiting = scene.key in ('positive_result', 'negative_result')
        self.events.append({'key': scene.key, 'title': scene.title,
                            'start': round(now - self.epoch, 3), 'end': None,
                            'speech_at': None if waiting else round(now - self.epoch, 3),
                            'speech': scene.speech})
        if scene.key.startswith('ask_'):
            kind = scene.key.removeprefix('ask_')
            try:
                self.jobs[kind] = submit(QUESTIONS[kind])
            except Exception as exc:
                self._fail('Không khởi tạo được câu hỏi.', kind, exc)
        if scene.key == 'logout':
            self.signed_out = True
            self.results.clear()
            self.jobs.clear()

    def tick(self, now, submit):
        if self.complete or self.error or now < self.epoch:
            return
        for kind, job in self.jobs.items():
            if kind not in self.results and job.done():
                try:
                    result = job.result()
                    self.results[kind] = result.to_dict() if hasattr(result, 'to_dict') else result
                except Exception as exc:
                    self._fail('Chưa lấy được phản hồi từ mô hình.', kind, exc)
                    return
        if self.position < 0:
            self._enter(0, now, submit)
            return
        key = self.scene.key
        if key in ('positive_result', 'negative_result'):
            kind = key.removesuffix('_result')
            if kind not in self.results:
                if now - self.entered > 180:
                    self._fail('Mô hình chờ quá lâu. Đợi tác vụ cũ kết thúc rồi thử lại.', kind)
                return
            result = self.results[kind]
            valid = (result['status'] == 'answered' and 'G02' in result['source_ids']
                     and 'ngô viết thụ' in result['answer'].casefold()) if kind == 'positive' else result['status'] == 'unknown'
            if not valid:
                self._fail('Kết quả chưa đạt kỳ vọng của kịch bản. Hãy đối chiếu đáp án bên dưới.', kind)
                return
            if self.events[-1]['speech_at'] is None:
                self.entered = now
                self.events[-1]['speech_at'] = round(now - self.epoch, 3)
        if now - self.entered >= self.scene.seconds:
            self.events[-1]['end'] = round(now - self.epoch, 3)
            if self.position + 1 == len(self.scenes):
                self.complete = True
            else:
                self._enter(self.position + 1, now, submit)


def timestamp(seconds):
    milliseconds = max(0, round(seconds * 1000))
    hours, remainder = divmod(milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    secs, milliseconds = divmod(remainder, 1000)
    return f'{hours:02}:{minutes:02}:{secs:02},{milliseconds:03}'


def subtitles(events):
    output = []
    for event in events:
        if event['end'] is None or event['speech_at'] is None:
            continue
        lines = textwrap.wrap(event['speech'], width=43, break_long_words=False)
        chunks = ['\n'.join(lines[i:i+2]) for i in range(0, len(lines), 2)]
        if not chunks:
            continue
        span = event['end'] - event['speech_at']
        weights = [len(chunk.split()) for chunk in chunks]
        total, elapsed = sum(weights), 0
        for chunk, weight in zip(chunks, weights):
            begin = event['speech_at'] + span * elapsed / total
            elapsed += weight
            end = event['speech_at'] + span * elapsed / total
            output.append(f'{len(output)+1}\n{timestamp(begin)} --> {timestamp(end)}\n{chunk}\n')
    return '\n'.join(output)
