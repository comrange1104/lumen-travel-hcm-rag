# Tạo Firebase cho người mới

Chỉ cần Firebase Authentication. Không tạo Firestore hay tải khóa service account.

1. Mở https://console.firebase.google.com/ và đăng nhập Google.
2. Chọn **Create a project / Tạo dự án**, đặt tên `lumen-travel-thien`. Nếu có lựa chọn Google Analytics, tắt vì bài này không dùng. Hoàn tất tạo project.
3. Trong project, vào **Build → Authentication → Get started**.
4. Mở **Sign-in method → Email/Password**, bật mục **Email/Password**, bấm **Save**. Không cần bật Email link hay Google login.
5. Về **Project overview**, chọn biểu tượng **Web `</>` / Add app**, đặt tên `lumen-streamlit`. Không bật Firebase Hosting. Bấm đăng ký ứng dụng.
6. Ở phần cấu hình Web, tìm `apiKey` và `projectId`. Sau này có thể xem lại tại biểu tượng bánh răng → **Project settings → General → Your apps → SDK setup and configuration → Config**.
7. Tại thư mục dự án, mở PowerShell và chạy:

```powershell
if (-not (Test-Path -LiteralPath .env)) { Copy-Item .env.example .env }
notepad .env
```

Điền các giá trị thật của project, không dùng ví dụ này nguyên xi:

```dotenv
FIREBASE_API_KEY=gia_tri_apiKey_tu_firebase
FIREBASE_PROJECT_ID=gia_tri_projectId_tu_firebase
OLLAMA_BASE_URL=https://URL-HTTPS-duoc-Pinggy-cap
OLLAMA_NUM_GPU=0
```

Giữ nguyên URL Ollama đã điền sẵn nếu tunnel hiện tại còn chạy. `OLLAMA_NUM_GPU=0` là chế độ CPU đã dùng để kiểm tra trên máy này.

8. Lưu tệp. Nếu Streamlit đang chạy, dừng bằng Ctrl+C và chạy lại. Nếu app chạy ẩn, mở terminal riêng và chạy `streamlit run app.py --server.port 8502` từ môi trường ảo để dùng cấu hình mới.
9. Trên ứng dụng chọn **Đăng ký**, dùng email và mật khẩu thử nghiệm ít nhất 6 ký tự. Đợi báo thành công, chọn **Đăng nhập** rồi nhập lại.
10. Trong Firebase → Authentication → Users sẽ thấy tài khoản vừa đăng ký.

Mật khẩu app thử nghiệm do bạn đặt, không phải mật khẩu tài khoản Google. Không đưa mật khẩu hay token vào README/video. Git đã được cấu hình bỏ qua `.env`.

Nếu Firebase báo yêu cầu chấp nhận điều khoản hoặc chọn vùng cho Authentication, hoàn tất trong Console theo thông tin tài khoản của bạn. Tên menu có thể thay đổi; chức năng cần bật vẫn là Email/Password.

Nguồn: https://firebase.google.com/docs/auth/web/start và https://firebase.google.com/docs/reference/rest/auth
