"""Dedicated, transparent automatic presentation; real Firebase and real RAG."""
import json
import time
from concurrent.futures import ThreadPoolExecutor
import streamlit as st
from dotenv import dotenv_values
from config import ROOT, OLLAMA_BASE_URL
from firebase_client import sign_in, refresh_user, FirebaseError
from rag import build_index, OllamaClient, answer_question, RagError
from recording import DemoRun, QUESTIONS, scenes, subtitles
import recording_ui as ui
import ollama_runtime


def current_url():
    # Launcher can renew an expired tunnel while this page is still running.
    return (dotenv_values(ROOT/'.env').get('OLLAMA_BASE_URL') or OLLAMA_BASE_URL).rstrip('/')

st.set_page_config(page_title='Lumen Travel · Trình bày đồ án', page_icon='🌿', layout='wide')
previous_run = st.session_state.get('record_run')
if previous_run is not None and getattr(previous_run, 'version', None) != 2:
    for job in previous_run.jobs.values():
        job.cancel()
    st.session_state.pop('record_run', None)
ui.apply_style(st.session_state.get('record_run') is not None)
if st.session_state.get('record_run') is None:
    st.title('🌿 Lumen Travel')
    st.caption('TRẦN HẢI THIÊN · 25127007')


@st.cache_resource
def executor():
    return ThreadPoolExecutor(max_workers=1, thread_name_prefix='lumen-recording')


def clear_private_state():
    for key in ('user', 'messages', 'record_index'):
        st.session_state.pop(key, None)


def render_result(kind, run):
    result = run.results.get(kind)
    if not result:
        ui.body('Đang tra cứu cẩm nang…')
        return
    ui.body(result['answer'], kind='answer')
    ui.sources(result)


def render_tests():
    st.caption('Kết quả kiểm thử · 16/11/2026')
    data = json.loads((ROOT/'docs/evaluation-real.json').read_text(encoding='utf-8'))
    by_id = {item['id']: item for item in data}
    good, failure = by_id['T01'], by_id['E01']
    ui.cards([('T01 · Thành công', f"{good['question']}\nKỳ vọng: G02.\nKết quả: {good['answer']}"),
              ('E01 · Giới hạn truy xuất', 'Yêu cầu liệt kê bốn bảo tàng.\nCần: G03, G08, G09, G10.\nĐã lấy: '+', '.join(failure['retrieved_ids'])+'.\nThiếu G08 → context chưa đủ.')])
    ui.body('6/6 câu hỏi chính đạt · E01 ghi nhận giới hạn top-3', kind='footnote')


run = st.session_state.get('record_run')
public_tail = run is not None and run.signed_out
if 'user' not in st.session_state and not public_tail:
    st.subheader('Đăng nhập Firebase trước khi quay')
    st.write('Dùng tài khoản đã đăng ký trong ứng dụng. Sau đó chuẩn bị cẩm nang và bắt đầu đếm ngược.')
    with st.form('record_login'):
        email = st.text_input('Email')
        password = st.text_input('Mật khẩu', type='password')
        login = st.form_submit_button('Đăng nhập')
    if login:
        try:
            st.session_state.user = sign_in(email, password)
            st.session_state.pop('record_run', None)
            st.rerun()
        except FirebaseError as exc:
            st.error(str(exc))
    st.caption('Đây là xác thực thật. Mật khẩu chỉ được gửi tới Firebase để đăng nhập, không được ghi vào kịch bản hay lưu để tự đăng nhập.')
    st.stop()

if not public_tail:
    try:
        st.session_state.user = refresh_user(st.session_state.user)
    except FirebaseError as exc:
        clear_private_state()
        st.session_state.pop('record_run', None)
        st.error(str(exc))
        st.stop()

if run is None:
    st.success('Đã đăng nhập Firebase. Bước tiếp theo: chuẩn bị chỉ mục trước khi bấm quay.')
    st.write('Demo tự gửi hai câu hỏi, hiển thị kết quả và nguồn, trình bày bốn bước Computational Thinking, đăng xuất và mở bảng kiểm thử.')
    st.info('Trình tự: demo hỏi–đáp → đăng xuất → bốn phần Computational Thinking → kiểm thử. Thời gian trình bày khoảng 3 phút 48 giây, cộng thời gian mô hình xử lý; có thể cần cắt gọn đoạn chờ để video dưới 5 phút.')
    if st.button('1. Chuẩn bị cẩm nang', type='primary'):
        try:
            with st.spinner('Đang tạo/lấy chỉ mục từ mô hình thật…'):
                base_url = ollama_runtime.ensure_connection(current_url())
                st.session_state.record_index = build_index((ROOT/'knowledge_base.json').read_text(encoding='utf-8'), base_url)
            st.success('Cẩm nang đã sẵn sàng.')
        except (RagError, OSError, ollama_runtime.ConnectionSetupError) as exc:
            st.error(str(exc))
    if 'record_index' in st.session_state:
        st.checkbox('Hiện nội dung thuyết trình', value=True, key='record_show_speech')
        if st.button('2. Bắt đầu — đếm ngược 8 giây để bấm quay', type='primary'):
            try:
                with st.spinner('Kiểm tra kết nối trước khi quay…'):
                    ollama_runtime.ensure_connection(current_url())
                st.session_state.record_run = DemoRun(scenes(ROOT/'docs/VIDEO_SCRIPT.md'), time.monotonic())
                st.rerun()
            except ollama_runtime.ConnectionSetupError as exc:
                st.error(str(exc))
    st.stop()


