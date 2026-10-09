# Test case đợt 2 – Lời nhắn phụ huynh, dặn thuốc, điểm danh, nhật ký

Mốc báo nghỉ lấy từ cấu hình (mặc định 08:00, giờ VN). Hoàn tiền ăn chỉ khi báo trước mốc.

## A. Báo nghỉ và mốc 8:00
| ID | Mô tả | Kỳ vọng | Ưu tiên |
|---|---|---|---|
| ABS-01 | Báo nghỉ hôm nay lúc 07:59:59 | Vắng có phép + được hoàn tiền ăn | P0 |
| ABS-02 | Báo đúng 08:00:00 | Không hoàn (mốc là "trước 8:00"), vẫn Vắng có phép | P0 |
| ABS-03 | Báo 08:00:01 / 10:00 | Vắng có phép, không hoàn | P0 |
| ABS-04 | Báo từ tối hôm trước cho ngày mai | Hoàn | P0 |
| ABS-05 | Báo nghỉ nhiều ngày (T2–T6) lúc 09:00 thứ Hai | Thứ Hai không hoàn, T3–T6 hoàn | P0 |
| ABS-06 | Khoảng nghỉ có thứ Bảy, Chủ nhật | Không tính hoàn cuối tuần/ngày lễ | P1 |
| ABS-07 | Giờ server UTC: báo 07:30 giờ VN (00:30 UTC) | Vẫn tính trước 8:00 giờ VN | P0 |
| ABS-08 | Đổi cấu hình mốc sang 07:30 | Màn PH, logic API và dòng chữ đều đổi theo | P1 |
| ABS-09 | PH hủy báo nghỉ trước 8:00 / sau 8:00 | Trước: bỏ hoàn. Sau: cần PM chốt | P1 |
| ABS-10 | Bé báo nghỉ nhưng vẫn đến lớp, GV điểm "Có mặt" | Không hoàn, lời nhắn ghi đã bị ghi đè | P0 |
| ABS-11 | Báo nghỉ ngày đã qua | 400 | P1 |
| ABS-12 | PH báo nghỉ cho bé không phải con mình | 403 | P0 |
| ABS-13 | Điểm danh: bé đã báo nghỉ tự hiện "Vắng có phép" (xanh dương), GV vẫn đổi được | Đúng | P0 |
| ABS-14 | Hoàn tiền ăn xuất hiện ở hóa đơn tháng sau, khớp số ngày; kế toán sửa tay có lịch sử | Đúng | P0 |
| ABS-15 | Báo nghỉ 2 lần cùng ngày | Không hoàn trùng | P0 |

## B. Dặn thuốc, "Đã cho uống"
| ID | Mô tả | Kỳ vọng | Ưu tiên |
|---|---|---|---|
| MED-01 | PH dặn thuốc có ảnh, tên thuốc, liều, giờ uống | 201, hiện đầu màn Điểm danh và "Cần chú ý" | P0 |
| MED-02 | Thiếu liều hoặc giờ | 400 | P1 |
| MED-03 | GV lớp bé bấm "Đã cho uống" | Lưu giờ thực + tên cô; PH thấy dấu tích kèm giờ và tên cô | P0 |
| MED-04 | Bấm "Đã cho uống" 2 lần cho cùng một liều | 409 (chống cho uống trùng liều) | P0 |
| MED-05 | GV lớp khác / kế toán / PH khác bấm hoặc xem | 403 | P0 |
| MED-06 | Thuốc nhiều lần trong ngày (10:00, 14:00) | Mỗi lần một dấu tích riêng | P1 |
| MED-07 | Quá giờ uống 30 phút chưa tích | Hiện "thuốc chưa cho uống" trong Cần chú ý | P1 |
| MED-08 | Bé vắng hôm đó | Không nhắc cho uống | P1 |
| MED-09 | PH sửa/hủy dặn thuốc sau khi cô đã cho uống | Không sửa được liều đã uống | P1 |
| MED-10 | Ảnh thuốc: HEIC thật nhận; file giả 400; xem ảnh cần đúng quyền | Đúng | P0 |
| MED-11 | Bé dị ứng với thành phần trùng tên dị ứng trong hồ sơ | Cảnh báo cho cô (cần PM chốt) | P2 |

