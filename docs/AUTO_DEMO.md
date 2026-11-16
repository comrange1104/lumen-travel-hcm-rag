# Quay video với demo tự chạy

## Cách mở

1. Bấm đúp `QUAY_DEMO.bat` tại thư mục dự án. Giữ cửa sổ terminal mở khi quay.
2. Launcher kiểm tra cấu hình, khởi động Ollama nếu cần, gia hạn tunnel Pinggy nếu đường cũ hết hiệu lực và mở trang http://localhost:8503.
3. Đăng nhập bằng tài khoản Firebase đã đăng ký. Đây là bước xác thực thật; ứng dụng không lưu mật khẩu để tự đăng nhập.
4. Bấm **1. Chuẩn bị cẩm nang**, đợi báo sẵn sàng. Bước này tạo/lấy chỉ mục thật trước khi quay.
5. Chọn có/không **Hiện nội dung thuyết trình**. Bấm **2. Bắt đầu**, rồi bấm quay màn hình trong 8 giây đếm ngược.
6. Từ đây không cần nhập câu hỏi hay chuyển cảnh. Chữ lớn được căn giữa và tự chuyển từng cụm theo thời gian đọc. Khi màn hình kết thúc hiện **Hoàn tất**, dừng quay.
7. Tải `lumen-demo.srt` và `lumen-timeline.json` ở cuối trang để ghép phụ đề/giọng đọc sau đó. Mốc 0 của phụ đề là lúc phần giới thiệu bắt đầu, sau đếm ngược; cắt phần đếm ngược của clip để khớp.

Để có thao tác đăng nhập trong bài nộp, quay thêm đoạn đăng nhập thật từ bước 3. Có thể quay liên tục rồi cắt phần chuẩn bị/đếm ngược, hoặc ghép đoạn đăng nhập trước phần tự trình diễn. Màn hình “Firebase Authentication” trong phần tự chạy chỉ xác nhận phiên đã đăng nhập, không giả lập thao tác nhập mật khẩu.

## Demo làm gì?

- Gửi thật “Dinh Độc Lập do ai thiết kế?” bằng cùng pipeline `rag.answer_question` của ứng dụng chính.
- Trình bày abstraction và decomposition trong lúc chờ mô hình, rồi hiện câu trả lời cùng ba mục nguồn khi có phản hồi.
- Gửi thật câu giá vé TP.HCM–Tokyo; trình bày pattern recognition và algorithm design trong lúc chờ, rồi hiện kết quả thiếu dữ kiện.
- Tự đăng xuất, xóa phiên và các kết quả hội thoại của phần demo.
- Hiện báo cáo kiểm thử **đã lưu ngày 16/11/2026**, có ghi nhãn, gồm T01 thành công và E01 giới hạn top-3. Không gọi phần báo cáo này là kết quả vừa chạy.

## Thời gian và lời thoại

Lịch cơ sở là khoảng **4 phút 26 giây**, chưa tính 8 giây đếm ngược và thời gian chờ thêm nếu mô hình chậm. Không bảo đảm mọi lần chạy đều dưới 5 phút. Trình diễn chỉ hiển thị đáp án khi có phản hồi thật, và luôn để thời gian đọc sau khi phản hồi xuất hiện.

Thứ tự các đoạn phân tích khác kịch bản quay thủ công trong `VIDEO_SCRIPT.md` để tận dụng thời gian chờ. Dùng SRT/timeline xuất cuối trang để ghép lời cho chế độ tự chạy; không lấy nguyên timestamp cũ 4:40.

Nếu thời lượng vượt 5 phút, rút ngắn đoạn chờ trong phần mềm dựng và hiện chú thích **“Đã rút ngắn thời gian chờ xử lý”**. Phải căn lại phụ đề nếu cắt tiếp clip sau khi đã xuất SRT. Giữ nguyên câu hỏi, kết quả và nguồn thực tế.

## Khi có lỗi

- Mất mạng, Ollama/Pinggy lỗi hoặc câu trả lời chưa đạt kỳ vọng: demo dừng và hiện thông báo; không thay kết quả bằng đáp án mẫu.
- Di chuột xuống góc phải dưới, mở menu **⋯** để bật/tắt nội dung chữ hoặc chọn **Dừng / chuẩn bị quay lại**. Bộ đếm, thanh tiến trình, nhãn điều khiển và nhãn “Lời thuyết minh” không xuất hiện trong phần đang quay. Một HTTP request đã chạy có thể cần đợi hoàn tất trước khi quay lại.
- Mở lại `QUAY_DEMO.bat` để kiểm tra các dịch vụ. Nếu có thay đổi cấu hình Firebase, khởi động lại trang demo để nạp cấu hình mới.
- Phiên đăng xuất ở cuối demo là phiên của trang 8503; một phiên độc lập ở trang 8501 không bị đăng xuất theo.

Mật khẩu và token Firebase không được đưa vào SRT/timeline hay repository. Chế độ này chưa tự tạo giọng đọc hoặc tự ghi màn hình; bạn chỉ cần thao tác quay/dừng quay bằng công cụ ghi hình mình sử dụng sau khi thiết lập.

## Xác minh triển khai

Ngày 16/11/2026: 21/21 kiểm thử tự động đạt, gồm kiểm tra render đủ 13 cảnh, gửi mỗi câu đúng một lần, chờ kết quả, dừng khi đáp án không đạt, xóa dữ liệu hội thoại khi đăng xuất và xuất SRT. Một lần gọi RAG qua tác vụ nền thật trả đúng Ngô Viết Thụ [G02] trong 28,14 giây, chưa tính chuẩn bị chỉ mục. Giao diện đăng nhập đã được mở và kiểm tra; một phiên quay trọn vẹn bằng tài khoản Firebase của sinh viên vẫn cần thực hiện sau khi đăng nhập.
