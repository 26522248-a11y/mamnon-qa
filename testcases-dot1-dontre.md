# Test case đợt 1 – An toàn đón trẻ (góp ý Mầm non Như Ý)

## A. Danh sách người đón hộ do phụ huynh đăng ký
| ID | Mô tả | Kỳ vọng | Ưu tiên |
|---|---|---|---|
| PK-A01 | PH thêm người đón hộ đủ tên, quan hệ, ảnh, CCCD 12 số, 2 SĐT | 201, hiện trong danh sách của bé | P0 |
| PK-A02 | Thiếu ảnh hoặc CCCD | 400 | P0 |
| PK-A03 | CCCD sai định dạng (≠12 số, có chữ), SĐT sai | 400 | P1 |
| PK-A04 | PH thêm người đón cho bé không phải con mình | 403 | P0 |
| PK-A05 | Ảnh/CCCD người đón: chưa login 401, PH khác 403, GV lớp khác 403 | Đúng | P0 |
| PK-A06 | PH xóa/sửa người đón hộ | Có hiệu lực ngay, lưu lịch sử | P1 |
| PK-A07 | Hai PH của cùng một bé: người này thêm, người kia thấy | Đúng | P1 |
| PK-A08 | Số CCCD hiển thị che bớt (ví dụ ***456) trừ màn giao bé | Đúng | P1 |

## B. Người đón ngoài danh sách, thông báo đẩy
| ID | Mô tả | Kỳ vọng | Ưu tiên |
|---|---|---|---|
| PK-B01 | GV tạo yêu cầu kèm ảnh người đón | PH nhận web push trong vài giây | P0 |
| PK-B02 | Bấm Xác nhận / Từ chối ngay trên push | Trạng thái cập nhật đúng, không cần mở app | P0 |
| PK-B03 | Push chỉ tới PH của bé đó | PH khác không nhận | P0 |
| PK-B04 | PH chưa cho phép thông báo / tắt push | Vẫn thấy yêu cầu nổi trên đầu "Bé hôm nay" | P0 |
| PK-B05 | Yêu cầu đón không nằm trong hộp thư chung, hiện nổi kèm ảnh | Đúng | P1 |
| PK-B06 | Nút trên push bị bấm 2 lần / bấm sau khi đã hết hạn | 409, không đổi trạng thái | P1 |
| PK-B07 | Xác nhận từ push dùng link giả/ID khác | 403 | P0 |

## C. Quá 15 phút chưa trả lời
| ID | Mô tả | Kỳ vọng | Ưu tiên |
|---|---|---|---|
| PK-C01 | Ở phút 14:59 | Chưa nhắc | P1 |
| PK-C02 | Ở phút 15 | Màn GV nhắc gọi số 1, sau đó số 2 | P0 |
| PK-C03 | Sau 15 phút, sau 2 giờ, cuối ngày | Không bao giờ tự giao bé, không tự chuyển "đã xác nhận" | P0 |
| PK-C04 | PH trả lời sau khi đã nhắc | Nhắc biến mất, trạng thái cập nhật | P1 |

## D. Giao bé: cần đủ 2 bước (P0 toàn bộ)
| ID | Mô tả | Kỳ vọng |
|---|---|---|
| PK-D01 | Chỉ PH xác nhận, nhà trường chưa duyệt → giao bé | API 403, nút khóa |
| PK-D02 | Chỉ nhà trường duyệt, PH chưa xác nhận → giao bé | API 403, nút khóa |
| PK-D03 | Đủ PH xác nhận + nhà trường duyệt | Giao được, ghi giờ và ai giao |
| PK-D04 | PH xác nhận rồi nhà trường từ chối (hoặc ngược lại) | Không giao được |
| PK-D05 | Gọi thẳng API `pickup` bỏ qua giao diện | Vẫn 403 khi thiếu một bước |
| PK-D06 | GV (kể cả GV chủ nhiệm) gọi API duyệt phần "nhà trường" | 403 (chỉ BGH hoặc tài khoản trực đón) |
| PK-D07 | Giao bé hai lần | 409 |
| PK-D08 | Bố mẹ / người đón hộ đã đăng ký và đã được BGH duyệt | Giao luôn, không cần 2 bước; PH nhận thông báo "Bé đã được X đón lúc HH:MM" |
| PK-D08b | Người đón hộ PH vừa đăng ký nhưng BGH chưa duyệt | Bị coi là ngoài danh sách, cần đủ 2 bước |
| PK-D09 | Yêu cầu hết hạn sau khi đủ 2 bước nhưng chưa giao | Không giao được |
| PK-D10 | Màn giao bé hiện ảnh to + CCCD đầy đủ | Đúng |

