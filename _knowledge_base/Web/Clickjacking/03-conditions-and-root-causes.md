# Điều kiện và nguyên nhân gốc rễ

## Mục tiêu

Xác định vì sao lỗ hổng clickjacking xuất hiện và điều kiện nào phải tồn tại để tấn công khả thi trong thực tế.

## Nhóm nguyên nhân chính

## 1. Thiếu cơ chế chống nhúng khung

Không có chính sách phía máy chủ đủ hiệu lực để hạn chế framing:

1. Thiếu `Content-Security-Policy: frame-ancestors ...`
2. Thiếu `X-Frame-Options` ở các đường dẫn legacy
3. Bao phủ header không đồng nhất giữa các route

## 2. Thiết kế chính sách yếu hoặc sai

1. Danh sách origin được phép nhúng quá rộng.
2. Giả định cũ rằng frame-busting phía client là đủ.
3. Endpoint production vô tình vẫn có thể bị nhúng.

## 3. Lỗi UI/UX tại hành động nhạy cảm

Ngay cả khi có thể bị nhúng, mức khai thác tăng mạnh nếu UX yếu:

1. Hành động một cú nhấp nhưng không thể hoàn tác.
2. Không có bước xác nhận cho thay đổi tác động cao.
3. Nút hành động đặt cố định, dễ đoán tọa độ.
4. Không yêu cầu re-auth/step-up cho thao tác tài khoản quan trọng.

## 4. Bối cảnh phiên cho phép hành động

Nạn nhân đang đăng nhập và hành động mục tiêu có thể thực thi trong đúng bối cảnh phiên đó.

## Vì sao chỉ CSRF token là chưa đủ

Trong clickjacking, request thường xuất phát từ UI hợp lệ của trang đích trong một phiên thật. CSRF token vẫn có thể hợp lệ, vì người dùng đang tương tác với nội dung thật của origin đích, chỉ là không nhận thức đúng hành động.

## Điều kiện tiên quyết để tấn công thành công

| Nhóm điều kiện | Điều kiện bắt buộc |
| --- | --- |
| Endpoint mục tiêu | Có thể bị nhúng bởi trang do attacker kiểm soát |
| Trình duyệt/phiên | Nạn nhân đã xác thực hoặc được phân quyền phù hợp |
| Hình học UI | Control nhạy cảm có thể căn chỉnh hoặc dẫn hướng |
| Yếu tố con người | Nạn nhân thực hiện thao tác nhấp/cử chỉ như dự kiến |
| Độ ổn định thời điểm | UI ổn định đủ lâu để kích hoạt |

## Các trường hợp thực tế khiến tấn công thất bại

Tấn công thường thất bại khi:

1. `frame-ancestors 'none'` hoặc allowlist chặt chặn nhúng.
2. Hành động nhạy cảm yêu cầu re-auth / OTP / xác nhận gõ tay.
3. UI mục tiêu quá động, khó căn chỉnh ổn định.
4. Người dùng chưa đăng nhập hoặc không đủ quyền.

## Checklist rà nguyên nhân gốc

1. Mọi route nhạy cảm đã được bảo vệ khỏi framing chưa?
2. Đã xét tương thích cả trình duyệt hiện đại lẫn legacy chưa?
3. Hành động rủi ro cao đã có lớp xác nhận bổ sung chưa?
4. Đã có kiểm thử clickjacking trong regression/release gate chưa?

## Tệp liên quan

- [Phát hiện và lập bản đồ mục tiêu](04-detection-and-target-mapping.md)
- [Khai thác cơ bản](05-basic-exploitation.md)
- [Phòng thủ và giảm thiểu](13-defense-mitigation.md)
