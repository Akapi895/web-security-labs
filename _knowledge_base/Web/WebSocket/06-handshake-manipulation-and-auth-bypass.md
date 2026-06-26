# Khai thác handshake và bypass xác thực

## Mục tiêu

Phân tích các lỗi thiết kế xuất hiện ngay ở bước mở kết nối WebSocket, nơi nhiều ứng dụng đặt niềm tin sai vào metadata HTTP.

## Vì sao handshake là điểm tấn công quan trọng

Handshake quyết định ngữ cảnh phiên cho toàn bộ kết nối dài hạn. Nếu bước này sai, mọi message phía sau có thể được xử lý trong ngữ cảnh sai quyền.

## Mẫu lỗi thường gặp

## 1. Tin cậy header không đáng tin

1. Dùng `X-Forwarded-For` hoặc header custom để quyết định quyền.
2. Dùng `Host`/`Origin` parse sai trong mô hình multi-tenant.
3. Cho phép override thông tin định danh qua query/header.

## 2. Xác thực không nhất quán giữa endpoint

1. Endpoint chính có auth, endpoint phụ hoặc debug endpoint không auth.
2. Cùng chức năng nhưng đường dẫn khác nhau có policy khác nhau.
3. Reconnect flow bỏ qua một phần kiểm soát ban đầu.

## 3. Sai sót trong xử lý token phiên

1. Chấp nhận token hết hạn do không re-validate.
2. Không bind token với user agent/context expected.
3. Chấp nhận session cũ sau logout.

## 4. WebSocket smuggling / Upgrade confusion

1. Proxy và backend diễn giải khác nhau về `Upgrade`/`Connection`.
2. Có thể chạm endpoint ẩn phía sau reverse proxy.

## Kỹ thuật kiểm thử handshake có hệ thống

1. Clone handshake hợp lệ.
2. Thay đổi từng thành phần có kiểm soát: origin, cookie/token, subprotocol, custom header.
3. Kết nối lại và so sánh phản hồi 101/reject.
4. Gửi message nhạy cảm để xác nhận ngữ cảnh quyền thực tế.

## Bảng kiểm thử đề xuất

| Kiểm thử                     | Kỳ vọng an toàn                       | Dấu hiệu lỗ hổng                 |
| ---------------------------- | ------------------------------------- | -------------------------------- |
| Không có cookie/token        | Bị từ chối ngay từ handshake          | Vẫn nhận 101 và thao tác được    |
| Origin không thuộc allowlist | Bị từ chối                            | Kết nối thành công               |
| Token hết hạn                | Bị từ chối hoặc đóng ngay sau connect | Socket vẫn hoạt động dài hạn     |
| Header giả mạo               | Không ảnh hưởng quyền                 | Quyền bị nâng bất thường         |
| Subprotocol lạ               | Bị từ chối                            | Được chấp nhận và mở thêm bề mặt |

## Điều kiện cần để bypass thành công

1. Có thành phần kiểm soát được attacker tác động trong handshake.
2. Logic xác thực/phân quyền phụ thuộc thành phần đó.
3. Không có kiểm tra bổ sung ở tầng message.

## Tác động điển hình

1. Truy cập dữ liệu không thuộc quyền.
2. Thực thi hành động admin từ tài khoản thường.
3. Mở đường cho injection hoặc lạm dụng logic ở các bước sau.

## Tệp liên quan

- [Nền tảng giao thức và handshake](01-websocket-protocol-and-handshake.md)
- [Điều kiện và nguyên nhân gốc rễ](03-conditions-and-root-causes.md)
- [CSWSH](07-cross-site-websocket-hijacking-cswsh.md)
- [Workflow khai thác](11-exploitation-workflows.md)
