# Điều kiện và nguyên nhân gốc rễ

## Mục tiêu

Làm rõ tại sao lỗ hổng WebSocket hình thành và những điều kiện cần để bị khai thác thực tế.

## Nhóm nguyên nhân gốc rễ

## 1. Thiếu xác thực hoặc kiểm soát truy cập ở handshake

1. Endpoint chấp nhận kết nối mà không xác thực người dùng.
2. Xác thực tùy chọn (optional) nhưng không bắt buộc cho action nhạy cảm.
3. Tin cậy metadata handshake thay vì xác minh session/token đúng chuẩn.

Hệ quả: attacker có thể mở kênh hợp lệ về mặt kỹ thuật nhưng không hợp lệ về quyền.

## 2. Không kiểm tra Origin hoặc kiểm tra sai cách

1. Không kiểm tra header `Origin`.
2. So khớp theo substring/wildcard quá rộng.
3. Logic allowlist bị bypass do parse URL sai.

Hệ quả: dễ phát sinh CSWSH khi cookie phiên được gửi tự động.

## 3. Xử lý message không an toàn

1. Parse dữ liệu không ràng buộc schema.
2. Dùng dynamic dispatch theo trường `action` mà không kiểm quyền.
3. Deserialize/transform dữ liệu không an toàn.

Hệ quả: injection, lạm dụng hành động trái phép, hoặc thực thi logic ngoài dự kiến.

## 4. Thiếu validate input ở tầng message

1. Không kiểm tra kiểu dữ liệu, độ dài, định dạng.
2. Không giới hạn kích thước payload nhị phân/text.
3. Không chống replay/duplicate message.

Hệ quả: tăng nguy cơ injection, bypass nghiệp vụ, và DoS.

## 5. Quản lý session và authorization yếu trong kết nối dài hạn

1. Chỉ kiểm quyền khi mở socket, không kiểm ở từng hành động.
2. Session hết hạn nhưng socket không bị đóng.
3. Logout/role-change không vô hiệu hóa socket cũ.

Hệ quả: quyền truy cập cũ tồn tại lâu hơn chính sách dự kiến.

## Điều kiện cần để khai thác thành công

| Điều kiện                              | Ý nghĩa                                         | Thường gặp ở                                    |
| -------------------------------------- | ----------------------------------------------- | ----------------------------------------------- |
| Có endpoint WebSocket reachable        | Có điểm vào kỹ thuật để gửi/nhận message        | Ứng dụng chat, dashboard, trading, notification |
| Biết hoặc suy ra được format message   | Attacker tạo được payload hợp lệ ở mức protocol | JSON event API, Socket.IO event naming rõ ràng  |
| Thiếu authN/authZ phù hợp              | Message độc hại đi qua kiểm soát                | API real-time triển khai nhanh, thiếu hardening |
| Có side effect quan sát được           | Chứng minh impact (đọc/ghi/đổi trạng thái)      | Action nghiệp vụ, broadcast, phản hồi lỗi       |
| Không có rate-limit/monitoring đủ mạnh | Khai thác lặp lại hoặc tự động hóa              | Môi trường thiếu telemetry hoặc quota           |

## Mô hình điều kiện theo từng loại lỗ hổng

1. CSWSH:
   Yêu cầu cookie phiên có thể được gửi, origin check yếu, và handshake thiếu chống CSRF.

2. Injection qua message:
   Yêu cầu input qua WebSocket đi vào sink nguy hiểm mà thiếu sanitize/parameterization.

3. Authorization bypass:
   Yêu cầu endpoint tin rằng "đã connect thì được phép" và không kiểm quyền theo action.

4. Race condition:
   Yêu cầu thao tác cạnh tranh trên cùng tài nguyên, thiếu khóa hoặc kiểm tra idempotency.

5. DoS:
   Yêu cầu giới hạn tài nguyên, payload hoặc tốc độ không đầy đủ.

## Dấu hiệu kiến trúc dễ phát sinh lỗi

1. Team xem WebSocket như kênh “internal event bus” nên giảm kiểm soát đầu vào.
2. Logic auth nằm ở gateway, còn service xử lý message tin tưởng ngầm.
3. Không có tài liệu state machine chính thức cho protocol real-time.
4. Kiểm thử chỉ tập trung HTTP endpoint, bỏ qua message-level test.

## Tệp liên quan

- [Bề mặt tấn công và biên tin cậy](02-attack-surface-and-trust-boundaries.md)
- [Phát hiện và lập bản đồ mục tiêu](04-detection-and-target-mapping.md)
- [CSWSH](07-cross-site-websocket-hijacking-cswsh.md)
- [Phiên và authorization trong kênh stateful](08-session-authorization-and-stateful-risks.md)
