# Test case đợt 3 – Thanh toán QR, ảnh hoạt động lớp

## QR học phí
| ID | Mô tả | Kỳ vọng | Ưu tiên |
|---|---|---|---|
| QR-01 | PH xem QR hóa đơn con mình | Số tiền = còn nợ, nội dung CK có mã hóa đơn duy nhất | P0 |
| QR-02 | PH xem QR hóa đơn bé khác | 403 | P0 |
| QR-03 | Hóa đơn đã trả đủ / đã hủy | Không tạo QR (409/400) | P1 |
| QR-04 | Chưa cấu hình tài khoản thật | Nhãn "Dữ liệu mẫu"; production không cho tạo QR mẫu | P0 |
| QR-05 | PH bấm "Tôi đã chuyển" | Hóa đơn "chờ kế toán xác nhận", KHÔNG tự thành đã trả | P0 |
| QR-06 | Bấm "Tôi đã chuyển" 2 lần | Không tạo trùng | P1 |
| QR-07 | Kế toán xác nhận / từ chối | Trả đủ → phiếu thu; từ chối → PH nhận lý do; lưu `audit_events` | P0 |
| QR-08 | GV / PH gọi xác nhận thanh toán | 403 | P0 |
| QR-09 | Chuyển thiếu / thừa tiền | Thiếu → còn nợ đúng; thừa → tiền dư | P1 |

## Ảnh hoạt động lớp (chờ PM chốt quy tắc)
| ID | Mô tả | Kỳ vọng | Ưu tiên |
|---|---|---|---|
| ALB-01 | Gắn bé chưa đồng ý, gọi thẳng API | Server từ chối | P0 |
| ALB-02 | Gắn thêm bé chưa đồng ý vào ảnh đã đăng | Bị chặn | P0 |
| ALB-03 | PH tắt đồng ý sau khi đã đăng | Mọi ảnh gắn bé tự ẩn khỏi album ngay (PH khác gọi thẳng URL ảnh cũng không xem được), file không bị xóa; GV thấy ảnh ẩn kèm lý do; ghi nhật ký thao tác | P0 |
| ALB-07 | PH bật lại đồng ý | Ảnh cũ KHÔNG tự hiện; cô chỉ hiện lại được khi mọi bé trong ảnh đều đồng ý | P1 |
| ALB-09 | Gỡ tag bé chưa đồng ý để hiện lại ảnh | Theo PM chốt; nếu cho phép phải ghi nhật ký | P0 |
| QR-10 | "Chờ xác nhận" không làm đổi công nợ/báo cáo (`paymentStatus` riêng) | Đúng | P1 |
| ALB-08 | Đăng ảnh gắn bé chưa đồng ý | Lỗi kèm tên bé chưa đồng ý | P1 |
| ALB-04 | PH lớp khác / chưa đăng nhập xem ảnh | 403 / 401 | P0 |
| ALB-05 | Upload file giả ảnh (exe, txt đổi đuôi), HEIC | 400 / chuyển JPEG | P0 |
| ALB-06 | GV đăng vào lớp không phụ trách | 403 | P0 |
| ALB-10 | Đăng 5 ảnh, 1 ảnh có bé chưa đồng ý | 4 ảnh lên đúng 1 lần (không trùng khi cô bấm đăng lại), ảnh lỗi chỉ ra đúng index và tên bé | P1 |
