# Lỗ hổng xử lý message và injection qua WebSocket

## Mục tiêu

Phân tích cách dữ liệu độc hại đi qua kênh WebSocket và trở thành lỗ hổng thực thi ở server hoặc client.

## Nguyên tắc cốt lõi

Mọi message WebSocket đều là dữ liệu không tin cậy, kể cả khi socket đã được mở từ một phiên đăng nhập hợp lệ.

## Các kiểu injection thường gặp

| Kiểu lỗ hổng                         | Đường đi phổ biến qua WebSocket                         | Tác động                                          |
| ------------------------------------ | ------------------------------------------------------- | ------------------------------------------------- |
| XSS                                  | Message chat/notification được render HTML không encode | Chiếm phiên, thực thi script phía client          |
| SQLi/NoSQLi                          | Trường tìm kiếm/lọc/sắp xếp chuyển thẳng vào query      | Rò rỉ/ghi sửa dữ liệu                             |
| Command Injection                    | Message điều khiển task/backend job thiếu sanitize      | Thực thi lệnh trái phép                           |
| XXE/deserialization                  | Payload XML/binary parse không an toàn                  | Đọc file nội bộ, SSRF, RCE tùy ngữ cảnh           |
| Prototype pollution (Node/Socket.IO) | Object merge không kiểm soát với key đặc biệt           | Biến đổi hành vi ứng dụng, mở đường chain lỗ hổng |

## Chuỗi kỹ thuật dẫn đến lỗ hổng

1. Attacker gửi message có cấu trúc hợp lệ ở tầng protocol.
2. Server parse và route message theo `action/event`.
3. Input đi vào sink nguy hiểm mà thiếu validate/sanitize.
4. Kết quả phản hồi hoặc side effect xác nhận khai thác thành công.

## Điểm yếu triển khai phổ biến

1. Chỉ kiểm tra schema ở client, server tin tưởng dữ liệu nhận được.
2. Dùng chuỗi động để tạo query/command từ trường message.
3. Chưa encode output trước khi broadcast cho client khác.
4. Cho phép object key tùy ý khi merge payload vào cấu hình nội bộ.

## Phương pháp kiểm thử message tampering

1. Thu message hợp lệ từ luồng nghiệp vụ thật.
2. Biến đổi từng trường theo chiến lược: kiểu dữ liệu, độ dài, ký tự đặc biệt, cấu trúc lồng.
3. Quan sát phản hồi trực tiếp và side effect gián tiếp.
4. Lặp lại theo từng state để phát hiện bug chỉ xuất hiện ở điều kiện cụ thể.

## Mẫu hướng kiểm thử theo trường

| Loại trường      | Biến đổi nên thử                          | Mục tiêu quan sát               |
| ---------------- | ----------------------------------------- | ------------------------------- |
| `id` số          | âm, rất lớn, chuỗi, null                  | ép kiểu, lỗi logic phân quyền   |
| `action`         | action không công khai                    | bypass dispatcher/authorization |
| `filters/search` | ký tự điều khiển, wildcard, biểu thức     | query injection hoặc lỗi parser |
| `html/text`      | nội dung có markup/script                 | reflected/stored XSS            |
| object metadata  | key bất thường (`__proto__`, nested deep) | pollution, crash, xử lý sai     |

## Blind vulnerabilities và OAST

Nhiều lỗ hổng qua WebSocket không phản hồi trực tiếp trên socket. Cần theo dõi tín hiệu out-of-band:

1. DNS/HTTP callback.
2. Log backend.
3. Thay đổi trạng thái dữ liệu ở thành phần khác.

## Điều kiện để khai thác thành công

1. Message parser chấp nhận payload attacker-controlled.
2. Input đi vào sink nhạy cảm.
3. Không có lớp validate/escape/parameterization phù hợp.
4. Có đường quan sát impact.

## Khuyến nghị thiết kế an toàn

1. Validate schema phía server bằng allowlist chặt chẽ.
2. Tách rõ control field và data field; kiểm quyền theo action.
3. Dùng API an toàn cho query/command (parameterized query, không eval).
4. Encode output khi trả về client và trước khi render.
5. Chặn key nguy hiểm trong object merge và giới hạn độ sâu cấu trúc.

## Tệp liên quan

- [Phát hiện và lập bản đồ mục tiêu](04-detection-and-target-mapping.md)
- [Lỗi handshake và auth bypass](06-handshake-manipulation-and-auth-bypass.md)
- [Phiên và authorization trong kênh stateful](08-session-authorization-and-stateful-risks.md)
- [Cheatsheet payload và kiểm thử](12-payloads-and-testing-cheatsheet.md)