## E. Hiệu trưởng duyệt nhanh, cảnh báo
| ID | Mô tả | Kỳ vọng | Ưu tiên |
|---|---|---|---|
| PK-E01 | BGH duyệt không ghi chú | Thành công | P1 |
| PK-E02 | BGH từ chối không ghi chú | 400 | P1 |
| PK-E03 | Một người (cùng CCCD/SĐT) đón ≥2 bé trong ngày | Hiện cảnh báo, không chặn | P1 |
| PK-E04 | Anh chị em ruột được cùng người đón | Vẫn cảnh báo nhưng ghi rõ quan hệ | P2 |

## F. Tên trường
| ID | Mô tả | Kỳ vọng | Ưu tiên |
|---|---|---|---|
| PK-F01 | `/settings/school` trả "Mầm non Như Ý"; login, menu, biên lai, phiếu chi đều đổi | Đúng | P1 |

## Câu hỏi cần PM chốt
1. Người đón có sẵn trong danh sách (bố mẹ, người đón hộ đã đăng ký) có cần 2 bước không, hay chỉ áp cho người ngoài danh sách?
2. "Nhà trường duyệt" là chỉ BGH, hay giáo viên chủ nhiệm cũng được?
3. Web push trên iPhone chỉ chạy khi phụ huynh thêm web vào màn hình chính (iOS 16.4 trở lên). Có chấp nhận không, hay cần thêm SMS hoặc Zalo dự phòng?

## G. Tài khoản "trực đón" (theo PM chốt)
| ID | Mô tả | Kỳ vọng | Ưu tiên |
|---|---|---|---|
| PK-G01 | BGH chỉ định tài khoản X trực đón ngày hôm nay | X duyệt được yêu cầu hôm nay | P0 |
| PK-G02 | X duyệt yêu cầu của ngày khác / sau khi hết ngày trực | 403 | P0 |
| PK-G03 | X là GV của chính lớp có bé đó, vừa duyệt vừa giao | Chặn: người duyệt và người giao phải khác nhau | P0 |
| PK-G04 | Người không phải BGH tự chỉ định trực đón | 403 | P0 |
| PK-G05 | Lịch sử ghi ai duyệt với vai trò gì (BGH / trực đón) | Đúng | P1 |

## H. Kênh dự phòng
| ID | Mô tả | Kỳ vọng | Ưu tiên |
|---|---|---|---|
| PK-H01 | PH dùng iPhone chưa thêm vào màn hình chính (không có push) | Sau 15 phút GV được nhắc gọi số 1 rồi số 2, nút `tel:` đúng số | P0 |
| PK-H02 | Push gửi thất bại (subscription hết hạn) | Ghi log, không làm hỏng luồng, vẫn có nhắc 15 phút | P1 |

## I. Bổ sung theo PM chốt (19:30)
| ID | Mô tả | Kỳ vọng | Ưu tiên |
|---|---|---|---|
| PK-I01 | PH sửa SĐT liên hệ 1/2 hợp lệ | Lưu ngay, lịch sử (cũ→mới, ai, lúc nào), BGH nhận thông báo | P1 |
| PK-I02 | Sửa SĐT sai định dạng / trùng nhau | 400 | P1 |
| PK-I03 | PH sửa SĐT của bé không phải con mình | 403 | P0 |
| PK-I04 | Đang có yêu cầu quá 15 phút, PH vừa đổi số | Nút gọi trên màn GV dùng số mới | P1 |
| PK-I05 | Danh sách yêu cầu đón có `className` đúng | Đúng | P2 |
| PK-I06 | `dueAt` = createdAt + `PICKUP_ESCALATE_MINUTES`; đổi cấu hình thì đổi theo | Đúng, theo giờ VN | P1 |
| PK-I07 | Ảnh HEIC thật (`/workspace/qa/heic/that.heic`) | 201, lưu thành JPEG, xem lại ra đúng ảnh | P1 |
| PK-I08 | File .exe / text đổi đuôi `.heic` (`gia_exe.heic`, `gia_txt.heic`) | 400 | P0 |
| PK-I09 | HEIC rất lớn (>5 MB) | 413 | P2 |
