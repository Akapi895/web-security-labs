# Tổng quan lỗ hổng WebSocket

## Định nghĩa

WebSocket là giao thức truyền thông full-duplex trên một kết nối TCP dài hạn, cho phép client và server gửi dữ liệu hai chiều theo thời gian thực sau khi hoàn tất bước handshake ban đầu qua HTTP.

Trong bảo mật ứng dụng web, WebSocket không chỉ là "HTTP nhanh hơn". Nó thay đổi mô hình tin cậy từ request-response ngắn hạn sang kênh stateful, liên tục, nên lỗi thiết kế về xác thực, phân quyền và kiểm soát dữ liệu thường có tác động rộng hơn.

## Vì sao WebSocket quan trọng trong pentest

| Khía cạnh               | Ý nghĩa bảo mật                                                          |
| ----------------------- | ------------------------------------------------------------------------ |
| Persistent connection   | Một sai sót ở thời điểm mở kết nối có thể duy trì quyền truy cập dài hạn |
| Bidirectional messaging | Dữ liệu độc hại có thể đi theo cả client -> server và server -> client   |
| Real-time workflow      | Lỗi race condition, state desync, replay thường rõ rệt hơn               |
| Giám sát                | Log HTTP truyền thống chỉ thấy handshake, bỏ lỡ phần lớn message         |

## WebSocket khác HTTP truyền thống như thế nào

| Tiêu chí               | HTTP truyền thống                       | WebSocket                                            |
| ---------------------- | --------------------------------------- | ---------------------------------------------------- |
| Mô hình kết nối        | Ngắn hạn, theo từng request             | Dài hạn, duy trì liên tục                            |
| Hướng truyền           | Chủ yếu client -> server                | Hai chiều đồng thời                                  |
| Trạng thái             | Dễ mô hình hóa theo request độc lập     | Stateful theo phiên/kết nối                          |
| Điểm kiểm soát bảo mật | Mỗi request có thể được kiểm tra đầy đủ | Thường kiểm tra mạnh ở handshake nhưng yếu ở message |
| Bề mặt tấn công        | URL, body, header                       | Handshake + schema message + state machine           |

## Nhóm lỗ hổng tiêu biểu

1. Lỗi ở handshake: thiếu xác thực, trust sai HTTP header, origin validation yếu.
2. Lỗi CSWSH: tái sử dụng cookie phiên khi mở kết nối chéo origin.
3. Lỗi xử lý message: thiếu validate input, parse không an toàn, injection đa lớp.
4. Lỗi authorization theo hành động: kiểm tra quyền lúc connect nhưng bỏ qua từng message.
5. Lỗi stateful logic: race condition, replay, desync trạng thái.
6. Lỗi vận hành: DoS do flood kết nối/message, payload lớn, frame bất thường.

## Vòng đời khai thác ở mức cao

```text
1. DISCOVER   -> Xác định endpoint WebSocket và luồng nghiệp vụ dùng real-time
2. MODEL      -> Mô hình hóa handshake, schema message, state transition
3. PROBE      -> Kiểm tra authN/authZ, origin, validate, rate-limit
4. ABUSE      -> Gửi message/handshake biến đổi để vượt kiểm soát
5. IMPACT     -> Chứng minh đọc/ghi trái phép, injection, chiếm phiên, DoS
6. HARDEN     -> Đề xuất kiểm soát theo nguyên nhân gốc
```

## Phạm vi sử dụng tài liệu

Bộ tài liệu này phục vụ:

1. Học tập kiến thức nền tảng WebSocket security.
2. Pentest có ủy quyền đối với hệ thống real-time.
3. Thiết kế lab thực hành và huấn luyện agent bảo mật.

## Tệp liên quan

- [Nền tảng giao thức và handshake](01-websocket-protocol-and-handshake.md)
- [Bề mặt tấn công và biên tin cậy](02-attack-surface-and-trust-boundaries.md)
- [Nguyên nhân gốc rễ và điều kiện khai thác](03-conditions-and-root-causes.md)
- [Phát hiện và lập bản đồ mục tiêu](04-detection-and-target-mapping.md)
- [Lỗ hổng xử lý message và injection](05-message-manipulation-and-injection.md)
- [Khai thác handshake và bypass xác thực](06-handshake-manipulation-and-auth-bypass.md)
- [Cross-Site WebSocket Hijacking (CSWSH)](07-cross-site-websocket-hijacking-cswsh.md)
- [Session, authorization và rủi ro stateful](08-session-authorization-and-stateful-risks.md)
- [Race condition trong luồng real-time](09-race-condition-in-realtime-flows.md)
- [DoS và cạn kiệt tài nguyên](10-denial-of-service-and-resource-exhaustion.md)
- [Workflow khai thác chuẩn hóa](11-exploitation-workflows.md)
- [Cheatsheet payload và kiểm thử](12-payloads-and-testing-cheatsheet.md)
- [Phòng thủ và giảm thiểu](13-defense-mitigation.md)
- [Kịch bản lab và huấn luyện agent](14-labs-and-agent-training-scenarios.md)
- [Ánh xạ tài liệu tham chiếu](15-reference-mapping.md)
