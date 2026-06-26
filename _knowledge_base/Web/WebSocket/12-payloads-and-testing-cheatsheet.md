# Cheatsheet payload và kiểm thử WebSocket

## Mục tiêu

Cung cấp mẫu kiểm thử có cấu trúc để phục vụ pentest có ủy quyền, nghiên cứu và xây dựng lab.

## Quy ước an toàn

1. Chỉ sử dụng trong môi trường hợp pháp và được cấp quyền.
2. Ưu tiên payload kiểm chứng an toàn trước khi thử biến thể mạnh hơn.
3. Ghi log đầy đủ để phục vụ phân tích và rollback.

## Mẫu message baseline

```json
{
  "action": "ping",
  "requestId": "test-001",
  "data": {
    "value": "hello"
  }
}
```

Mục tiêu: xác nhận đường đi cơ bản client -> server -> response.

## Nhóm mutation nên thử

## 1. Type mutation

1. Chuyển `string` thành `number`, `boolean`, `null`, object.
2. Chuyển trường số sang giá trị cực lớn/âm.

## 2. Structure mutation

1. Thiếu trường bắt buộc.
2. Thêm trường không công khai.
3. Lồng object sâu bất thường.

## 3. Control-field mutation

1. Thử `action` không hiển thị ở UI.
2. Thử kết hợp role thấp + action nhạy cảm.

## 4. Replay/sequence mutation

1. Gửi lại cùng `requestId` nhiều lần.
2. Gửi message sai thứ tự state.

## 5. Size/rate mutation

1. Payload sát ngưỡng kích thước tối đa.
2. Burst nhiều message trong thời gian ngắn.

## Khung kiểm thử handshake

| Thành phần    | Biến đổi thử nghiệm                        |
| ------------- | ------------------------------------------ |
| Origin        | origin hợp lệ, origin lạ, origin gần giống |
| Cookie/token  | thiếu, sai, hết hạn, thu hồi               |
| Subprotocol   | đúng, thiếu, giá trị lạ                    |
| Header custom | có/không, giá trị giả mạo                  |

## Gợi ý công cụ

1. Burp WebSockets: intercept, repeater, clone handshake.
2. `websocat`: gửi message thô và quan sát phản hồi.
3. `wsrepl`: tương tác và tự động hóa plugin theo protocol.
4. `ws-harness.py`: bridge WebSocket sang HTTP để tích hợp công cụ HTTP-based.

Ví dụ command kiểm thử cơ bản:

```bash
websocat --insecure wss://target.example/ws -v
```

```powershell
python ws-harness.py -u "ws://target.example/ws" -m ./message.txt
```

## Mẫu biểu ghi nhận kết quả

```text
Test ID: WS-AUTHZ-003
Precondition: user role = standard
Mutation: action = admin.deleteUser
Observed: server returned success
Impact: vertical privilege escalation
Evidence: websocket transcript + state change in target account
```

## Tệp liên quan

- [Phát hiện và lập bản đồ mục tiêu](04-detection-and-target-mapping.md)
- [Lỗ hổng xử lý message](05-message-manipulation-and-injection.md)
- [Workflow khai thác](11-exploitation-workflows.md)
- [Phòng thủ và giảm thiểu](13-defense-mitigation.md)
