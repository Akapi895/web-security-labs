# Root Causes of Race Condition Vulnerabilities

## 1. Logic Design Flaws

Đây là nhóm nguyên nhân quan trọng nhất: thiết kế workflow không coi concurrency là first-class concern.

Dấu hiệu phổ biến:

- Validation và commit tách rời bởi nhiều thao tác trung gian.
- Mỗi request tự tin rằng state đang đọc vẫn còn đúng khi ghi.
- Quy tắc one-time hoặc limit chỉ kiểm tra ở đầu luồng.

## 2. Missing or Incorrect Synchronization

### Thiếu khóa hoàn toàn

Không có cơ chế tuần tự hóa truy cập vào shared resource.

### Khóa sai phạm vi

- Khóa theo session nhưng state nằm ở database theo user/account.
- Khóa in-memory trong một worker, nhưng hệ thống có nhiều worker/node.

### Khóa quá trễ

Khóa được đặt sau bước check quan trọng, race window vẫn còn tồn tại.

## 3. Transaction Handling Inconsistency

Các biến thể lỗi thường gặp:

- Check ở transaction A, update ở transaction B.
- Đọc bằng isolation yếu, ghi ở luồng khác trước khi commit.
- Nhiều lệnh SQL rời rạc thay vì một transaction nguyên tử.

Hậu quả: TOCTOU giữa thời điểm check và thời điểm dùng state.

## 4. Non-atomic Session or State Updates

Session thường bị xem là nơi an toàn để điều phối bảo mật, nhưng có nhiều rủi ro:

- Cập nhật từng biến session riêng lẻ thay vì batch/atomic.
- Kết hợp state từ nhiều lớp lưu trữ (session + DB + cache) không đồng nhất.

Ví dụ: `session['reset-user']` và `session['reset-token']` có thể bị trộn giữa hai request nếu update không đồng bộ.

## 5. Async Side Effects and Out-of-band Operations

Các tiến trình gửi email, queue worker, webhook, audit logger có thể đọc state sau khi request chính đã thay đổi state bởi request khác.

Mẫu lỗi điển hình:

- Request 1 bắt đầu gửi email xác nhận.
- Request 2 đổi giá trị email pending.
- Nội dung email hoặc token bị mismatch với người nhận.

## 6. Multi-thread, Multi-process, Distributed Pitfalls

| Environment   | Typical Mistake                               | Result                     |
| ------------- | --------------------------------------------- | -------------------------- |
| Multi-thread  | Không lock critical section                   | Double-spend, double-apply |
| Multi-process | Dùng mutex local cho state global             | Bỏ lọt race giữa workers   |
| Distributed   | Dựa vào eventual consistency cho rule bảo mật | Check/commit lệch node     |

## 7. Weak Time-based Token Generation

Không phải mọi timing bug là race, nhưng nhiều hệ thống tạo token bằng timestamp hoặc bộ sinh đoán được. Khi gửi request đồng thời, hai user có thể nhận token trùng.

Đây là lỗi cryptography/state design, khai thác bằng kỹ thuật timing precision.

## 8. Mapping: Cause -> Exploit Primitive

| Root Cause                       | Primitive Attacker Gains              |
| -------------------------------- | ------------------------------------- |
| Check-then-update không atomic   | Limit overrun, TOCTOU bypass          |
| Update session không batch       | State mix-up (user/token mismatch)    |
| Async side effect đọc state muộn | Email/token misdelivery               |
| Object tạo nhiều bước            | Confirm bằng null/uninitialized value |
| Token phụ thuộc timestamp        | Predictable/colliding token           |

## 9. Design Principle

Nếu một rule bảo mật phụ thuộc vào "thứ tự chạy lý tưởng", hệ thống đó đang có nợ kỹ thuật concurrency và có nguy cơ race condition.

## Related Files

- [01-concurrency-and-timing-foundations](01-concurrency-and-timing-foundations.md)
- [03-detection-and-scoping](03-detection-and-scoping.md)
- [12-defense-mitigation](12-defense-mitigation.md)
