# DoS và cạn kiệt tài nguyên trong WebSocket

## Mục tiêu

Xác định các hướng tấn công từ chối dịch vụ đặc thù của kết nối WebSocket dài hạn và cách phòng thủ.

## Nhóm vector DoS thường gặp

## 1. Connection exhaustion

1. Mở số lượng lớn kết nối đồng thời.
2. Giữ kết nối idle để chiếm tài nguyên file descriptor/bộ nhớ.

## 2. Message flooding

1. Gửi nhiều message với tần suất cao.
2. Kích hoạt xử lý backend nặng qua action tốn CPU/IO.

## 3. Oversized payload và parsing abuse

1. Payload text/binary vượt ngưỡng an toàn.
2. Cấu trúc lồng sâu gây tốn CPU khi parse/validate.

## 4. Frame-level abuse

1. Frame bất thường về length/opcode gây lỗi parser.
2. Kịch bản "Ping of Death" kiểu khai báo độ dài cực lớn để kích thích cấp phát bộ nhớ.

## 5. Backpressure failure

1. Producer gửi nhanh hơn consumer xử lý.
2. Hàng đợi nội bộ phình to và dẫn đến OOM.

## Điều kiện khiến DoS dễ xảy ra

1. Không giới hạn kết nối theo user/IP/tenant.
2. Không giới hạn tốc độ message.
3. Không đặt `max payload` và timeout idle.
4. Thiếu cơ chế ping/pong health check và cleanup kết nối chết.

## Chỉ báo giám sát cần theo dõi

| Chỉ báo                        | Ý nghĩa                               |
| ------------------------------ | ------------------------------------- |
| Số kết nối mở tăng đột biến    | Dấu hiệu connection flood             |
| Độ trễ xử lý message tăng mạnh | Message flooding hoặc action nặng     |
| Memory queue tăng liên tục     | Backpressure không hiệu quả           |
| Tỷ lệ close code bất thường    | Có thể có frame abuse/protocol errors |

## Baseline hardening đề xuất

1. Giới hạn `max connections` toàn hệ thống và theo user.
2. Rate-limit theo action/message type.
3. Đặt `max payload` chặt chẽ theo nghiệp vụ.
4. Idle timeout + heartbeat để dọn kết nối chết.
5. Circuit breaker cho action nặng và hàng đợi.
6. Tách tài nguyên xử lý WebSocket khỏi luồng API quan trọng khác.

## Kiểm thử DoS an toàn trong lab

1. Bắt đầu ở mức tải thấp, tăng theo bậc.
2. Theo dõi tài nguyên theo thời gian thực và ngưỡng rollback.
3. Chỉ thực hiện trong môi trường được ủy quyền, không trên production.

## Tệp liên quan

- [Bề mặt tấn công và biên tin cậy](02-attack-surface-and-trust-boundaries.md)
- [Race condition trong luồng real-time](09-race-condition-in-realtime-flows.md)
- [Cheatsheet payload và kiểm thử](12-payloads-and-testing-cheatsheet.md)
- [Phòng thủ và giảm thiểu](13-defense-mitigation.md)
