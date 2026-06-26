# Nền tảng giao thức và handshake WebSocket

## Mục tiêu

Hiểu đúng cách WebSocket hoạt động để xác định chính xác nơi phát sinh lỗ hổng bảo mật.

## Luồng thiết lập kết nối

1. Trình duyệt gửi HTTP request với cơ chế Upgrade.
2. Server xác nhận điều kiện và phản hồi `101 Switching Protocols`.
3. Kết nối chuyển sang kênh WebSocket dài hạn để trao đổi frame hai chiều.

Ví dụ handshake rút gọn:

```http
GET /chat HTTP/1.1
Host: app.example.com
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Version: 13
Sec-WebSocket-Key: <random-base64>
Origin: https://app.example.com
Cookie: session=...
```

```http
HTTP/1.1 101 Switching Protocols
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Accept: <derived-value>
```

## Ý nghĩa bảo mật của các thành phần handshake

| Thành phần               | Mục đích kỹ thuật                      | Rủi ro nếu xử lý sai                                            |
| ------------------------ | -------------------------------------- | --------------------------------------------------------------- |
| `Upgrade` + `Connection` | Kích hoạt chuyển giao thức             | Proxy/reverse proxy parse sai có thể mở bề mặt smuggling        |
| `Sec-WebSocket-Key`      | Nonce phía client cho handshake        | Không dùng cho auth; hiểu sai dễ tạo trust sai                  |
| `Sec-WebSocket-Accept`   | Xác nhận server thực sự đồng ý upgrade | Không thay thế cơ chế xác thực người dùng                       |
| `Origin`                 | Nguồn khởi tạo kết nối từ trình duyệt  | Bỏ kiểm tra hoặc kiểm tra yếu dẫn tới CSWSH                     |
| Cookie / token           | Gắn phiên đăng nhập vào socket         | Chỉ dựa cookie mà không anti-CSRF/origin kiểm soát sẽ nguy hiểm |

Ghi chú kỹ thuật: `Sec-WebSocket-Accept` được suy ra từ `Sec-WebSocket-Key + GUID` qua hàm băm SHA-1 rồi Base64. Cơ chế này xác nhận đúng tiến trình handshake, không phải kiểm soát truy cập.

## Sau handshake: giao tiếp stateful theo frame

1. Text/Binary frame mang dữ liệu nghiệp vụ.
2. Ping/Pong giữ sống kết nối và hỗ trợ health check.
3. Close frame đóng kết nối với mã trạng thái.

Điểm khác quan trọng: sau khi kết nối mở, nhiều hệ thống không còn đi qua đầy đủ middleware bảo mật kiểu HTTP route-by-route, nên validation và authorization phải được triển khai riêng ở tầng message.

## Socket.IO và giao thức lớp trên

Một số ứng dụng dùng Socket.IO hoặc protocol tùy biến trên WebSocket:

1. Có thêm bước bắt tay riêng của framework.
2. Message có framing riêng (event name, namespace, ack id).
3. Heartbeat riêng ngoài ping/pong chuẩn.

Pentest cần mô hình đúng protocol lớp ứng dụng thay vì chỉ xem payload JSON thô.

## Khác biệt bảo mật giữa HTTP và WebSocket

| Chủ đề           | HTTP                          | WebSocket                                             |
| ---------------- | ----------------------------- | ----------------------------------------------------- |
| AuthN/AuthZ      | Thường kiểm tra ở mỗi request | Dễ chỉ kiểm tra lúc connect rồi bỏ sót ở từng message |
| CSRF             | Được quan tâm rộng rãi        | Dễ quên CSWSH ở handshake                             |
| Input validation | Tập trung ở endpoint/body     | Cần áp dụng cho mọi message và trạng thái             |
| Monitoring       | Dễ ghi log theo request       | Cần log theo sự kiện/message để thấy lạm dụng         |

## Tệp liên quan

- [Tổng quan](00-overview.md)
- [Nguyên nhân gốc rễ và điều kiện khai thác](03-conditions-and-root-causes.md)
- [CSWSH](07-cross-site-websocket-hijacking-cswsh.md)
- [Phòng thủ và giảm thiểu](13-defense-mitigation.md)
