# Checklist thử thông báo đón bé trên điện thoại thật (5 bước)

Chuẩn bị: 1 điện thoại phụ huynh (iPhone iOS 16.4+ hoặc Android Chrome), 1 tài khoản phụ huynh có con, 1 cô giáo ở lớp bé, 1 người Ban giám hiệu.

1. **Cài web lên màn hình chính.** iPhone: mở web bằng Safari → nút Chia sẻ → "Thêm vào Màn hình chính" → mở app từ biểu tượng mới. Android: Chrome → menu ⋮ → "Cài đặt ứng dụng". Đăng nhập tài khoản phụ huynh.
2. **Cho phép thông báo.** Khi app hỏi, bấm "Cho phép". Kiểm tra: trang "Bé hôm nay" không còn dòng vàng "Bạn đã chặn thông báo".
3. **Tắt màn hình, cô giáo tạo yêu cầu.** Phụ huynh khóa máy. Cô giáo bấm "+ Người khác đến đón" cho bé, nhập tên và chụp ảnh người đón. Ghi lại: thông báo đến sau bao nhiêu giây, có hiện ảnh không.
4. **Bấm ngay trên thông báo.** Bấm "Đúng, cho đón" (hoặc "Từ chối") trên thông báo. Kiểm tra trên máy cô giáo: dấu tích phụ huynh hiện ra, nút "Giao bé" VẪN KHÓA cho đến khi Ban giám hiệu duyệt. Ban giám hiệu duyệt xong thì nút mới mở.
5. **Thử không trả lời.** Tạo yêu cầu thứ hai, phụ huynh không bấm gì. Sau 15 phút, màn cô giáo phải hiện nút gọi số ① rồi ②, và bé tuyệt đối không được tự giao.

Ghi kết quả: loại máy, phiên bản iOS/Android, thời gian nhận thông báo, có ảnh không, bước nào sai (kèm ảnh chụp màn hình).

## Ảnh trên điện thoại thật (B32/B31/B27, thêm 10/10) – khoảng 5 phút, làm cùng buổi G8 sáng thứ Hai
Máy QA chỉ chạy được Chrome giả lập khổ iPhone, không có Safari/WebKit thật, nên các bước này cần người cầm máy:
1. iPhone (Safari): giáo viên vào Giao bé, bấm "📷 Chụp ảnh" bằng camera thật → ảnh hiện đúng chiều, gửi được, phụ huynh thấy ảnh.
2. iPhone: chọn 1 ảnh HEIC từ thư viện cho ảnh người đón và ảnh lớp → gửi được, ảnh hiện đúng chiều.
3. Android (Chrome): chụp ảnh 6–8 MB (chế độ chất lượng cao) cho ảnh lớp → gửi được trong vài giây trên 4G.
4. Chứng từ thu chi: chụp hoá đơn bằng điện thoại → tải về vẫn đọc rõ chữ nhỏ.
5. Sau 1 lần deploy lại backend, mở lại các ảnh trên → vẫn còn (B27, lưu trên Backblaze B2).
