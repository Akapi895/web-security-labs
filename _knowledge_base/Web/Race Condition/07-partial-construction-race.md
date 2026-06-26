# Partial Construction Race Conditions

## Core Idea

Partial construction race xuất hiện khi hệ thống tạo object theo nhiều bước và để lộ trạng thái trung gian chưa hoàn chỉnh. Trong khoảng này, giá trị chưa khởi tạo (null/empty/default) có thể bị lợi dụng như một trạng thái hợp lệ.

## Typical Registration Anti-pattern

Quy trình đăng ký tách rời:

1. Tạo user record.
2. Sinh và lưu verification token.
3. Gửi email xác nhận.

Race window nằm giữa bước 1 và 2: user đã tồn tại nhưng token chưa được set.

## Exploit Primitive

Nếu endpoint confirm so sánh token với giá trị trong DB khi token còn uninitialized, attacker có thể thử biểu diễn null-equivalent để vượt qua.

Ví dụ tham số kiểu mảng rỗng trong một số framework:

- `token[]=`

Mục tiêu không phải payload cố định, mà là tìm biểu diễn dữ liệu mà backend quy đổi về giá trị tương đương null/empty trong phép so sánh.

## Practical Workflow

1. Dò endpoint xác nhận (qua JS, route, flow ứng dụng).
2. Thử phản ứng với token tùy ý, token thiếu, token rỗng, token kiểu mảng.
3. Benchmark thời gian: request confirm thường nhanh hơn register.
4. Dùng kỹ thuật đồng bộ để gửi 1 register + nhiều confirm gần đồng thời.
5. Quan sát response thành công bất thường của confirm.

## Why Multiple Confirm Requests

Vì race window rất ngắn và thứ tự xử lý không ổn định, gửi nhiều request confirm tăng xác suất có ít nhất một request rơi đúng thời điểm token chưa khởi tạo.

## Lab-oriented Success Criteria

- Có response xác nhận thành công cho user mới tạo mà không có token hợp lệ từ email.
- Đăng nhập được bằng tài khoản vừa tạo.
- Chứng minh hậu quả nghiệp vụ (ví dụ chiếm vai trò hoặc thao tác admin path).

## Defensive Direction

1. Tạo object và token trong cùng transaction.
2. Không cho phép trạng thái trung gian có thể truy cập từ endpoint bảo mật.
3. Xử lý kiểu dữ liệu đầu vào nghiêm ngặt, tránh coercion mơ hồ giữa null/array/string.

## Related Files

- [01-concurrency-and-timing-foundations](01-concurrency-and-timing-foundations.md)
- [10-tooling-burp-and-turbo-intruder](10-tooling-burp-and-turbo-intruder.md)
- [12-defense-mitigation](12-defense-mitigation.md)
