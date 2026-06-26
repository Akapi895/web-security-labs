# Phòng thủ và giảm thiểu lỗ hổng WebSocket

## Mục tiêu

Đưa ra chiến lược phòng thủ đa lớp cho WebSocket dựa trên nguyên nhân gốc rễ, không chỉ vá triệu chứng.

## Ưu tiên kiểm soát cốt lõi

## 1. Bảo mật kênh truyền

1. Bắt buộc `wss://` trong môi trường production.
2. Tắt giao thức/phiên bản cũ, chuẩn hóa theo RFC hiện hành.
3. Chỉ bật compression khi thật sự cần và đã đánh giá rủi ro.

## 2. Siết chặt handshake

1. Xác thực bắt buộc ngay khi mở kết nối.
2. Kiểm tra `Origin` theo allowlist chính xác (scheme + host + port).
3. Không tin tưởng header có thể bị giả mạo để quyết định quyền.
4. Bổ sung cơ chế chống giả mạo handshake khi dùng cookie-based auth.

## 3. Authorization ở từng message

1. Mỗi action phải có kiểm quyền riêng.
2. Ràng buộc ownership theo resource/user/tenant.
3. Áp dụng state machine validation cho chuỗi hành động.

## 4. Input validation và xử lý an toàn

1. Validate schema phía server bằng allowlist.
2. Giới hạn kích thước payload và độ sâu cấu trúc.
3. Dùng API truy vấn an toàn (parameterized), không dựng lệnh động.
4. Encode output trước khi render ở client.

## 5. Quản lý session cho kết nối dài hạn

1. Re-validate session định kỳ với socket đang mở.
2. Đóng socket khi logout, expire, hoặc revoke token.
3. Hỗ trợ token rotation cho phiên dài.

## 6. Chống DoS và abuse tài nguyên

1. Giới hạn kết nối theo user/IP/tenant.
2. Rate-limit theo message type/action.
3. Heartbeat + idle timeout + cleanup kết nối chết.
4. Cơ chế backpressure và queue guard.

## 7. Logging, monitoring, và phản ứng sự cố

1. Log theo sự kiện message, không chỉ handshake.
2. Gắn correlation id: `connection_id`, `user_id`, `action`.
3. Cảnh báo bất thường: burst message, authz deny spike, close code bất thường.
4. Duy trì dashboard giám sát real-time cho luồng WebSocket.

## Checklist triển khai nhanh

| Kiểm soát                        | Mức ưu tiên |
| -------------------------------- | ----------- |
| Origin allowlist chính xác       | Critical    |
| Message-level authZ              | Critical    |
| Server-side schema validation    | High        |
| Session revoke + socket teardown | High        |
| Rate-limit + max payload         | High        |
| Message telemetry                | High        |

## Sai lầm phổ biến cần tránh

1. "Đã đăng nhập thì mọi message đều tin cậy".
2. Chỉ chống CSRF cho HTTP form, quên handshake WebSocket.
3. Chỉ dựa vào WAF/proxy mà không validate ở ứng dụng.
4. Không test hồi quy bảo mật sau khi thay đổi protocol real-time.

## Tệp liên quan

- [Điều kiện và nguyên nhân gốc rễ](03-conditions-and-root-causes.md)
- [CSWSH](07-cross-site-websocket-hijacking-cswsh.md)
- [DoS và cạn kiệt tài nguyên](10-denial-of-service-and-resource-exhaustion.md)
- [Kịch bản lab và huấn luyện agent](14-labs-and-agent-training-scenarios.md)
