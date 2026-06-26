# Defense and Mitigation

## Security Objective

Mục tiêu phòng thủ race condition là đảm bảo mọi thao tác nhạy cảm giữ được invariant nghiệp vụ ngay cả khi có nhiều request đồng thời.

## 1. Make Sensitive State Changes Atomic

Nguyên tắc:

- Check và update phải nằm trong cùng transaction/atomic operation.
- Không tách rule bảo mật thành nhiều thao tác độc lập.

Ví dụ cần atomic:

- Validate payment amount + confirm order.
- Verify one-time token + mark token used.
- Check quota + increment counter.

## 2. Use Correct Locking Strategy

| Strategy                      | Use Case                                    | Caveat                                |
| ----------------------------- | ------------------------------------------- | ------------------------------------- |
| Pessimistic lock              | Tài nguyên giá trị cao, ghi cạnh tranh mạnh | Có thể giảm throughput                |
| Optimistic lock (version/CAS) | Khối lượng lớn, xung đột vừa phải           | Cần retry logic đúng                  |
| Distributed lock              | Nhiều node/service                          | Tránh lock giả do timeout/split brain |

Quan trọng: lock phải theo đúng resource key bảo mật (user/account/order), không chỉ theo session local.

## 3. Enforce Datastore Integrity Constraints

Các ràng buộc DB là lớp phòng thủ rất mạnh:

- Unique constraints.
- Check constraints.
- Foreign key + status transition constraints.

Constraint không thay thế logic đúng, nhưng giúp chặn nhiều trạng thái sai khi race xảy ra.

## 4. Idempotency and Replay Safety

Với hành động có thể retry:

- Dùng idempotency key.
- Lưu kết quả theo key và trả lại cùng kết quả cho replay.
- Không thực thi side effect nhiều lần cho cùng business action.

## 5. Session and State Consistency

- Không cập nhật biến session bảo mật theo kiểu rời rạc dễ trộn state.
- Tránh dùng session như cơ chế duy nhất để bảo vệ rule nằm ở database.
- Nếu cần nhiều biến trạng thái, cập nhật theo batch nhất quán.

## 6. Secure Token Lifecycle

1. Sinh token bằng CSPRNG.
2. Bind token theo user/context/action.
3. TTL ngắn và one-time use.
4. Consume token atomically (verify + invalidate trong một bước).

## 7. Design for Async Side Effects

Khi dùng email/queue/webhook:

- Snapshot dữ liệu cần gửi tại thời điểm commit thành công.
- Worker chỉ dùng snapshot, tránh đọc lại state mutable không khóa.
- Ghi correlation ID để truy vết mismatch.

## 8. Preventive Testing in SDLC

1. Unit/integration tests cho concurrency edge cases.
2. Security tests gửi song song cho endpoint nhạy cảm.
3. Chaos/timing tests cho distributed workflows.
4. Code review bắt buộc với luồng check-then-update.

## 9. Anti-patterns to Eliminate

- "Chỉ cần rate limit là đủ".
- "Session lock sẽ bảo vệ DB rule".
- "ORM tự xử lý transaction nên không cần quan tâm".
- "Token có timestamp là đủ ngẫu nhiên".

## 10. Mitigation Mapping

| Vulnerability Pattern        | Primary Fix                                                  |
| ---------------------------- | ------------------------------------------------------------ |
| Limit overrun TOCTOU         | Atomic check+update, DB transaction/lock                     |
| Multi-endpoint race          | Transaction boundary xuyên flow, invariant checks tại commit |
| Single-endpoint state mix-up | Consistent state model, snapshot side effects                |
| Partial construction         | Không để lộ object ở trạng thái chưa hoàn thiện              |
| Time-sensitive token flaw    | CSPRNG + context-bound token                                 |

## Related Files

- [02-root-causes](02-root-causes.md)
- [11-lab-design-and-training](11-lab-design-and-training.md)
- [13-testing-and-review-checklists](13-testing-and-review-checklists.md)
