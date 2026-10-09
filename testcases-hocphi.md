# Test case học phí – tuần 2 (theo 9 điểm PM chốt)

## Hoàn tiền ăn ngày nghỉ (điểm 3)
| ID | Mô tả | Kỳ vọng | Ưu tiên |
|---|---|---|---|
| FEE-R01 | Bé vắng 3 ngày có báo trước trong tháng 10 | Hóa đơn tháng 11 có dòng hoàn = 3 × đơn giá tiền ăn | P0 |
| FEE-R02 | Vắng không báo trước | Không hoàn | P0 |
| FEE-R03 | Đi muộn | Không hoàn, vẫn tính là ngày đi học | P1 |
| FEE-R04 | Vắng có báo nhưng điểm danh sửa lại thành có mặt (trong 3 ngày) | Hoàn cập nhật lại, không hoàn trùng | P0 |
| FEE-R05 | Generate hóa đơn tháng 11 hai lần | Không tạo trùng dòng hoàn | P0 |
| FEE-R06 | Kế toán sửa tay số tiền hoàn | Lưu, có lịch sử ai sửa | P1 |
| FEE-R07 | Giáo viên / phụ huynh sửa tiền hoàn | 403 | P0 |
| FEE-R08 | Đơn giá tiền ăn đổi giữa tháng | Hoàn theo đơn giá của ngày vắng | P2 |
| FEE-R09 | Bé nghỉ học hẳn cuối tháng | Phần hoàn chuyển thành số dư hoặc hoàn trả (cần PM chốt) | P1 |

## Trả trước, số dư (điểm 5)
| ID | Mô tả | Kỳ vọng | Ưu tiên |
|---|---|---|---|
| FEE-P01 | Hóa đơn 2.000.000đ, trả 2.500.000đ | Hóa đơn đã trả, số dư +500.000đ | P0 |
| FEE-P02 | Tháng sau tự trừ số dư vào hóa đơn mới | Còn phải trả = tổng − 500.000đ | P0 |
| FEE-P03 | Số dư lớn hơn hóa đơn tháng sau | Hóa đơn 0đ, phần dư chuyển tiếp | P1 |
| FEE-P04 | Trả thiếu 1.500.000đ / 2.000.000đ | Trạng thái trả một phần, công nợ 500.000đ | P0 |
| FEE-P05 | Thanh toán nhiều lần cộng dồn | Đúng tổng, mỗi lần một biên lai | P0 |
| FEE-P06 | Hủy hóa đơn đã có thanh toán | Tiền đã trả chuyển về số dư, không mất | P0 |
| FEE-P07 | Hai request thanh toán gửi đồng thời | Không ghi trùng, số dư đúng | P1 |
| FEE-P08 | Số tiền lẻ, rất lớn (999.999.999đ), chữ | 400 với dữ liệu sai; lưu đúng số nguyên VND | P1 |
| FEE-P09 | `GET /children/:id/balance` khớp tổng hóa đơn − tổng thanh toán | Khớp | P0 |

## Giảm trừ (điểm 6)
| ID | Mô tả | Kỳ vọng | Ưu tiên |
|---|---|---|---|
| FEE-D01 | Thêm giảm trừ anh chị em kèm lý do | Dòng riêng loại "giảm trừ", tổng giảm đúng | P0 |
| FEE-D02 | Giảm trừ không có lý do | 400 | P0 |
| FEE-D03 | Nhập số âm cho bất kỳ khoản nào | 400 | P0 |
| FEE-D04 | Giảm trừ lớn hơn tổng hóa đơn | Chặn hoặc hóa đơn tối thiểu 0đ (cần chốt) | P1 |
| FEE-D05 | Giảm trừ theo % và theo số tiền cố định | Làm tròn đúng đến đồng | P1 |
| FEE-D06 | Phụ huynh xem hóa đơn thấy dòng giảm trừ + lý do | Hiển thị | P2 |

