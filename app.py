"""Run with: streamlit run app.py"""
import time
import streamlit as st
from config import ROOT, OLLAMA_BASE_URL
from firebase_client import sign_up, sign_in, refresh_user, FirebaseError
from rag import build_index, OllamaClient, answer_question, RagError

st.set_page_config(page_title='Lumen · Sài Gòn trong cẩm nang', page_icon='🌿', layout='centered')
st.title('🌿 Lumen Travel')
st.caption('Khám phá TP. Hồ Chí Minh · Câu trả lời có nguồn')


def auth_screen():
    st.subheader('Chào bạn, cùng khám phá Sài Gòn')
    st.write('Đăng nhập để hỏi cẩm nang du lịch với 16 chủ đề được chọn lọc.')
    with st.form('auth'):
        mode = st.radio('Tài khoản', ['Đăng nhập', 'Đăng ký'], horizontal=True)
        email = st.text_input('Email', max_chars=254)
        password = st.text_input('Mật khẩu', type='password')
        submitted = st.form_submit_button('Tiếp tục', use_container_width=True)
    if submitted:
        try:
            if mode == 'Đăng ký':
                sign_up(email, password)
                st.success('Đăng ký thành công. Hãy chọn Đăng nhập để tiếp tục.')
            else:
                st.session_state.user = sign_in(email, password)
                st.session_state.messages = []
                st.rerun()
        except FirebaseError as exc:
            st.error(str(exc))


def display_sources(result):
    with st.expander('Xem 3 mục được truy xuất và điểm tương đồng'):
        for item in result['retrieved_entries']:
            entry = item['entry']
            st.markdown(f"**[{entry['id']}] {entry['title']}** · cosine {item['score']:.3f}")
            st.write(entry['text'])
            st.link_button('Mở nguồn tham khảo', entry['source'])


if 'user' not in st.session_state:
    auth_screen()
    st.stop()

with st.sidebar:
    st.header('Cẩm nang của bạn')
    st.write(st.session_state.user['email'])
    st.caption('12 địa điểm · 4 hướng dẫn thực tế')
    st.write('Gợi ý câu hỏi:')
    st.write('• Dinh Độc Lập do ai thiết kế?\n• Bảo tàng Áo dài trưng bày gì?\n• TP.HCM thường có mưa vào tháng nào?')
    st.caption('Giá vé, lịch và giờ mở cửa chưa được đưa vào cẩm nang. Hãy hỏi câu đầy đủ tên địa điểm.')
    if st.button('Đăng xuất', use_container_width=True):
        st.session_state.clear()
        st.rerun()

try:
    st.session_state.user = refresh_user(st.session_state.user)
except FirebaseError as exc:
    st.session_state.clear()
    st.error(str(exc))
    st.info('Tải lại trang để đăng nhập.')
    st.stop()

st.session_state.setdefault('messages', [])
for message in st.session_state.messages:
    with st.chat_message(message['role']):
        st.write(message['content'])
        if message.get('result'):
            display_sources(message['result'])

if question := st.chat_input('Bạn muốn tìm hiểu gì về TP. Hồ Chí Minh?', max_chars=1500):
    if not question.strip():
        st.warning('Vui lòng nhập một câu hỏi.')
        st.stop()
    st.session_state.messages.append({'role': 'user', 'content': question})
    with st.chat_message('user'):
        st.write(question)
    try:
        with st.spinner('Đang tra cẩm nang và chuẩn bị câu trả lời…'):
            start = time.perf_counter()
            index = build_index((ROOT / 'knowledge_base.json').read_text(encoding='utf-8'), OLLAMA_BASE_URL)
            result = answer_question(question, index, OllamaClient(OLLAMA_BASE_URL)).to_dict()
        st.session_state.messages.append({'role': 'assistant', 'content': result['answer'], 'result': result})
        with st.chat_message('assistant'):
            st.write(result['answer'])
            display_sources(result)
            st.caption(f"Thời gian xử lý: {time.perf_counter() - start:.1f} giây")
    except (RagError, OSError) as exc:
        # Operational failures are not saved as fabricated travel answers.
        st.error(str(exc) if isinstance(exc, RagError) else 'Không đọc được tệp cẩm nang.')
        st.info('Kiểm tra kết nối rồi gửi lại câu hỏi.')
