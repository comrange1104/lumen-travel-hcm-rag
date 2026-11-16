# Kịch bản video 4 phút 40 giây

Sinh viên: **Trần Hải Thiên — 25127007**.

Trước khi quay: chạy Ollama, tạo tunnel Pinggy mới, kiểm tra URL trong .env, mở app và chuẩn bị kết quả kiểm thử thật. Chỉ quay cửa sổ trình duyệt và tài liệu cần thiết. Có thể cắt gọn thời gian chờ và ghi chú việc cắt đoạn chờ.

## 0:00–1:20: Demo

“Em là Trần Hải Thiên, MSSV 25127007. Đây là Lumen Travel, trợ lý du lịch TP.HCM dựa trên cẩm nang 16 mục.”

- Đăng nhập bằng tài khoản thử nghiệm.
- Hỏi “Dinh Độc Lập do ai thiết kế?”. Mở bảng nguồn, chỉ vào G02 và điểm cosine.
- Hỏi “Bảo tàng Mỹ thuật TP.HCM mở cửa lúc mấy giờ vào Chủ nhật?”. Chỉ ra cẩm nang có bảo tàng nhưng không chứa giờ mở cửa, vì vậy cần từ chối đoán.
- Đăng xuất, cho thấy trang chat biến mất.

## 1:20–3:45: Computational Thinking

**Abstraction:** “Đầu vào là câu hỏi du lịch; đầu ra là câu trả lời cùng nguồn. Mỗi mục giữ ID để trích dẫn, tiêu đề và nội dung để tìm kiếm, URL để đối chiếu. Category và tags phục vụ bài đề xuất địa điểm tiếp theo. Không đưa mọi dữ kiện trên Internet vào hệ thống.”

**Decomposition:** Mở sơ đồ trong README. “Xác thực nhận email và mật khẩu, trả phiên người dùng. Embedding nhận câu hỏi, trả vector. Retrieval nhận vector và chỉ mục, trả ba mục có điểm cao nhất. Context ghép ba mục với câu hỏi. Generation trả câu trả lời hoặc không biết. Display hiển thị lịch sử và nguồn.”

**Pattern recognition:** “Em dùng lại cách tạo giao diện và lưu session của Lab 3, xác thực qua Firebase REST. Từ Lab 4 em dùng Ollama, embedding và RAG. Mẫu filter → score → top-k xuất hiện khi chọn các mục hợp lệ, tính cosine và lấy ba mục tốt nhất. Bài RAG-Rec có thể lọc theo category/tags rồi chấm điểm và chọn địa điểm.”

**Algorithm design:** Mở mã giả. “Em chọn k bằng 3 để cân bằng lượng thông tin và bộ nhớ GPU 4 GB. Ví dụ hỏi người thiết kế Dinh Độc Lập chỉ cần mục G02; ba mục cho phép có thêm ngữ cảnh nhưng vẫn gọn. Nếu ba mục thiếu giờ mở cửa, mô hình phải nói không biết. Kiểm tra ID ngăn trích dẫn mục không được truy xuất, nhưng không tự chứng minh mọi câu trả lời đều đúng.”

## 3:45–4:40: Kiểm thử

- Mở bảng kết quả thật đã được người đọc duyệt.
- Nêu một câu thành công, ID kỳ vọng và ID đã truy xuất.
- Dùng lỗi đã ghi nhận tại `docs/FAILURE_ANALYSIS.md`: T01 truy xuất đúng G02, mô hình trả đúng Ngô Viết Thụ và danh sách ID nhưng thiếu `[G02]` trong văn bản, khiến kiểm tra cũ từ chối đáp án. Mở `citation-before-fix.json`, rồi đối chiếu T01 sau sửa trong `evaluation-real.json`. Nêu cách sửa: thêm trích dẫn từ danh sách ID đã kiểm tra hợp lệ. Không dùng lỗi này làm ví dụ retrieval sai.
- Nếu chưa ghi nhận lỗi RAG thực tế, tiếp tục thử câu hỏi phức tạp và ghi nhận; không tự tạo số liệu hay dùng lỗi mô phỏng như kết quả thật.
- Kết: “Ứng dụng có giới hạn bộ dữ liệu nhỏ, thông tin tĩnh và thời gian xử lý phụ thuộc máy và tunnel.”

Sau khi tải video: bật quyền ai có link cũng xem được, thử trong cửa sổ ẩn danh, điền URL vào README. Nội dung sau 5:00 không được chấm.
