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


def current_url():
    # Launcher can renew an expired tunnel while this page is still running.
    return (dotenv_values(ROOT/'.env').get('OLLAMA_BASE_URL') or OLLAMA_BASE_URL).rstrip('/')

st.set_page_config(page_title='Lumen · Demo tự chạy', page_icon='🌿', layout='wide')
st.markdown('''<style>
.block-container{padding-top:1.4rem;max-width:1250px}
h1{font-size:2.3rem!important} h2{font-size:1.7rem!important}
[data-testid="stCaptionContainer"]{font-size:.95rem}
</style>''', unsafe_allow_html=True)
st.title('🌿 Lumen Travel')
st.caption('TRẦN HẢI THIÊN · 25127007 · Tự trình diễn · Câu hỏi gọi mô hình thật')


@st.cache_resource
def executor():
    return ThreadPoolExecutor(max_workers=1, thread_name_prefix='lumen-recording')


def clear_private_state():
    for key in ('user', 'messages', 'record_index'):
        st.session_state.pop(key, None)


def render_result(kind, run):
    with st.chat_message('user'):
        st.write(QUESTIONS[kind])
    result = run.results.get(kind)
    if not result:
        st.info('Đang chờ phản hồi thật từ Ollama… Chưa có đáp án để hiển thị.')
        return
    st.success(result['answer'])
    columns = st.columns(3)
    for col, item in zip(columns, result['retrieved_entries']):
        entry = item['entry']
        with col, st.container(border=True):
            st.markdown(f"**[{entry['id']}] {entry['title']}**")
            st.caption(f"Cosine: {item['score']:.3f}")
            st.write(entry['text'])
            st.link_button('Nguồn tham khảo', entry['source'])


