# Bề mặt tấn công và biên tin cậy của WebSocket

## Mục tiêu

Xác định đầy đủ các điểm có thể bị lạm dụng trong vòng đời WebSocket, từ handshake đến xử lý message real-time.

## Biên tin cậy điển hình

1. Trình duyệt và JavaScript runtime của người dùng.
2. Edge layer: CDN, reverse proxy, load balancer, WAF.
3. WebSocket gateway hoặc endpoint ứng dụng.
4. Dịch vụ backend mà endpoint gọi đến (DB, cache, queue, RPC).
5. Client khác nhận broadcast qua cùng kênh real-time.

Mỗi biên tin cậy là một nơi có thể phát sinh sai lệch kiểm soát: xác thực, phân quyền, validate dữ liệu, hoặc giới hạn tài nguyên.

## Bề mặt tấn công theo lớp

### 1. Lớp handshake

1. Endpoint WebSocket bị lộ và không yêu cầu auth rõ ràng.
2. Trust sai các header như `X-Forwarded-For`, `Origin`, `Host`.
3. Cho phép subprotocol hoặc extension không được kiểm soát.
4. Chấp nhận cross-origin quá rộng hoặc wildcard.

### 2. Lớp message protocol

1. Schema message không chặt (thiếu type, thiếu required field, thiếu giới hạn kích thước).
2. Dispatcher theo `action/event` cho phép gọi chức năng nhạy cảm không kiểm quyền.
3. Parse nhị phân hoặc deserialize không an toàn.
4. Thiếu chống replay, thiếu kiểm tra thứ tự trạng thái.

### 3. Lớp stateful workflow

1. Quyền được “gán một lần” khi connect, không re-check ở từng hành động.
2. Session hết hạn nhưng socket vẫn hoạt động.
3. Logout không đóng các socket đang mở.
4. Race condition khi nhiều kết nối cùng thao tác trên một tài nguyên.

### 4. Lớp hạ tầng và vận hành

1. Không giới hạn số kết nối, tốc độ message, kích thước payload.
2. Backpressure yếu dẫn tới cạn bộ nhớ.
3. Proxy xử lý Upgrade không nhất quán, có nguy cơ WebSocket smuggling.
4. Monitoring thiếu chiều sâu: chỉ log handshake, không log hành vi message.

## Ma trận năng lực attacker theo bối cảnh

| Bối cảnh                         | Năng lực thường có                               | Tác động tiềm năng                                   |
| -------------------------------- | ------------------------------------------------ | ---------------------------------------------------- |
| Unauthenticated Internet user    | Mở kết nối, fuzz message công khai               | Rò rỉ dữ liệu công khai, DoS, enum chức năng         |
| Authenticated low-privilege user | Dùng phiên thật để thử vượt quyền                | Horizontal/vertical privilege escalation             |
| Cross-site attacker              | Mở socket từ trang độc hại bằng cookie nạn nhân  | CSWSH, thao tác trái phép, đọc dữ liệu phiên         |
| Nội bộ hoặc localhost abuse      | Tương tác dịch vụ local/intranet qua trình duyệt | Lạm dụng IPC helper, mở rộng ảnh hưởng ngoài web app |

## Dấu hiệu ưu tiên khi rà soát

1. Có endpoint `ws://` hoặc `wss://` nhưng không có chính sách origin rõ ràng.
2. Chức năng nghiệp vụ nhạy cảm đi qua message nhưng không có kiểm quyền theo action.
3. Message format “linh hoạt quá mức” (dynamic field, free-form command).
4. Nhiều sự kiện bất thường trong real-time nhưng log không truy vết được.

## Tệp liên quan

- [Nền tảng giao thức và handshake](01-websocket-protocol-and-handshake.md)
- [Phát hiện và lập bản đồ mục tiêu](04-detection-and-target-mapping.md)
- [Lỗ hổng xử lý message](05-message-manipulation-and-injection.md)
- [DoS và cạn kiệt tài nguyên](10-denial-of-service-and-resource-exhaustion.md)