@st.fragment(run_every=0.5)
def presentation():
    run = st.session_state.record_run
    now = time.monotonic()
    def submit(question):
        if 'user' not in st.session_state:
            raise FirebaseError('Cần đăng nhập trước khi gửi câu hỏi.')
        st.session_state.user = refresh_user(st.session_state.user)
        return executor().submit(answer_question, question, st.session_state.record_index, OllamaClient(current_url()))
    run.tick(now, submit)
    if run.signed_out:
        clear_private_state()
    if run.position < 0:
        ui.heading(str(max(0, int(run.epoch-now)+1)))
        ui.body('Chuẩn bị bắt đầu')
        return
    elapsed = max(0, now-run.epoch)
    if run.error:
        st.error(run.error)
        if st.button('Thử lại câu hỏi'):
            if run.retry(now, submit):
                st.rerun()
            else:
                st.info('Tác vụ trước đang kết thúc hoặc phiên đã đăng xuất. Chờ thêm một chút rồi thử lại.')
        for kind in run.results:
            render_result(kind, run)
        return
    scene = run.scene
    key = scene.key
    if key == 'intro':
        ui.intro()
    elif key in ('ask_positive', 'positive_result', 'ask_negative', 'negative_result'):
        ui.heading(QUESTIONS['positive' if 'positive' in key else 'negative'])
    else:
        ui.heading(scene.title)
    waiting = key in ('positive_result', 'negative_result') and key.removesuffix('_result') not in run.results
    if st.session_state.get('record_show_speech', True) and not waiting and key in ('intro', 'closing'):
        speech_start = run.events[-1].get('speech_at')
        if speech_start is not None:
            ui.narration(scene.speech, elapsed-speech_start, scene.seconds)
    if key == 'intro':
        ui.body('Streamlit · Firebase Authentication · Ollama + Pinggy · RAG', kind='footnote')
    elif key == 'auth':
        ui.body('Xác thực thành công', kind='answer')
        ui.body('Firebase Authentication bảo vệ quyền truy cập trang chat.')
    elif key in ('ask_positive', 'positive_result', 'ask_negative', 'negative_result'):
        kind = 'positive' if 'positive' in key else 'negative'
        render_result(kind, run)
    elif key == 'abstraction':
        ui.cards([('Đầu vào', 'Câu hỏi du lịch TP.HCM\nNgười dùng đã đăng nhập'),
                  ('Đầu ra', 'Câu trả lời kèm nguồn\nHoặc thông báo thiếu dữ kiện')])
        ui.body('16 mục · id / title / text / source · category / tags cho địa điểm', kind='footnote')
    elif key == 'decomposition':
        ui.pipeline()
        ui.body('Cẩm nang JSON → embedding một lần → cache chỉ mục')
    elif key == 'pattern':
        ui.cards([('Lab 3', 'Streamlit · Firebase · session state'),
                  ('Lab 4', 'Ollama + Pinggy · embedding · RAG')])
        ui.body('filter → score → top-k', kind='answer')
        ui.body('RAG-Rec: lọc category / tags → chấm điểm → chọn địa điểm')
    elif key == 'algorithm':
        st.code('''1. Kiểm tra đăng nhập và câu hỏi
2. Lấy chỉ mục cẩm nang đã cache
3. Embedding câu hỏi → tính cosine → lấy top-3
4. Ghép context → gọi qwen3:4b
5. Thiếu dữ kiện → trả lời không biết
6. Kiểm tra ID nguồn → hiển thị đáp án
7. Lưu hội thoại trong session''', language='text')
        ui.body('k = 3 · Context gọn · Giảm nhu cầu bộ nhớ')
    elif key == 'logout':
        ui.body('Đã đăng xuất', kind='answer')
        ui.body('Phiên người dùng và lịch sử hội thoại đã được xóa.')
    elif key == 'tests':
        render_tests()
    elif key == 'closing':
        ui.body('Dữ liệu tĩnh · Giới hạn top-3 · Tốc độ xử lý trên CPU')
        st.link_button('Repository công khai', 'https://github.com/comrange1104/lumen-travel-hcm-rag')
    if run.complete:
        st.caption('Hoàn tất. Bạn có thể dừng quay và tải phụ đề.')
        st.download_button('Tải phụ đề SRT theo thời gian thực tế', subtitles(run.events), 'lumen-demo.srt', mime='application/x-subrip')
        st.download_button('Tải mốc thời gian để ghép giọng đọc', json.dumps(run.events, ensure_ascii=False, indent=2), 'lumen-timeline.json', mime='application/json')


with st.container(key='record-controls'):
    with st.popover('⋯', help='Điều khiển trình chiếu'):
        st.checkbox('Hiện nội dung thuyết trình', value=st.session_state.get('record_show_speech', True), key='record_speech_control',
                    on_change=lambda: st.session_state.update(record_show_speech=st.session_state.record_speech_control))
        if st.button('Dừng / chuẩn bị quay lại'):
            for job in run.jobs.values():
                job.cancel()
            st.session_state.pop('record_run', None)
            st.rerun()
presentation()