## C. Xin đón muộn
| ID | Mô tả | Kỳ vọng | Ưu tiên |
|---|---|---|---|
| LATE-01 | PH xin đón muộn kèm giờ | Hiện đầu Điểm danh, không bật nhắc 15 phút trước giờ đó | P1 |
| LATE-02 | Giờ đón muộn ngoài giờ trường cho phép | 400 hoặc cảnh báo | P2 |

## D. Điểm danh
| ID | Mô tả | Kỳ vọng | Ưu tiên |
|---|---|---|---|
| ATT2-01 | "Cả lớp có mặt" | Chỉ đổi bé đang "Chưa điểm", KHÔNG ghi đè bé đã báo nghỉ / đã điểm vắng | P0 |
| ATT2-02 | Bé vắng chọn chip lý do; vắng không phép bắt buộc lý do? | Lưu đúng lý do | P1 |
| ATT2-03 | "Cả lớp có mặt" rồi lưu, đọc lại | Đúng, có lịch sử sửa | P1 |
| ATT2-04 | Lời nhắn PH hiện đầu màn đúng lớp, đúng ngày | Đúng | P1 |

## E. Nhật ký chọn nhiều bé
| ID | Mô tả | Kỳ vọng | Ưu tiên |
|---|---|---|---|
| NOTE-01 | Chọn 5 bé, ghi ăn sáng/ăn trưa/ngủ/vệ sinh một lần | Mỗi bé có bản ghi riêng | P0 |
| NOTE-02 | Trong nhóm có bé đã có nhật ký hôm nay | Không xóa mất dữ liệu cũ (gộp hoặc hỏi) | P0 |
| NOTE-03 | Chọn bé lớp khác qua API | 403 | P0 |
| NOTE-04 | Ghi chú dài 500 ký tự, tiếng Việt có dấu, xuống dòng | Không cắt chữ, ô tự giãn, PH xem đủ | P1 |
| NOTE-05 | Bé vắng có trong nhóm chọn | Bỏ qua hoặc cảnh báo | P2 |

## F. "Cần chú ý"
| ID | Mô tả | Kỳ vọng | Ưu tiên |
|---|---|---|---|
| ATTN-01 | Bấm từng dòng (lớp chưa điểm danh, dị ứng, yêu cầu đón, thuốc chưa uống) | Đi thẳng đúng màn xử lý | P1 |
| ATTN-02 | Xử lý xong quay lại | Dòng biến mất | P2 |

## Câu hỏi cần PM chốt
1. Mốc 8:00 là "trước 8:00" hay "đến hết 8:00"? Em đang để 08:00:00 là không hoàn.
2. Phụ huynh hủy báo nghỉ sau 8:00 (bé vẫn đi học): xử lý ra sao?
3. Ngày lễ/nghỉ trường lấy từ đâu để không tính hoàn?

