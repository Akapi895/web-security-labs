# Single-endpoint Race Conditions

## Core Idea

Single-endpoint race xảy ra khi cùng một endpoint được gọi song song với input khác nhau, khiến state nội bộ bị trộn hoặc ghi đè ngoài mong đợi.

Điểm quan trọng: cùng endpoint không đồng nghĩa cùng logic kết quả. Input khác nhau có thể chạm cùng biến trạng thái theo thứ tự bất định.

## Typical Targets

- Đổi email tài khoản.
- Tạo reset token theo username.
- Cập nhật profile kèm gửi xác nhận qua email.

## Canonical Collision Example

Hai request `POST /change-email` cùng session:

1. Request A đặt email = attacker mailbox.
2. Request B đặt email = victim/admin-pending mailbox.
3. Worker gửi email đọc dữ liệu ở thời điểm không đồng bộ.
4. Email xác nhận có thể gửi sai người nhận hoặc chứa dữ liệu lệch.

## Session-based Keying

Nhiều chức năng account management được key theo session/user. Vì vậy:

- Cùng endpoint + cùng session thường có collision mạnh.
- Nếu framework lock theo session, cần đa session để kiểm chứng.

## Exploitation Workflow

1. Thu thập endpoint có hành vi "replace" thay vì "append".
2. Gửi tuần tự nhiều giá trị để hiểu cơ chế pending state.
3. Gửi song song nhiều giá trị khác nhau.
4. Quan sát mismatch giữa request input và email/response side effect.
5. Thu hẹp còn 2 request tối thiểu để chiếm state mục tiêu.

## Observable Clues

- Confirmation email recipient/body không khớp.
- Token hợp lệ cho giá trị không thuộc request tạo token ban đầu.
- Account state sau cùng là giá trị không phải "last expected write" theo logic bình thường.

## Risk

| Area              | Potential Impact                            |
| ----------------- | ------------------------------------------- |
| Account Ownership | Chiếm email, chiếm account                  |
| Privilege         | Kế thừa quyền admin từ email pending invite |
| Recovery Flow     | Đặt lại mật khẩu trái phép                  |

## Related Files

- [03-detection-and-scoping](03-detection-and-scoping.md)
- [08-time-sensitive-attacks](08-time-sensitive-attacks.md)
- [12-defense-mitigation](12-defense-mitigation.md)
