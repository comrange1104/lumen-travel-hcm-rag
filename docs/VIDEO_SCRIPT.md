# Kịch bản video Lumen Travel — 4 phút 40 giây

**Trần Hải Thiên — MSSV 25127007 — Assignment 03, Computational Thinking.**

Các mốc là mục tiêu dựng video. Tập đọc một lần để điều chỉnh tốc độ; phần sau 5:00 không được chấm.

## Chuẩn bị trước khi quay

- Giữ Streamlit, Ollama và Pinggy hoạt động. Kiểm tra trang không còn chữ CONNECTING.
- Chạy thử một câu để tạo cache và kiểm tra kết nối, sau đó đăng xuất để bắt đầu với lịch sử trống.
- Mở ứng dụng và tài liệu [Hình và bảng trình bày](VIDEO_VISUALS.md) ở chế độ xem Markdown đã render, chẳng hạn trên GitHub.
- Chuẩn bị tài khoản thử nghiệm và hai câu demo bên dưới. Quay ứng dụng và tài liệu, tránh quay `.env` hay mật khẩu trong terminal.
- Rút ngắn đoạn chờ mô hình khi dựng và chèn chú thích **“Đã rút ngắn thời gian chờ xử lý”**. Giữ nguyên câu hỏi và kết quả thật. Lần đo CPU đã lưu mất khoảng 31–79 giây/câu, chưa tính tạo chỉ mục.

## 0:00–0:12 — Giới thiệu

**Màn hình:** Tiêu đề Lumen Travel và form đăng nhập; thêm tên, MSSV trong video nếu cần.

**Lời thoại:**

> Em là Trần Hải Thiên, mã số sinh viên 25127007. Em xin trình bày Lumen Travel, trợ lý du lịch Thành phố Hồ Chí Minh có đăng nhập và trả lời dựa trên cẩm nang.

## 0:12–0:25 — Đăng nhập

**Thao tác:** Chọn Đăng nhập, nhập tài khoản thử nghiệm, bấm Tiếp tục; cho thấy ô chat xuất hiện.

**Lời thoại:**

> Trang chat chỉ xuất hiện sau khi đăng nhập bằng Firebase Authentication. Em dùng tài khoản thử nghiệm để truy cập ứng dụng.

## 0:25–0:50 — Câu hỏi có đáp án

**Thao tác:** Gửi câu sau, rút đoạn chờ khi dựng, mở bảng nguồn và chỉ vào G02 cùng điểm cosine.

```text
Dinh Độc Lập do ai thiết kế?
```

**Kỳ vọng:** Ngô Viết Thụ, trích dẫn `[G02]`. Kiểm tra kết quả thật trước khi quay bản chính thức.

**Lời thoại:**

> Em hỏi người thiết kế Dinh Độc Lập. Trợ lý trả lời Ngô Viết Thụ và trích dẫn G02. Bảng mở rộng hiển thị ba mục được truy xuất, nội dung, nguồn tham khảo và điểm tương đồng cosine.

## 0:50–1:10 — Câu hỏi ngoài dữ liệu

**Thao tác:** Gửi câu dưới đây, cho thấy câu trả lời không có thông tin. Có thể mở G13 để chỉ ra mục đó chỉ nói về di chuyển từ sân bay.

```text
Giá vé máy bay từ TP.HCM đi Tokyo ngày mai là bao nhiêu?
```

**Lời thoại:**

> Cẩm nang không có giá vé chuyến bay này, nên trợ lý nói không có thông tin. Dù vẫn tìm được ba mục gần nghĩa nhất, hệ thống không được dùng chúng để tự đoán giá vé.

**Lưu ý:** Đây là test ĐẠT về xử lý thiếu dữ liệu, không phải ví dụ lỗi ở cuối video.

## 1:10–1:20 — Đăng xuất

**Thao tác:** Bấm Đăng xuất; cho thấy trang quay về form đăng nhập.

**Lời thoại:**

> Khi đăng xuất, ứng dụng xóa lịch sử trong session và quay về trang đăng nhập. Lịch sử không được lưu vào cơ sở dữ liệu.

## 1:20–1:50 — Abstraction: trừu tượng hóa

**Màn hình:** Phần Abstraction trong VIDEO_VISUALS; chỉ vào bảng trường dữ liệu.

**Lời thoại:**

> Đầu vào là câu hỏi du lịch; đầu ra là câu trả lời hoặc thông báo thiếu thông tin, kèm các mục được truy xuất. Em giới hạn dữ liệu ở 16 mục về Thành phố Hồ Chí Minh. Mỗi mục giữ ID để trích dẫn, tiêu đề và nội dung để tìm kiếm, nguồn để đối chiếu. Các địa điểm có thêm category và tags, chuẩn bị cho bài gợi ý địa điểm tiếp theo.

## 1:50–2:25 — Decomposition: chia nhỏ bài toán

**Màn hình:** Sơ đồ Decomposition; trỏ lần lượt các khối, mỗi khối ghi đầu vào và đầu ra.

**Lời thoại:**