## G. Bổ sung theo hợp đồng round2 và PM chốt (19:53)
| ID | Mô tả | Kỳ vọng | Ưu tiên |
|---|---|---|---|
| HOL-01 | Áp mẫu lễ dương lịch | Tự có hiệu lực | P1 |
| HOL-02 | Tết, Giỗ Tổ trong mẫu | Trạng thái "chờ xác nhận", KHÔNG có hiệu lực (vẫn tính suất ăn, PH vẫn báo nghỉ được) cho đến khi BGH xác nhận | P0 |
| HOL-03 | BGH xác nhận Tết | Ngày đó: không tính suất, không hoàn, PH không báo nghỉ được, điểm danh hiện "Trường nghỉ" | P0 |
| HOL-04 | GV / PH / kế toán sửa lịch nghỉ | 403 | P0 |
| HOL-05 | Thêm ngày nghỉ khi đã có PH báo nghỉ ngày đó | Không hoàn trùng | P1 |
| ABS-16 | Hủy từng ngày trong khoảng báo nghỉ, ngày đã qua mốc | 409 `CANCEL_AFTER_CUTOFF`, các ngày chưa qua mốc hủy được | P0 |
| ABS-17 | `/settings/school` trả `absenceCutoff`; giao diện dùng giá trị này | Đúng | P1 |
| PWD-01 | Tài khoản `mustChangePassword` gọi `/children`, `/fees`, `/notifications` | 403 `PASSWORD_CHANGE_REQUIRED` | P0 |
| PWD-02 | Cùng tài khoản gọi feed đón trẻ, confirm/reject, ảnh người đón, `/auth/*`, `/settings/school`, đăng ký push | Vẫn 200 | P0 |
| CON-01 | Cờ đồng ý đăng ảnh mặc định `false`; PH bật/tắt cho con mình; PH khác 403; có lịch sử | Đúng | P1 |
| CON-02 | PH gọi danh sách bé / photo-consent của bé không phải con mình | Không thấy cờ, 403 | P0 |
| CON-03 | GV chỉ thấy `photoConsent` của lớp mình; GV lớp khác 403 | Đúng | P1 |
| MSG-H1 | "Nhắn cô" hiện lịch sử 30 ngày, chỉ xem, gom theo tháng; ngày 31 trở về trước không hiện | Đúng | P2 |
| MSG-H2 | Ngày nghỉ đã qua ghi "Được hoàn" (báo trước 8:00) / "Không hoàn, báo sau 8:00" (kể cả đúng 08:00:00) | Khớp với hóa đơn | P1 |
| MSG-H3 | Tin đã qua không có nút hủy/sửa | Đúng | P1 |
| MSG-H4 | PH gọi `GET /children/:id/absences?from&to` của bé khác | 403 | P0 |
| MSG-H5 | Lịch sử không chứa ngày trường nghỉ đã xác nhận; có `reportedAt`, `refundEligible` | Đúng | P1 |
| HOL-06 | Tạo ngày nghỉ trùng ngày đã có điểm danh (đường thường) | 409 `HOLIDAY_HAS_ATTENDANCE`, không đổi dữ liệu | P1 |
| HOL-07 | BGH "Đóng cửa đột xuất" ngày đã điểm danh, thiếu lý do | 400 | P1 |
| HOL-08 | Đóng cửa đột xuất có lý do | Điểm danh giữ nguyên; bé chưa đến được hoàn suất, bé đã có mặt không hoàn; lưu `audit_events` (ai, lúc, lý do) | P0 |
| HOL-09 | Đóng cửa đột xuất | Mọi PH của trường nhận thông báo quan trọng; PH không bị trùng báo nghỉ/hoàn hai lần | P0 |
| HOL-10 | GV/KT/PH gọi đóng cửa đột xuất | 403 | P0 |
| ATT-21 | GV đổi "Vắng có phép" về "Vắng" (`absenceReason: null`), tải lại | Hết lý do, trạng thái "Vắng"; báo cáo tháng đếm đúng | P1 |
| ATT-22 | Bé vắng có lý do do cô ghi, PH không báo | "Vắng có phép" nhưng `refundEligible=false` | P1 |
| ATT-23 | Màn điểm danh không có huy hiệu 🚫 | Đúng | P3 |
| EMG-01 | `dryRun` trả `childrenWithoutParent[{childId,name,className,phone1}]`; số khớp với dữ liệu thật | Đúng | P1 |
| EMG-02 | Chỉ admin thấy danh sách này (có SĐT); không lưu khi dryRun | Đúng | P0 |
| EMG-03 | UI: 5 bé đầu + "Xem tất cả", nhóm theo lớp, link `tel:`, tải file | Đúng | P2 |
| EMG-04 | Bé không có tài khoản PH và `phone1` null | Vẫn có trong `childrenWithoutParent` (phone1 null); UI hiện nhãn đỏ "Chưa có số điện thoại" thay link `tel:` | P0 |
