# Ánh xạ tài liệu tham chiếu (WebSocket)

## Mục tiêu

Liên kết từng chương trong bộ knowledge base WebSocket với nguồn gốc trong thư mục `reference/` để hỗ trợ truy vết và bảo trì.

## Danh sách nguồn gốc đã sử dụng

1. `reference/hacktricks.txt`
2. `reference/OWASP.TXT`
3. `reference/PayloadsAllTheThings.md`
4. `reference/portswigger.txt`
5. `reference/ws-harness.py`

## Bản đồ chương -> nguồn

| Chương                                       | Trọng tâm                                           | Nguồn tham chiếu chính                          |
| -------------------------------------------- | --------------------------------------------------- | ----------------------------------------------- |
| 00-overview                                  | Khái niệm, khác biệt WS vs HTTP, nhóm rủi ro        | HackTricks, OWASP, PortSwigger                  |
| 01-websocket-protocol-and-handshake          | Cơ chế handshake, frame, stateful communication     | HackTricks, PayloadsAllTheThings                |
| 02-attack-surface-and-trust-boundaries       | Attack surface từ handshake đến backend             | HackTricks, OWASP, PortSwigger                  |
| 03-conditions-and-root-causes                | Nguyên nhân gốc rễ và điều kiện khai thác           | OWASP, HackTricks, PortSwigger                  |
| 04-detection-and-target-mapping              | Quy trình phát hiện và lập bản đồ mục tiêu          | PortSwigger, HackTricks                         |
| 05-message-manipulation-and-injection        | Tampering message, injection, prototype pollution   | PortSwigger, OWASP, HackTricks                  |
| 06-handshake-manipulation-and-auth-bypass    | Lỗi thiết kế handshake, trust sai header            | PortSwigger, HackTricks                         |
| 07-cross-site-websocket-hijacking-cswsh      | CSWSH, điều kiện, biến thể và phòng thủ             | OWASP, HackTricks, PortSwigger                  |
| 08-session-authorization-and-stateful-risks  | Session expiration, message-level authZ             | OWASP, PortSwigger                              |
| 09-race-condition-in-realtime-flows          | Race trong luồng real-time stateful                 | HackTricks                                      |
| 10-denial-of-service-and-resource-exhaustion | Connection/message flood, frame abuse, backpressure | OWASP, HackTricks                               |
| 11-exploitation-workflows                    | Chuẩn hóa quy trình khai thác                       | Tổng hợp từ toàn bộ nguồn                       |
| 12-payloads-and-testing-cheatsheet           | Mutation strategy, tooling, harness                 | PayloadsAllTheThings, HackTricks, ws-harness.py |
| 13-defense-mitigation                        | Kiểm soát đa lớp và hardening                       | OWASP, PortSwigger                              |
| 14-labs-and-agent-training-scenarios         | Kịch bản đào tạo và rubric                          | Tổng hợp từ toàn bộ nguồn                       |

## Ánh xạ điểm tri thức đặc biệt

1. CSWSH và origin validation: nhấn mạnh từ OWASP + PortSwigger + HackTricks.
2. Handshake manipulation và trust-in-header flaws: trọng tâm từ PortSwigger.
3. Tooling thực hành (`websocat`, `wsrepl`, `ws-harness.py`): từ HackTricks và PayloadsAllTheThings.
4. Race/DoS trong kênh dài hạn: từ HackTricks và khuyến nghị hardening của OWASP.

## Hướng dẫn bảo trì mapping

1. Mỗi khi thêm chương mới, cập nhật bảng ánh xạ ngay.
2. Nếu chỉnh sửa nội dung trọng yếu, ghi chú lại nguồn bổ sung tương ứng.
3. Ưu tiên nguồn có nội dung kỹ thuật kiểm chứng được trong lab.

## Tệp liên quan

- [Tổng quan](00-overview.md)
- [Workflow khai thác](11-exploitation-workflows.md)
- [Phòng thủ và giảm thiểu](13-defense-mitigation.md)
- [Kịch bản lab và huấn luyện agent](14-labs-and-agent-training-scenarios.md)
