# Session, authorization và rủi ro stateful

## Mục tiêu

Giải thích vì sao kết nối WebSocket dài hạn làm bài toán phiên và phân quyền khó hơn HTTP truyền thống.

## Vấn đề cốt lõi

Nhiều hệ thống kiểm tra quyền tại thời điểm connect, sau đó mặc định mọi message là hợp lệ. Đây là nguyên nhân trực tiếp của nhiều lỗi bypass authorization.

## Rủi ro chính trong kết nối dài hạn

## 1. Session lifetime lệch với socket lifetime

1. Session HTTP đã hết hạn nhưng socket chưa bị đóng.
2. Token bị thu hồi nhưng kết nối cũ vẫn dùng được.

## 2. Authorization chỉ kiểm tra một lần

1. User low-privilege gọi action nhạy cảm do thiếu check theo message.
2. Thay đổi role ở backend nhưng socket không cập nhật quyền.

## 3. Replay và duplicate action

1. Message cũ bị gửi lại trong ngữ cảnh mới.
2. Action không idempotent gây giao dịch trùng hoặc sai trạng thái.

## 4. State desynchronization

1. Nhiều tab/kết nối cùng user tạo trạng thái cạnh tranh.
2. Server và client bất đồng thứ tự sự kiện.

## Yêu cầu thiết kế authorization đúng

1. Xác thực khi handshake.
2. Kiểm quyền ở từng message/action.
3. Kiểm tra điều kiện state machine trước khi thực thi.
4. Gắn message với tenant/resource ownership cụ thể.

## Checklist kiểm thử authorization message-level

| Câu hỏi                                                             | Kỳ vọng an toàn                                |
| ------------------------------------------------------------------- | ---------------------------------------------- |
| User thường gọi action admin có bị chặn không?                      | Chặn và ghi log sự kiện                        |
| User A truy vấn dữ liệu của user B qua ID sửa tay có bị chặn không? | Chặn theo ownership check                      |
| Sau logout/expire, socket cũ còn gửi action được không?             | Socket bị đóng hoặc từ chối hành động          |
| Message gửi lại (replay) có hiệu lực không?                         | Bị từ chối bởi nonce/timestamp/idempotency key |

## Mẫu kiểm soát phiên khuyến nghị

1. Session re-validation định kỳ cho socket đang mở.
2. Mapping session -> danh sách socket để revoke tức thời khi logout.
3. Rotation token cho kết nối dài hạn.
4. Audit log theo `connection_id`, `user_id`, `action`, `decision`.

## Dấu hiệu kiến trúc cần ưu tiên hardening

1. Action handler không nhận context quyền mà chỉ nhận payload.
2. Không có khái niệm transaction/idempotency cho message có side effect.
3. Không thể truy vết action nào đến từ kết nối nào.

## Tệp liên quan

- [Nguyên nhân gốc rễ và điều kiện khai thác](03-conditions-and-root-causes.md)
- [Lỗ hổng xử lý message](05-message-manipulation-and-injection.md)
- [Race condition trong luồng real-time](09-race-condition-in-realtime-flows.md)
- [Phòng thủ và giảm thiểu](13-defense-mitigation.md)
