# Phát hiện và lập bản đồ mục tiêu

## Mục tiêu

Cung cấp phương pháp lặp lại được để xác định liệu clickjacking có khả thi hay không và mức tác động có ý nghĩa thực tế hay không.

## Giai đoạn 1: Liệt kê endpoint ứng viên

Ưu tiên các trang có thay đổi trạng thái do người dùng kích hoạt:

1. Thiết lập bảo mật tài khoản.
2. Đổi thông tin hồ sơ/email/mật khẩu.
3. Thanh toán, chuyển khoản, xác nhận mua hàng.
4. Màn hình đồng ý quyền OAuth.
5. Nút bật/tắt quản trị và thao tác hủy hoại.

## Giai đoạn 2: Xác minh chính sách framing

Kiểm tra header phản hồi ở từng endpoint ứng viên:

1. `Content-Security-Policy` có `frame-ancestors`.
2. `X-Frame-Options` cho mục tiêu tương thích.

Phát hiện thường gặp:

| Quan sát | Ý nghĩa |
| --- | --- |
| Không có `frame-ancestors`, không có `X-Frame-Options` | Khả năng cao có thể bị nhúng |
| `X-Frame-Options: DENY` | Bị chặn nhúng (phụ thuộc hỗ trợ trình duyệt cũ) |
| `CSP frame-ancestors 'none'` | Chặn nhúng mạnh |
| Allowlist hẹp | Chỉ origin được liệt kê mới nhúng được |

## Giai đoạn 3: Kiểm tra khả năng nhúng khung

Dùng trang test local để nhúng endpoint mục tiêu trong iframe.

Kết quả kỳ vọng:

1. Trang hiển thị trong khung: endpoint có thể bị nhúng.
2. Trình duyệt từ chối hiển thị khung: cơ chế bảo vệ đang hoạt động.

## Giai đoạn 4: Phân tích khả năng khai thác hành động

Với trang có thể bị nhúng, đánh giá:

1. Có hành động nhạy cảm kiểu một cú nhấp không?
2. Control có nằm ở tọa độ dễ dự đoán không?
3. Có bước xác nhận bổ sung không?
4. Có yêu cầu re-auth/step-up không?

## Giai đoạn 5: Độ tin cậy và tính khả thi ép thao tác

1. Độ ổn định layout desktop so với mobile.
2. Ảnh hưởng của nội địa hóa và viewport.
3. Nhu cầu tương tác nhiều bước.
4. Chất lượng mồi lừa trong thực tế.

## Bằng chứng cần thu thập

1. Header request/response chứng minh trạng thái chính sách framing.
2. Ảnh/chuỗi video thể hiện trang mục tiêu bị nhúng.
3. PoC tương tác cho thấy kết quả trái phép.
4. Mô tả tác động rõ ràng cùng điều kiện tiên quyết.

## Công cụ

1. Developer tools của trình duyệt.
2. Proxy tooling để kiểm tra header.
3. Burp Clickbandit để tạo nhanh overlay PoC.

## False positive thường gặp

1. Trang có thể nhúng nhưng không có control nhạy cảm để khai thác.
2. Có hành động nhạy cảm nhưng được bảo vệ tốt bằng re-auth.
3. PoC chỉ hoạt động trong điều kiện viewport quá nhân tạo.

## Hướng dẫn báo cáo

1. Tách bạch “có thể nhúng” và “có thể khai thác”.
2. Nêu rõ precondition (role đăng nhập, trình duyệt, viewport).
3. Gắn tác động kinh doanh vào hành động thực tế đã chứng minh.

## Tệp liên quan

- [Điều kiện và nguyên nhân gốc rễ](03-conditions-and-root-causes.md)
- [Workflow khai thác](11-exploitation-workflows.md)
- [Phòng thủ và giảm thiểu](13-defense-mitigation.md)
