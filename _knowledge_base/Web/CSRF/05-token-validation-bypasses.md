# Bypassing CSRF Token Validation

## Vai trò của token trong mô hình phòng thủ

CSRF token chỉ hiệu quả khi đạt đủ ba tính chất:

1. Unique cho phiên hoặc request.
2. Secret, attacker không đoán hoặc ép đặt được.
3. Server-side validation chặt và fail-closed.

Thiếu một trong ba, token có thể bị bypass.

## Nhóm lỗi phổ biến trong validation token

## 1. Validation phụ thuộc method

Mô tả:

- Token chỉ được kiểm tra với POST.
- GET/HEAD hoặc route qua method override bị bỏ qua.

Hệ quả:

- Attacker chuyển request sang method không bị kiểm tra và bỏ token.

## 2. Validation phụ thuộc token có xuất hiện hay không

Mô tả:

- Nếu token có mặt thì validate.
- Nếu thiếu hẳn token parameter thì cho qua.

Hệ quả:

- Chỉ cần xóa hẳn tham số token khỏi request forged.

## 3. Chấp nhận token rỗng hoặc validate hình thức

Mô tả:

- Server chỉ check tồn tại key, không check giá trị thực.
- `csrf=` hoặc chuỗi sai format vẫn được chấp nhận.

## 4. Token không ràng buộc session user

Mô tả:

- App giữ global pool token hoặc check token độc lập session.

Hệ quả:

- Attacker lấy token hợp lệ từ tài khoản của họ, gắn vào request gửi nạn nhân.

## 5. Token gắn với non-session cookie

Mô tả:

- Token gắn với cookie riêng không đồng bộ session cookie.

Hệ quả:

- Nếu attacker có điểm đặt cookie cho nạn nhân (cookie injection), có thể đồng bộ token/cookie theo ý attacker.

## 6. Double-submit triển khai sai

Mô tả:

- Server chỉ so sánh token ở cookie và request param (đều có thể do client kiểm soát).
- Không có chữ ký server-side hoặc binding với session.

Hệ quả:

- Attacker tự chọn token, đặt cookie tương ứng, gửi request chứa cùng token.

## 7. Token predictable hoặc reuse quá lâu

Mô tả:

- Token sinh theo timestamp yếu, ID tuần tự, hoặc không rotate hợp lý.

Hệ quả:

- Tăng khả năng đoán token hoặc tái sử dụng token cũ.

## Quy trình test token validation

## Ma trận kiểm thử

| Test case            | Kỳ vọng nếu an toàn | Dấu hiệu lỗi           |
| -------------------- | ------------------- | ---------------------- |
| Token đúng           | Thành công          | -                      |
| Token sai ngẫu nhiên | Bị chặn             | Vẫn thành công         |
| Token bị xóa hẳn     | Bị chặn             | Thành công             |
| Token rỗng           | Bị chặn             | Thành công             |
| Token của phiên khác | Bị chặn             | Thành công             |
| Method thay đổi      | Bị chặn hoặc 405    | Thành công không token |

## Khung suy luận root cause

```text
Nếu request forged thành công
  -> Token có được kiểm tra không?
  -> Kiểm tra trên route/method nào?
  -> Token có ràng buộc session/action không?
  -> Có thành phần client-controlled nào quyết định pass/fail?
```

## Ví dụ luồng bypass điển hình

## Luồng A: Omit-token bypass

1. Bắt request hợp lệ có `csrf=...`.
2. Xóa toàn bộ tham số `csrf`.
3. Gửi lại request trong context nạn nhân.
4. Nếu action vẫn thành công -> token-present flaw.

## Luồng B: Session-unbound token bypass

1. Attacker đăng nhập account của chính họ.
2. Lấy token hợp lệ.
3. Nhúng token đó vào PoC gửi cho nạn nhân.
4. Nếu action thành công với session victim -> token không bind session.

## Luồng C: Double-submit weak design

1. Quan sát server chỉ so sánh token cookie == token param.
2. Tận dụng điểm set-cookie để đặt token attacker vào browser victim.
3. Gửi request với token trùng giá trị đó.
4. Nếu pass -> double-submit không có integrity binding.

## Khuyến nghị khắc phục theo từng lỗi

| Lỗi                    | Khắc phục                                                           |
| ---------------------- | ------------------------------------------------------------------- |
| Method-dependent check | Validate token trên mọi action state-changing theo effective method |
| Token optional         | Thiết kế bắt buộc token, thiếu token phải fail                      |
| Empty token accepted   | So sánh giá trị chặt, reject null/empty/invalid format              |
| Unbound token          | Bind token với session + user + action context                      |
| Weak double-submit     | Dùng token có chữ ký HMAC server-side và ràng buộc session          |

## Related Files

- [Root Causes and Conditions](02-root-causes-and-conditions.md)
- [Exploitation Workflow](04-exploitation-workflow.md)
- [Origin Referer and Request Shape Bypass](07-origin-referer-and-request-shape-bypass.md)
- [Defense and Mitigation](10-defense-mitigation.md)