> Em chia hệ thống thành sáu bước. Đăng nhập nhận email, mật khẩu và trả phiên người dùng. Embedding nhận câu hỏi, trả vector. Truy xuất so sánh vector câu hỏi với các vector cẩm nang, trả ba mục cùng điểm số. Ghép context biến câu hỏi và ba mục thành đầu vào cho mô hình. Mô hình sinh câu trả lời. Cuối cùng, ứng dụng kiểm tra trích dẫn rồi hiển thị đáp án, nguồn và lịch sử. Vector cẩm nang được tạo một lần và cache để tái sử dụng.

## 2:25–3:00 — Pattern recognition: nhận diện mẫu

**Màn hình:** Phần Pattern recognition, các thành phần tái sử dụng từ Lab 3–4 và mẫu filter → score → top-k.

**Lời thoại:**

> Từ Lab 3, em tái sử dụng Streamlit, session state và xác thực Firebase. Từ Lab 4, em sử dụng Ollama qua Pinggy, embedding và RAG. Em nhận ra mẫu lọc ứng viên, chấm điểm rồi chọn top-k. Hiện tại, sau khi kiểm tra dữ liệu hợp lệ, hệ thống chấm cosine cho toàn bộ cẩm nang rồi chọn ba mục. Sang bài RAG-Rec, em có thể thêm lọc category hoặc tags theo sở thích trước khi chấm điểm và chọn địa điểm.

**Ghi chú:** Bản hiện tại chưa lọc theo sở thích. Kiểm tra định dạng JSON là kiểm tra dữ liệu, không phải bộ lọc category/tags đã triển khai.

## 3:00–3:45 — Algorithm design: thiết kế thuật toán

**Màn hình:** Mã giả trong VIDEO_VISUALS; chỉ vào embedding, top-3, trả lời không biết và kiểm tra ID.

**Lời thoại:**

> Với mỗi câu hỏi, thuật toán kiểm tra đăng nhập và nội dung rỗng, sau đó lấy chỉ mục đã cache. Câu hỏi được embedding bằng embeddinggemma. Hệ thống tính cosine, chọn ba mục tốt nhất, ghép context rồi gọi qwen3:4b. Mô hình chỉ được dùng dữ kiện trong context. Nếu thiếu dữ kiện thì trả lời không biết; ID trích dẫn phải thuộc các mục đã truy xuất. Em chọn k bằng ba để context gọn và giảm nhu cầu bộ nhớ. Ví dụ, câu hỏi người thiết kế Dinh Độc Lập cần mục G02. Tuy nhiên, ba mục có thể chưa đủ cho câu hỏi tổng hợp nhiều địa điểm.

## 3:45–4:30 — Kiểm thử: một thành công và một thất bại

**Màn hình:** Bảng T01 và E01 trong VIDEO_VISUALS. Đây là kết quả chạy thật đã lưu; không cần chạy lại E01 trong lúc quay. Có link tới JSON gốc để đối chiếu.

**Lời thoại:**

> Bộ sáu câu hỏi chính đã đạt trong lần kiểm thử được lưu. Ví dụ T01 kỳ vọng G02; hệ thống truy xuất đúng G02 và trả lời Ngô Viết Thụ. Với test mở rộng E01, câu hỏi yêu cầu bốn bảo tàng. Cẩm nang có đủ G03, G08, G09 và G10, nhưng top ba chỉ lấy G03, G09 và G10, thiếu G08. Trợ lý vì vậy trả lời không có thông tin. Đây là giới hạn ở bước retrieval: context chưa đủ để trả lời toàn bộ câu hỏi. Em ghi nhận hạn chế này trong README.

**Giải thích dự phòng, không cần đọc nếu sắp hết giờ:** Giá vé không có trong cẩm nang; bốn bảo tàng có trong cẩm nang nhưng không được truy xuất đầy đủ. Có thể cải thiện bằng tăng k hoặc truy xuất thích ứng; bản hiện tại chưa triển khai hướng này.

## 4:30–4:40 — Hạn chế và kết thúc

**Màn hình:** Hạn chế, khai báo công cụ AI và tên repository.

**Lời thoại:**

> Ứng dụng dùng dữ liệu tĩnh và còn chậm trên CPU. Em công bố hạn chế và việc dùng Codex hỗ trợ trong README. Em xin cảm ơn.

## Sau khi quay

- Kiểm tra video thực tế dưới 5 phút; mục tiêu 4:40 chừa khoảng đệm 20 giây.
- Đủ đăng nhập, câu có đáp án và nguồn, câu ngoài dữ liệu, đăng xuất, bốn bước Computational Thinking, một test thành công và một thất bại có chỉ rõ bước gây lỗi.
- Nếu kết quả thực tế khác báo cáo, điều chỉnh lời thoại theo kết quả quan sát.
- Tải video lên YouTube hoặc Google Drive, bật quyền xem qua link, thử bằng cửa sổ ẩn danh rồi thêm link vào README.
- Sinh viên cần đọc hiểu và kiểm tra nội dung trước khi sử dụng kịch bản.