def render_tests():
    st.caption('BÁO CÁO ĐÃ LƯU · 16/11/2026 · Không phải kết quả chạy lại ở màn hình này')
    data = json.loads((ROOT/'docs/evaluation-real.json').read_text(encoding='utf-8'))
    rows = []
    for item in data:
        if item['id'] in ('T01', 'T05', 'E01'):
            rows.append({'Test': item['id'], 'Câu hỏi': item['question'],
                         'ID kỳ vọng': ', '.join(item['expected_ids']) or 'Không có dữ kiện',
                         'ID truy xuất': ', '.join(item['retrieved_ids']),
                         'Kết quả': 'Đạt' if item['passed_automatic'] else 'Chưa đạt — retrieval'})
    st.table(rows)
    st.warning('E01: cẩm nang có đủ bốn bảo tàng, nhưng top-3 thiếu G08. T05 nói không biết là kết quả đúng vì cẩm nang không có giá vé.')


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
    st.info('Phần phân tích chạy trong lúc chờ mô hình. Mục tiêu khoảng 4 phút 26 giây; có thể dài hơn nếu máy hoặc kết nối chậm. Không thay phản hồi thật bằng đáp án mẫu.')
    if st.button('1. Chuẩn bị cẩm nang', type='primary'):
        try:
            with st.spinner('Đang tạo/lấy chỉ mục từ mô hình thật…'):
                st.session_state.record_index = build_index((ROOT/'knowledge_base.json').read_text(encoding='utf-8'), current_url())
            st.success('Cẩm nang đã sẵn sàng.')
        except (RagError, OSError) as exc:
            st.error(str(exc))
    if 'record_index' in st.session_state:
        st.checkbox('Hiện lời thoại để đọc theo', value=True, key='record_show_speech')
        if st.button('2. Bắt đầu — đếm ngược 8 giây để bấm quay', type='primary'):
            st.session_state.record_run = DemoRun(scenes(ROOT/'docs/VIDEO_SCRIPT.md'), time.monotonic())
            st.rerun()
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
        st.header(f'Bắt đầu sau {max(0, int(run.epoch-now)+1)} giây')
        st.write('Bấm quay màn hình ngay bây giờ. Có thể cắt đoạn đếm ngược khi dựng.')
        return
    elapsed = max(0, now-run.epoch)
    st.caption(f'Bước {run.position+1}/{len(run.scenes)} · {int(elapsed)//60:02}:{int(elapsed)%60:02} · Mọi câu trả lời demo đều lấy từ mô hình thật')
    st.progress((run.position+1)/len(run.scenes))
    if elapsed > 290 and not run.complete:
        st.warning('Video đang gần giới hạn 5 phút. Nếu cần, cắt đoạn chờ và chú thích rõ khi dựng.')
    if run.error:
        st.error(run.error)
        for kind in run.results:
            render_result(kind, run)
        return
    scene = run.scene
    st.header(scene.title)
    key = scene.key
    if key == 'intro':
        st.markdown('## Trợ lý du lịch Thành phố Hồ Chí Minh')
        st.write('Streamlit · Firebase Authentication · Ollama + Pinggy · RAG có nguồn')
        st.metric('Cẩm nang', '16 mục', '12 địa điểm + 4 hướng dẫn')
    elif key == 'auth':
        st.success('Phiên người dùng đã được xác thực bằng Firebase Authentication.')
        st.write('Đăng nhập thật đã thực hiện trước phần tự trình diễn. Nếu cần ghi thao tác đăng nhập, quay màn hình ngay từ form đăng nhập.')
        st.write('Chưa đăng nhập → không truy cập chat. Đăng xuất → xóa lịch sử phiên.')
    elif key in ('ask_positive', 'positive_result', 'ask_negative', 'negative_result'):
        kind = 'positive' if 'positive' in key else 'negative'
        render_result(kind, run)
    elif key == 'abstraction':
        st.write('Đầu vào: câu hỏi du lịch của người đã đăng nhập. Đầu ra: đáp án có trích dẫn hoặc thông báo thiếu dữ kiện.')
        st.table([{'Trường': 'id', 'Vai trò': 'Định danh để trích dẫn, ví dụ G02'},
                  {'Trường': 'title, text', 'Vai trò': 'Embedding và dữ kiện trả lời'},
                  {'Trường': 'source', 'Vai trò': 'URL nguồn để đối chiếu'},
                  {'Trường': 'category, tags', 'Vai trò': 'Chuẩn bị cho bài RAG-Rec'}])
    elif key == 'decomposition':
        st.graphviz_chart('''digraph { rankdir=LR; node [shape=box,style=rounded];
        a [label="Đăng nhập\nEmail + mật khẩu → phiên"];
        b [label="Embedding\nCâu hỏi → vector"];
        c [label="Truy xuất\nVectors → 3 mục + điểm"];
        d [label="Ghép context\nCâu hỏi + mục → prompt"];
        e [label="Sinh đáp án\nPrompt → JSON"];
        f [label="Hiển thị\nJSON + nguồn → chat"];
        a -> b -> c -> d -> e -> f; }''')
        st.info('Cẩm nang JSON → embedding một lần → cache chỉ mục. Kiểm tra ID trích dẫn trước khi hiển thị.')
    elif key == 'pattern':
        st.table([{'Nguồn': 'Lab 3', 'Tái sử dụng': 'Streamlit, session state, Firebase Authentication'},
                  {'Nguồn': 'Lab 4', 'Tái sử dụng': 'Ollama + Pinggy, embedding, RAG'}])
        st.subheader('filter → score → top-k')
        st.write('Hiện tại: kiểm tra cẩm nang → tính cosine cho 16 mục → lấy top-3.')
        st.write('RAG-Rec tiếp theo: có thể lọc category/tags theo sở thích → chấm điểm → chọn địa điểm.')
    elif key == 'algorithm':
        st.code('''nếu chưa đăng nhập hoặc câu hỏi rỗng: dừng
index = lấy chỉ mục cẩm nang đã cache
vector = embeddinggemma(câu hỏi)
entries = top_3(cosine(vector, index))
context = ghép câu hỏi và entries
result = qwen3:4b(context, chỉ dùng dữ kiện trong context)
nếu thiếu dữ kiện: trả lời không biết
kiểm tra IDs thuộc entries, bổ sung dấu trích dẫn hợp lệ
hiển thị câu trả lời và nguồn; lưu lịch sử trong session''', language='text')
        st.info('k = 3: context gọn, giảm nhu cầu bộ nhớ. G02 đủ cho câu hỏi Dinh Độc Lập; câu hỏi cần bốn mục có thể bị thiếu context.')
    elif key == 'logout':
        st.success('Đã đăng xuất: phiên người dùng và lịch sử của phần demo đã được xóa.')
        st.write('Phần tiếp theo chỉ trình bày báo cáo kiểm thử đã lưu; không mở chat khi chưa đăng nhập.')
    elif key == 'tests':
        render_tests()
    elif key == 'closing':
        st.write('Dữ liệu tĩnh · top-3 có thể thiếu mục · CPU phản hồi chậm · tunnel cần duy trì kết nối')
        st.write('Codex hỗ trợ code, nháp dữ liệu, kiểm thử và tài liệu. Sinh viên duyệt và giải thích giải pháp.')
        st.link_button('Repository công khai', 'https://github.com/comrange1104/lumen-travel-hcm-rag')
    waiting = key in ('positive_result', 'negative_result') and key.removesuffix('_result') not in run.results
    if st.session_state.get('record_show_speech', True) and not waiting:
        st.info('Lời thuyết minh: ' + scene.speech)
    if run.complete:
        st.success('TRÌNH DIỄN ĐÃ KẾT THÚC — bạn có thể dừng quay.')
        st.download_button('Tải phụ đề SRT theo thời gian thực tế', subtitles(run.events), 'lumen-demo.srt', mime='application/x-subrip')
        st.download_button('Tải mốc thời gian để ghép giọng đọc', json.dumps(run.events, ensure_ascii=False, indent=2), 'lumen-timeline.json', mime='application/json')


if st.button('Dừng / chuẩn bị quay lại'):
    for job in run.jobs.values():
        job.cancel()
    st.session_state.pop('record_run', None)
    st.rerun()
presentation()
