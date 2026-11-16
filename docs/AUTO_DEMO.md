# Quay video với demo tự chạy

## Cách mở

1. Bấm đúp `QUAY_DEMO.bat` tại thư mục dự án. Giữ cửa sổ terminal mở khi quay.
2. Launcher kiểm tra cấu hình, khởi động Ollama nếu cần, mở lại tunnel Pinggy nếu đường cũ hết hiệu lực và mở trang http://localhost:8503. Trang kiểm tra lại kết nối khi chuẩn bị và ngay trước đếm ngược.
3. Đăng nhập bằng tài khoản Firebase đã đăng ký. Đây là bước xác thực thật; ứng dụng không lưu mật khẩu để tự đăng nhập.
4. Bấm **1. Chuẩn bị cẩm nang**, đợi báo sẵn sàng. Bước này tạo/lấy chỉ mục thật trước khi quay.
5. Chọn có/không **Hiện nội dung thuyết trình**. Bấm **2. Bắt đầu**, rồi bấm quay màn hình trong 8 giây đếm ngược.
6. Từ đây không cần nhập câu hỏi hay chuyển cảnh. Chữ lớn được căn giữa và tự chuyển từng cụm theo thời gian đọc. Khi màn hình kết thúc hiện **Hoàn tất**, dừng quay.
7. Tải `lumen-demo.srt` và `lumen-timeline.json` ở cuối trang để ghép phụ đề/giọng đọc sau đó. Mốc 0 của phụ đề là lúc phần giới thiệu bắt đầu, sau đếm ngược; cắt phần đếm ngược của clip để khớp.

Để có thao tác đăng nhập trong bài nộp, quay thêm đoạn đăng nhập thật từ bước 3. Có thể quay liên tục rồi cắt phần chuẩn bị/đếm ngược, hoặc ghép đoạn đăng nhập trước phần tự trình diễn. Màn hình “Firebase Authentication” trong phần tự chạy chỉ xác nhận phiên đã đăng nhập, không giả lập thao tác nhập mật khẩu.

## Demo làm gì?

- Gửi thật “Dinh Độc Lập do ai thiết kế?” bằng cùng pipeline `rag.answer_question` của ứng dụng chính.
- Chờ kết quả câu thứ nhất rồi hiện đáp án, nguồn được trích dẫn và ba mục truy xuất với điểm số. Chi tiết đầy đủ nằm trong bảng mở rộng.
- Gửi thật câu giá vé TP.HCM–Tokyo, chờ kết quả rồi hiện phản hồi thiếu dữ kiện.
- Tự đăng xuất, xóa phiên và các kết quả hội thoại của phần demo.
- Sau phần hỏi–đáp, trình bày lần lượt Abstraction → Decomposition → Pattern recognition → Algorithm design. Mỗi cảnh chỉ có một nhóm nội dung; lời thoại dài được giữ trong SRT, không chèn đè lên sơ đồ và bảng.
- Hiện báo cáo kiểm thử **đã lưu ngày 16/11/2026**, có ghi nhãn, gồm T01 thành công và E01 giới hạn top-3. Không gọi phần báo cáo này là kết quả vừa chạy.

## Thời gian và lời thoại

Thời gian các cảnh là **3 phút 48 giây**, cộng thời gian chờ mô hình và 8 giây đếm ngược. Lần kiểm tra sau sửa, hai câu hỏi mất khoảng 30 và 26 giây; video thường có thể ở gần giới hạn 5 phút. Không bảo đảm mọi lần chạy đều dưới 5 phút. Trình diễn chỉ hiển thị đáp án khi có phản hồi thật, và luôn để thời gian đọc sau khi phản hồi xuất hiện.

Trình tự: giới thiệu → xác thực → câu hỏi có đáp án và nguồn → câu ngoài dữ liệu → đăng xuất → bốn phần phân tích → kiểm thử → kết thúc. Dùng SRT/timeline xuất cuối trang để ghép lời cho chế độ tự chạy; không lấy nguyên timestamp cũ 4:40.

Nếu thời lượng vượt 5 phút, rút ngắn đoạn chờ trong phần mềm dựng và hiện chú thích **“Đã rút ngắn thời gian chờ xử lý”**. Phải căn lại phụ đề nếu cắt tiếp clip sau khi đã xuất SRT. Giữ nguyên câu hỏi, kết quả và nguồn thực tế.

## Khi có lỗi

- Nếu Pinggy ngắt, client thử khôi phục tunnel và gửi lại đúng request một lần. URL mới được cập nhật trong `.env`; không chuyển sang gọi localhost thay cho Pinggy.
- Nếu vẫn lỗi, demo dừng và hiện nguyên nhân an toàn thay vì chỉ hiện thông báo chung. Nút **Thử lại câu hỏi** gửi lại tác vụ đã kết thúc; không tạo bản sao của tác vụ còn chạy. Request quá thời gian xử lý không tự lặp lại vì có thể vẫn đang dùng CPU.
- Câu trả lời chưa đạt kỳ vọng vẫn được giữ để đối chiếu, không bị thay bằng đáp án mẫu.
- Di chuột xuống góc phải dưới, mở menu **⋯** để bật/tắt nội dung chữ hoặc chọn **Dừng / chuẩn bị quay lại**. Bộ đếm, thanh tiến trình, nhãn điều khiển và nhãn “Lời thuyết minh” không xuất hiện trong phần đang quay. Một HTTP request đã chạy có thể cần đợi hoàn tất trước khi quay lại.
- Mở lại `QUAY_DEMO.bat` để kiểm tra các dịch vụ. Nếu có thay đổi cấu hình Firebase, khởi động lại trang demo để nạp cấu hình mới.
- Phiên đăng xuất ở cuối demo là phiên của trang 8503; một phiên độc lập ở trang 8501 không bị đăng xuất theo.

Mật khẩu và token Firebase không được đưa vào SRT/timeline hay repository. Chế độ này chưa tự tạo giọng đọc hoặc tự ghi màn hình; bạn chỉ cần thao tác quay/dừng quay bằng công cụ ghi hình mình sử dụng sau khi thiết lập.

## Xác minh triển khai

Ngày 16/11/2026: 21/21 kiểm thử tự động đạt, gồm kiểm tra render đủ 13 cảnh, gửi mỗi câu đúng một lần, chờ kết quả, dừng khi đáp án không đạt, xóa dữ liệu hội thoại khi đăng xuất và xuất SRT. Một lần gọi RAG qua tác vụ nền thật trả đúng Ngô Viết Thụ [G02] trong 28,14 giây, chưa tính chuẩn bị chỉ mục. Giao diện đăng nhập đã được mở và kiểm tra; một phiên quay trọn vẹn bằng tài khoản Firebase của sinh viên vẫn cần thực hiện sau khi đăng nhập.

Bản sửa kết nối ngày 16/11/2026: **29/29 kiểm thử đạt**. Đã xác nhận localhost Ollama HTTP 200 trong khi tunnel cũ ngắt, sau đó client tự mở tunnel mới và chạy thành công cả hai câu: G02/Ngô Viết Thụ (30,02 giây) và từ chối đoán giá vé (25,82 giây). Có kiểm thử cho tunnel hết hiệu lực, tái sử dụng URL đã khôi phục, giới hạn số lần gửi lại, không lặp request đọc quá thời gian, giữ thông báo lỗi và tiếp tục sau lỗi.
