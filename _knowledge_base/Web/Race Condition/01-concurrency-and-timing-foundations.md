# Concurrency and Timing Foundations

## Execution Model in Web Applications

Một web request nhìn bề ngoài là một thao tác đơn, nhưng phía server thường gồm nhiều bước:

1. Nhận request và parse dữ liệu.
2. Đọc state hiện tại (session, DB, cache).
3. Kiểm tra điều kiện (authorization, limit, token, số dư).
4. Cập nhật state.
5. Kích hoạt side effects (gửi email, publish queue, log, webhook).

Khi nhiều request chạy đồng thời, các bước trên có thể xen kẽ, tạo ra kết quả không còn giống thiết kế tuyến tính.

## Shared Resource and Consistency Boundary

Race condition chỉ có ý nghĩa khi tồn tại shared resource:

- Bản ghi người dùng (email pending, reset token, role).
- Bản ghi tài chính (balance, ledger, transaction state).
- Trạng thái mua hàng (cart total, coupon usage, order state).
- Bộ đếm phòng thủ (failed login count, rate-limit quota).

Điều quan trọng không phải chỉ là "cùng endpoint" mà là "cùng key dữ liệu". Ví dụ:

- Cùng username.
- Cùng session ID.
- Cùng order ID hoặc account ID.

## Critical Section and Atomicity

Critical section là đoạn logic cần thực thi như một khối nguyên tử. Ví dụ luồng coupon:

1. Check coupon chưa dùng.
2. Áp dụng giảm giá.
3. Mark coupon đã dùng.

Nếu 3 bước không atomic, request song song có thể đều vượt qua bước 1 trước khi bước 3 của request đầu hoàn tất.

## Race Window and Hidden Sub-state

Race window là khoảng thời gian giữa hai thao tác mà trạng thái tạm thời có thể bị can thiệp.

Ví dụ sub-state trong luồng login + MFA:

1. Server gán session đăng nhập.
2. Chưa bật enforce MFA.
3. Sau đó mới bật enforce MFA.

Ở bước 2, user tạm thời có session hợp lệ nhưng chưa bị ràng buộc MFA. Đây là hidden sub-state có thể khai thác nếu gửi request nhạy cảm đúng thời điểm.

## Order Dependency

Nhiều lỗi race không cần "phá" cơ chế check, mà chỉ cần ép thứ tự thực thi theo hướng có lợi:

- Request A validate trước, request B ghi đè state sau.
- Request B đọc state cũ trước khi request A commit state mới.

Do đó, cùng một nhóm request nhưng thứ tự xử lý khác nhau sẽ tạo kết quả khác nhau.

## Concurrency Across Architectures

### Multi-thread

Nhiều luồng trong cùng process cùng truy cập bộ nhớ và DB. Lỗi thường do lock không đầy đủ.

### Multi-process

Nhiều worker process xử lý song song; lock in-memory không còn hiệu lực toàn cục.

### Distributed System

Nhiều service và datastore khác nhau (DB, cache, queue) với độ trễ và consistency khác nhau. Lỗi dễ xuất hiện ở ranh giới service-to-service.

## Practical Mental Model

Khi đánh giá một endpoint, đặt câu hỏi:

1. Endpoint này đọc gì?
2. Endpoint này ghi gì?
3. Có side effect nào chạy async không?
4. Các bước đó có cùng transaction/lock không?
5. Nếu 2 request vào cùng lúc, điểm nào có thể giao thoa?

Nếu trả lời được 5 câu hỏi này, bạn đã có bản đồ để tìm race window.

## Related Files

- [00-overview](00-overview.md)
- [02-root-causes](02-root-causes.md)
- [03-detection-and-scoping](03-detection-and-scoping.md)
- [09-exploitation-workflows](09-exploitation-workflows.md)
