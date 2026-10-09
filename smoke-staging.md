# Smoke test bản chạy thử

**Tự động:** `smoke_staging.py`, xem cách chạy ở đầu file. Mất khoảng 2 phút và chỉ ghi đúng 1 tin "SMOKE hẹn giờ", gửi cho nhân viên.

**Thủ công trên điện thoại thật (Safari iPhone và Chrome Android), khoảng 15 phút:**
1. Đăng nhập: cả 4 vai trò đăng nhập được. Tải lại trang vẫn giữ đăng nhập. Tài khoản mới tạo bị buộc đổi mật khẩu.
2. Điểm danh: giáo viên điểm danh 1 bé rồi lưu, phụ huynh thấy "Bé đã đến lớp".
3. Đón bé: giáo viên tạo yêu cầu cho người ngoài danh sách. Nút giao bị khóa cho tới khi phụ huynh xác nhận và BGH duyệt, sau đó giao được.
4. Học phí: ở trang `/fees`, khổ 390px hiện dạng thẻ. Ghi thu được và in biên lai có tên trường thật.
5. Thông báo: BGH hẹn giờ một tin kèm 2 ảnh. Phụ huynh không thấy tin trước giờ gửi, tới giờ thì thấy, ảnh đúng thứ tự. Chọn giờ đã qua thì nút bị khóa.
6. Chấm công: giáo viên bấm Vào ca rồi Ra ca. BGH thấy trên bảng tuần.
7. Thu chi: kế toán ghi khoản chi trên 10 triệu, khoản này chờ duyệt và chưa cộng vào tổng chi. BGH duyệt xong mới cộng. Giáo viên mở `/finance` bị chặn.
8. Ảnh và hóa đơn đính kèm vẫn mở được sau khi redeploy, để kiểm tra R2 đã lưu ảnh thật.
9. Cron: tin hẹn giờ vẫn được gửi sau khi backend Render đã ngủ hơn 15 phút.

Sau khi test xong, xóa các tin và khoản có chữ "SMOKE".
