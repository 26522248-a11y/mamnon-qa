# Test case tuần 1 – Web quản lý trẻ mầm non (API /api/v1)

Vai trò: BGH (admin), GV (giáo viên), KT (kế toán), PH (phụ huynh). Mức ưu tiên: P0 cao nhất.

## 1. Xác thực
| ID | Mô tả | Kỳ vọng | Ưu tiên |
|---|---|---|---|
| AUTH-01 | Login đúng tài khoản | 200, access token, refresh token trong cookie httpOnly | P0 |
| AUTH-02 | Sai mật khẩu | 401, `{code,message}`, không lộ tài khoản có tồn tại hay không | P0 |
| AUTH-03 | Thiếu trường / email sai định dạng | 400 | P1 |
| AUTH-04 | Gọi API không token / token hết hạn / token sửa chữ ký | 401 | P0 |
| AUTH-05 | Refresh bằng cookie hợp lệ | 200, token mới | P0 |
| AUTH-06 | Refresh token cũ sau khi đã dùng (nếu có rotation) | 401 | P1 |
| AUTH-07 | `GET /auth/me` trả đúng vai trò, không trả mật khẩu/hash | 200 | P0 |
| AUTH-08 | Đăng nhập sai nhiều lần liên tiếp | Bị giới hạn (429 hoặc khóa tạm) | P1 |
| AUTH-09 | Tài khoản bị vô hiệu hóa | 401/403 | P1 |

## 2. Phân quyền (P0 toàn bộ)
| ID | Mô tả | Kỳ vọng |
|---|---|---|
| PERM-01 | GV xem `GET /classes/:id` lớp mình | 200 |
| PERM-02 | GV xem/sửa lớp khác, điểm danh lớp khác | 403 |
| PERM-03 | GV `GET /children` chỉ thấy trẻ lớp mình, kể cả khi truyền filter lớp khác | Không lộ trẻ lớp khác |
| PERM-04 | GV xem/sửa `/children/:id` của lớp khác (đoán ID) | 403 |
| PERM-05 | GV tạo/xóa lớp, gán giáo viên | 403 |
| PERM-06 | PH xem con mình | 200 |
| PERM-07 | PH xem trẻ không phải con mình (đổi ID trên URL) | 403 |
| PERM-08 | PH gọi `GET /children` | Chỉ thấy con mình |
| PERM-09 | PH gọi PUT điểm danh, POST lớp, sửa hồ sơ | 403 |
| PERM-10 | KT sửa điểm danh / hồ sơ sức khỏe | 403 (chờ chốt quyền KT) |
| PERM-11 | BGH truy cập mọi lớp | 200 |
| PERM-12 | GV bị gỡ khỏi lớp, token cũ vẫn còn | Mất quyền ngay ở lần gọi sau |

## 3. Lớp học
| ID | Mô tả | Kỳ vọng | Ưu tiên |
|---|---|---|---|
| CLS-01 | Tạo lớp hợp lệ (tên, khối tuổi) | 201 | P0 |
| CLS-02 | Trùng tên lớp trong cùng năm học | 409 | P1 |
| CLS-03 | Sửa lớp, gán GV | 200, GV thấy lớp | P0 |
| CLS-04 | Gán user không phải GV vào lớp | 400 | P1 |
| CLS-05 | Xóa lớp còn trẻ | Bị chặn hoặc yêu cầu chuyển trẻ trước | P0 |
| CLS-06 | ID không tồn tại | 404 | P2 |

## 4. Hồ sơ trẻ
| ID | Mô tả | Kỳ vọng | Ưu tiên |
|---|---|---|---|
| CHD-01 | Tạo trẻ đủ trường bắt buộc | 201 | P0 |
| CHD-02 | Ngày sinh ở tương lai / ngoài độ tuổi mầm non | 400 | P1 |
| CHD-03 | Tìm theo tên có dấu và không dấu ("Nguyễn" / "nguyen") | Ra đúng kết quả | P1 |
| CHD-04 | Phân trang `page`,`limit`, kiểm tra `total` với 300 trẻ | Đúng số, không trùng/sót giữa các trang | P0 |
| CHD-05 | `limit` âm, 0, quá lớn (10000) | 400 hoặc giới hạn tối đa | P1 |
| CHD-06 | Upload ảnh jpg/png hợp lệ | 200 | P1 |
| CHD-07 | Upload file không phải ảnh / quá dung lượng / đổi đuôi .exe→.jpg | 400 | P0 |
| CHD-08 | Thêm người giám hộ, nhiều người cho một trẻ | 201 | P0 |
| CHD-09 | Dị ứng, ghi chú sức khỏe lưu và hiển thị đúng | 200 | P0 |
| CHD-10 | Xóa trẻ: xóa mềm, lịch sử điểm danh vẫn còn | 200 | P1 |
| CHD-11 | Ký tự đặc biệt / HTML trong tên (XSS) | Lưu an toàn, không chạy script | P0 |

## 5. Điểm danh và đón trẻ
| ID | Mô tả | Kỳ vọng | Ưu tiên |
|---|---|---|---|
| ATT-01 | Lấy điểm danh lớp theo ngày chưa có dữ liệu | Danh sách trẻ, trạng thái trống | P0 |
| ATT-02 | `PUT` lưu cả lớp (có mặt/vắng/muộn) | 200, đọc lại đúng | P0 |
| ATT-03 | Lưu lại lần 2 cùng ngày | Ghi đè, không tạo bản trùng | P0 |
| ATT-04 | Payload chứa trẻ không thuộc lớp | 400 | P0 |
| ATT-05 | Ngày tương lai | 400 | P1 |
| ATT-06 | Sửa điểm danh ngày cũ (quá X ngày) | Theo quy định, chờ PM chốt | P1 |
| ATT-07 | Ngày theo múi giờ VN (điểm danh 23h, 0h30) | Đúng ngày theo UTC+7 | P0 |
| ATT-08 | Ghi đón trẻ bởi người giám hộ đã đăng ký | 201, lưu giờ đón | P0 |
| ATT-09 | Ghi đón bởi người không có trong danh sách | Bị chặn hoặc cảnh báo + ghi chú bắt buộc | P0 |
| ATT-10 | Ghi đón trẻ đang vắng hôm đó | 400 | P1 |
| ATT-11 | Ghi đón 2 lần cho cùng một lượt | 409 | P1 |
| ATT-12 | Hai GV cùng lưu điểm danh một lớp cùng lúc | Không mất dữ liệu | P1 |
| ATT-13 | Giao diện mobile: chạm một lần đổi trạng thái, lưu 30 trẻ < 2 giây | Đạt | P1 |

## 6. Chung
- Mọi lỗi đúng định dạng `{code, message}`, không lộ stack trace.
- Hiệu năng: `GET /children` 300 trẻ < 500 ms.
- Swagger khớp với hành vi thật.

## Câu hỏi cần PM chốt
1. Kế toán có được xem hồ sơ trẻ/điểm danh không?
2. Giáo viên được sửa điểm danh lùi bao nhiêu ngày?
3. Người đón không có trong danh sách: chặn hẳn hay cho phép kèm ghi chú?
