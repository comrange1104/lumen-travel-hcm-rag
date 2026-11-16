# Lỗi thực tế và cách xử lý

Ghi nhận ngày 16/11/2026 trên Windows, RAM khoảng 8 GB, GTX 1650 4 GB, Ollama 0.40.16. Không dùng các lỗi mô phỏng của unit test để thay thế kết quả này.

## 1. HTTP 403 khi gọi qua Pinggy

Server trực tiếp trả HTTP 200 ở `/api/tags`, nhưng URL Pinggy trả HTTP 403. Ollama kiểm tra Host header của request. Đã sửa lệnh tạo tunnel bằng `u:Host:localhost:11434` theo https://pinggy.io/quickstart/ollama-api/. Sau sửa, cùng endpoint qua Pinggy trả HTTP 200 và liệt kê đúng hai mô hình.

## 2. Khởi tạo CUDA thất bại

Trong server log xuất hiện `CUDA error: shared object initialization failed` khi khởi tạo runner cho qwen3:4b. Máy có ít RAM trống và GPU 4 GB; chưa xác định đây là lỗi thư viện, driver hay tài nguyên. Không kết luận đơn thuần rằng 4 GB không chạy được mô hình.

Đã thêm cấu hình `OLLAMA_NUM_GPU=0` và chạy kiểm thử bằng CPU để giảm phụ thuộc CUDA. Hạn chế còn lại là độ trễ cao. Mô hình vẫn là qwen3:4b đúng yêu cầu.

## 3. Từ chối nhầm câu trả lời vì thiếu trích dẫn trong văn bản

- Câu hỏi: “Dinh Độc Lập do ai thiết kế?”
- Retrieval trả G02, G10, G06: chứa đúng mục kỳ vọng G02.
- Đầu ra JSON thật: `answerable=true`, `answer="Dinh Độc Lập do kiến trúc sư Ngô Viết Thụ thiết kế"`, `citations=["G02"]`.
- Bộ kiểm tra cũ yêu cầu văn bản phải có `[G02]`, vì vậy trả câu không biết dù đáp án và danh sách ID đúng.
- Phân loại: bước xử lý kết quả generation/định dạng trích dẫn; không phải retrieval hay thiếu dữ liệu.
- Sửa: kiểm tra mọi ID thuộc các mục được truy xuất, sau đó tự thêm trích dẫn từ danh sách hợp lệ khi văn bản thiếu dấu trích dẫn. ID ngoài context vẫn bị từ chối. Có kiểm thử hồi quy cho trường hợp này.

Bằng chứng: [đầu ra mô hình trước khi sửa](citation-before-fix.json). Lần chẩn đoán CPU mất 44,74 giây cho T01. Kết quả cuối cùng nằm trong `evaluation-real.json` sau khi chạy lại; cần đối chiếu nội dung trước khi nộp.

## 4. Câu hỏi cần nhiều mục hơn top-3

`exploratory_cases.json` hỏi bốn bảo tàng, kỳ vọng G03, G08, G09, G10. Lần chạy thật lấy G03, G09, G10, thiếu G08; mô hình trả câu không biết, mất 79,67 giây. Phân loại giới hạn **retrieval** vì top-3 không chứa đủ bốn mục. Đây là bài kiểm tra giới hạn thiết kế, không nằm trong sáu test bắt buộc. Kết quả thật được lưu cùng lần đánh giá cuối. Bài hiện tại giữ k=3 và công bố hạn chế, chưa triển khai truy xuất thích ứng.