## Quá hạn (điểm 7)
| ID | Mô tả | Kỳ vọng | Ưu tiên |
|---|---|---|---|
| FEE-O01 | Chưa trả, ngày 10 | Chưa quá hạn | P0 |
| FEE-O02 | Chưa trả, ngày 11 (giờ VN 00:01) | Quá hạn, tô hồng trong `/debts` | P0 |
| FEE-O03 | Trả đủ sau ngày 10 | Hết quá hạn | P0 |
| FEE-O04 | Trả một phần sau hạn | Vẫn quá hạn với phần còn lại | P1 |
| FEE-O05 | Không có phí trễ hạn tự sinh | Không có dòng phí | P1 |
| FEE-O06 | Lọc `/debts` theo lớp, quá hạn; tổng công nợ khớp | Khớp | P1 |

## Biên lai, phân quyền
| ID | Mô tả | Kỳ vọng | Ưu tiên |
|---|---|---|---|
| FEE-B01 | Số tiền bằng chữ: 0, 1.000.005, 2.150.000, 1.000.000.000 | Đọc đúng tiếng Việt ("một triệu không trăm linh năm đồng") | P0 |
| FEE-B02 | Số biên lai liên tục, không trùng | Đúng | P1 |
| FEE-B03 | ph2 xem biên lai / hóa đơn con ph1 | 403 | P0 |
| FEE-B04 | Giáo viên xem hóa đơn | 403 | P0 |
| FEE-B05 | Tên, địa chỉ, SĐT trường trên biên lai | Đúng thông tin thật (chờ anh/chị cung cấp) | P1 |
| FEE-B06 | Khoản thu một lần thêm tay chỉ áp cho bé được chọn | Đúng | P1 |

## Câu hỏi cần PM chốt
1. Bé nghỉ học hẳn: tiền hoàn và số dư trả trước xử lý thế nào?
2. Giảm trừ lớn hơn tổng hóa đơn: chặn hay để hóa đơn 0đ?

## Bổ sung theo 3 quy tắc PM chốt
| ID | Mô tả | Kỳ vọng | Ưu tiên |
|---|---|---|---|
| FEE-V01 | Kế toán / BGH hủy hóa đơn đã thanh toán, có lý do | Tiền về số dư, có lịch sử (ai, lúc nào, lý do) | P0 |
| FEE-V02 | Hủy không có lý do | 400 | P0 |
| FEE-V03 | Giáo viên / phụ huynh hủy hóa đơn | 403 | P0 |
| FEE-V04 | Hủy một hóa đơn hai lần | 409, số dư không cộng hai lần | P0 |
| FEE-W01 | Bé nghỉ hẳn giữa tháng, số dư dương | Chốt công nợ đến ngày nghỉ, tính cả tiền ăn hoàn; phiếu chi + biên lai; số dư về 0 | P0 |
| FEE-W02 | Bé nghỉ hẳn, số dư âm | Vẫn nằm trong `/debts` cho đến khi trả xong | P0 |
| FEE-W03 | Hồ sơ bé đã nghỉ | Trạng thái "đã nghỉ", dữ liệu cũ vẫn xem được, không còn trong danh sách điểm danh, không sinh hóa đơn tháng sau | P0 |
| FEE-W04 | Phiếu chi hoàn lớn hơn số dư | 400 | P1 |
| FEE-X01 | Giảm trừ lớn hơn hóa đơn tạo tự động | Hóa đơn 0đ, không sinh số dư, có cảnh báo | P0 |
| FEE-X02 | Giảm trừ lớn hơn hóa đơn tạo tay | Giống hệt X01, không còn bị chặn | P0 |
| FEE-X03 | Số tiền bằng chữ so sánh không phân biệt hoa thường | Đúng | P1 |
| ACC-01 | Sai mật khẩu 5 lần trong 15 phút | Lần thứ 5/6 bị khóa 15 phút, kể cả khi nhập đúng | P0 |
| ACC-02 | Đổi mật khẩu: sai mật khẩu cũ, mật khẩu mới quá ngắn | 400; đổi xong token/refresh cũ hết hiệu lực | P0 |
| ACC-03 | Giáo viên / phụ huynh gọi `/users` | 403 | P0 |
