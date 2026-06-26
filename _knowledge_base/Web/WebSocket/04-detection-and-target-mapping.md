# Phát hiện và lập bản đồ mục tiêu WebSocket

## Mục tiêu

Biến quá trình "thấy có WebSocket" thành bản đồ kiểm thử có thể lặp lại: endpoint, handshake, schema message, và hành động nhạy cảm.

## Quy trình phát hiện chuẩn

## 1. Xác định vị trí sử dụng WebSocket

1. Quan sát trình duyệt (DevTools Network) để tìm request `Upgrade: websocket`.
2. Dùng proxy (ví dụ Burp) để thu lịch sử message hai chiều.
3. Ghi nhận module nghiệp vụ nào đang dùng real-time (chat, thông báo, quản trị, giao dịch).

## 2. Thu thập handshake và ngữ cảnh phiên

Checklist tối thiểu:

1. URL endpoint, tham số query, subprotocol.
2. Header: `Origin`, `Cookie`, `Authorization`, custom header.
3. Cơ chế auth được dùng thực tế (cookie-only, bearer token, kết hợp).
4. Kết quả khi thiếu/sai từng thành phần auth.

Mẫu ghi nhận:

```text
Endpoint: wss://target/ws
Auth source: Cookie session
Origin enforced: unknown
Subprotocol: json.v2
Handshake result when no cookie: accepted/rejected
```

## 3. Mô hình hóa message protocol

1. Thu message mẫu theo từng chức năng người dùng.
2. Tách trường điều khiển (`action`, `event`, `type`) khỏi dữ liệu nghiệp vụ.
3. Xác định ràng buộc: bắt buộc/trùy chọn, kiểu dữ liệu, range, enum.
4. Ghi nhận sequencing (thứ tự message hợp lệ theo state).

## 4. Lập bản đồ authZ theo hành động

1. Liệt kê action theo vai trò (guest/user/admin).
2. Kiểm tra từng action có kiểm quyền riêng hay không.
3. Xác định hành động có side effect cao: thay đổi dữ liệu, thao tác tài chính, điều khiển tác vụ.

## 5. Kiểm tra xử lý lỗi và quan sát side effect

1. Đưa dữ liệu sai kiểu/sai cấu trúc để xem behavior.
2. Kiểm tra phản hồi lỗi có lộ thông tin nội bộ không.
3. Theo dõi side effect ngoài kênh WebSocket (DB, UI, log, queue, email).

## 6. Ưu tiên mục tiêu khai thác

Ưu tiên cao nếu có đồng thời các dấu hiệu:

1. Endpoint chấp nhận kết nối chéo origin.
2. Action nhạy cảm không kiểm quyền message-level.
3. Input đi vào sink nguy hiểm.
4. Không có rate-limit hoặc quota.

## Ma trận kiểm thử phát hiện

| Nhóm kiểm thử     | Câu hỏi chính                                | Bằng chứng cần có                    |
| ----------------- | -------------------------------------------- | ------------------------------------ |
| Handshake auth    | Không có token/cookie thì sao?               | Response 101 hay reject + reason     |
| Origin policy     | Origin lạ có bị từ chối?                     | Kết quả theo từng origin thử nghiệm  |
| Message schema    | Payload lệch kiểu có bị chặn?                | Validation error hoặc xử lý sai      |
| Authorization     | User thấp quyền gọi action admin được không? | Response + side effect               |
| Session lifecycle | Session hết hạn nhưng socket còn sống?       | Bằng chứng sau timeout/logout        |
| DoS baseline      | Flood nhẹ có bị kiểm soát?                   | Số message/kết nối trước khi bị chặn |

## Output chuẩn cho báo cáo pentest

1. Danh sách endpoint WebSocket đã xác nhận.
2. Bản đồ action và quyền tương ứng.
3. Các điểm kiểm soát thiếu hoặc sai.
4. Chuỗi tái hiện lỗ hổng (precondition -> thao tác -> impact).
5. Khuyến nghị hardening theo ưu tiên.

## Tệp liên quan

- [Nguyên nhân gốc rễ và điều kiện khai thác](03-conditions-and-root-causes.md)
- [Lỗ hổng xử lý message](05-message-manipulation-and-injection.md)
- [Lỗi handshake và auth bypass](06-handshake-manipulation-and-auth-bypass.md)
- [Workflow khai thác chuẩn hóa](11-exploitation-workflows.md)
