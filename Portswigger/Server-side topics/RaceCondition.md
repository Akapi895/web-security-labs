# Race Condition - Báo Cáo Tổng Hợp

## 1. Race Condition là gì

Race Condition là lỗi xảy ra khi kết quả xử lý phụ thuộc vào thứ tự hoặc thời điểm thực thi của nhiều request/tác vụ đồng thời, trong khi hệ thống không đảm bảo đồng bộ đúng cách. Hậu quả là trạng thái dữ liệu cuối cùng có thể khác với quy tắc nghiệp vụ dự kiến.

Bản chất của lỗi này là lỗi quản lý trạng thái trong bối cảnh concurrency, không phải lỗi cú pháp.

## 2. Các khái niệm cốt lõi

- Shared resource: tài nguyên dùng chung như balance, cart, token, counter.
- Critical section: đoạn logic cần atomic để tránh chen lấn nhau.
- Race window: khoảng thời gian có thể xảy ra va chạm.
- Order dependency: kết quả thay đổi khi đảo thứ tự thực thi.
- Hidden sub-state: trạng thái tạm thời trong một request, dễ bị lợi dụng.

## 3. Nguyên nhân gốc rễ

1. Logic check và update tách rời, không atomic.
2. Thiếu lock hoặc lock sai phạm vi.
3. Transaction không nhất quán giữa các bước quan trọng.
4. Session/DB/cache cập nhật lệch nhau.
5. Side effect async (email, worker) đọc state tại thời điểm không an toàn.
6. Token bảo mật dựa vào timestamp hoặc entropy yếu.

## 4. Nhóm khai thác chính

1. Limit overrun TOCTOU: vượt giới hạn sử dụng một lần/rate-limit.
2. Multi-endpoint race: endpoint check và endpoint mutate va chạm.
3. Single-endpoint race: cùng endpoint, input khác nhau, state bị trộn.
4. Partial construction: object được tạo nhiều bước, lợi dụng state chưa hoàn tất.
5. Time-sensitive attacks: timing chính xác để tạo token trùng/dự đoán được.

## 5. Quy trình đánh giá và khai thác

Predict -> Probe -> Prove:

1. Predict: chọn endpoint nhạy cảm và có collision potential.
2. Probe: benchmark sequential, sau đó parallel để tìm deviation.
3. Prove: thu hẹp PoC, tái lập nhiều lần, chứng minh invariant bị phá.

Ví dụ chức năng nhạy cảm cần ưu tiên:

- Chuyển tiền, rút tiền, loyalty points.
- Reset password, change email, verify account.
- Checkout, apply coupon/gift card.
- Failed login counter va anti-bruteforce.

## 6. Dấu hiệu xác nhận lỗi thực sự

- Nhiều request cùng thành công vượt giới hạn cho phép.
- Trạng thái cuối cùng vi phạm quy tắc nghiệp vụ.
- Side effect bậc hai sai (email/token gửi sai đối tượng).
- Có thể tái lập với điều kiện timing rõ ràng.

## 7. Tư duy phòng thủ đúng bản chất

Nguyên tắc phòng thủ cốt lõi:

1. Atomic check + update trong cùng transaction/critical section.
2. Lock theo đúng resource key (user/account/order), không chỉ theo session.
3. Ràng buộc integrity ở datastore (unique/check constraints).
4. Idempotency key cho hành động có nguy cơ replay.
5. Token bảo mật sử dụng CSPRNG, bind context, one-time consume atomically.
6. Async worker dùng snapshot đã commit, không đọc mutable state lệch thời điểm.

## 8. Giá trị cho học tập, pentest, và huấn luyện agent

Bộ tài liệu Race Condition được tổ chức theo module để:

- Học theo lộ trình từ nền tảng đến kỹ thuật nâng cao.
- Áp dụng trực tiếp vào pentest với workflow tái lập được.
- Dùng làm nền cho xây lab và huấn luyện agent theo state-machine reasoning.

Xem bộ đầy đủ trong thư mục:

- [00-overview](../Web/Race%20Condition/00-overview.md)
- [14-reference-mapping](../Web/Race%20Condition/14-reference-mapping.md)
