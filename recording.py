"""Timed recording controller. All live answers come from the real RAG pipeline."""
from dataclasses import dataclass
from concurrent.futures import Future
from pathlib import Path
import re
import textwrap


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
        Scene('intro', 12, 'Lumen Travel · Trần Hải Thiên · 25127007', voice[0]),
        Scene('auth', 12, 'Firebase Authentication', 'Đây là phiên đăng nhập thật qua Firebase Authentication. Trang chat chỉ được mở sau khi xác thực thành công.'),
        Scene('ask_positive', 4, 'Gửi câu hỏi có đáp án', 'Em hỏi: Dinh Độc Lập do ai thiết kế?'),
        Scene('abstraction', 30, 'Abstraction · Trừu tượng hóa', voice[5]),
        Scene('decomposition', 35, 'Decomposition · Chia nhỏ bài toán', voice[6]),
        Scene('positive_result', 14, 'Kết quả câu hỏi có đáp án', voice[2]),
        Scene('ask_negative', 4, 'Gửi câu hỏi ngoài cẩm nang', 'Tiếp theo là câu hỏi ngoài cẩm nang.'),
        Scene('pattern', 35, 'Pattern recognition · Nhận diện mẫu', voice[7]),
        Scene('algorithm', 45, 'Algorithm design · Thiết kế thuật toán', voice[8]),
        Scene('negative_result', 12, 'Kết quả câu hỏi ngoài cẩm nang', voice[3]),
        Scene('logout', 8, 'Đăng xuất · Xóa lịch sử phiên', voice[4]),
        Scene('tests', 45, 'Kiểm thử · Thành công và giới hạn', voice[9]),
        Scene('closing', 10, 'Hạn chế và kết thúc', voice[10]),
    ]


class DemoRun:
    """Clock and future state only; no Streamlit calls from worker threads."""
    def __init__(self, scene_list, now, countdown=8):
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
            except Exception:
                self.error = 'Không khởi tạo được câu hỏi thật. Kiểm tra đăng nhập, cấu hình Ollama và chuẩn bị lại.'
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
                except Exception:
                    self.error = 'Không lấy được phản hồi thật từ Ollama. Dừng quay, kiểm tra server/Pinggy rồi chuẩn bị lại.'
                    return
        if self.position < 0:
            self._enter(0, now, submit)
            return
        key = self.scene.key
        if key in ('positive_result', 'negative_result'):
            kind = key.removesuffix('_result')
            if kind not in self.results:
                if now - self.entered > 180:
                    self.error = 'Mô hình chờ quá lâu. Dừng quay và kiểm tra kết nối.'
                return
            result = self.results[kind]
            valid = (result['status'] == 'answered' and 'G02' in result['source_ids']
                     and 'ngô viết thụ' in result['answer'].casefold()) if kind == 'positive' else result['status'] == 'unknown'
            if not valid:
                self.error = 'Kết quả thật chưa đạt kỳ vọng của kịch bản. Demo đã dừng; hãy đối chiếu đáp án bên dưới trước khi quay lại.'
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
