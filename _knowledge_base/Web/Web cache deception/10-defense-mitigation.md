# Phòng thủ và giảm thiểu

## Mục tiêu phòng thủ

Để loại bỏ WCD, cần xử lý đồng thời 3 lớp:

1. Origin application.
2. Reverse proxy/CDN/cache layer.
3. Quy trình test và governance.

Nếu chỉ fix ở một lớp, nguy cơ discrepancy vẫn còn.

## 1) Nguyên tắc cốt lõi

1. Dynamic response nhạy cảm phải `no-store` hoặc ít nhất `private`.
2. Cache rules không được dựa đơn thuần vào extension/prefix.
3. Cache và origin phải thống nhất cách parse/normalize URL.
4. Từ chối URL mơ hồ (delimiter bất thường, traversal encoded) ở edge hoặc origin.

## 2) Hardening HTTP caching policy

## Đối với endpoint nhạy cảm

- Đặt `Cache-Control: no-store, private`.
- Tránh để edge override policy này.
- Kiểm soát `Vary` phù hợp nếu có cache theo ngữ cảnh.

## Đối với endpoint có thể cache

- Cho phép cache có điều kiện rõ ràng theo content-type và route allow-list.
- Hạn chế cache theo đường dẫn được thiết kế cho static.

## 3) Hardening CDN/reverse proxy rules

1. Tắt rule extension-based quá rộng cho route dynamic.
2. Tắt rule static-prefix cho path có khả năng map đến route động.
3. Bật cơ chế đối chiếu extension và `Content-Type` (nếu nhà cung cấp hỗ trợ).
4. Canonicalize URL tại edge và reject request mơ hồ.

## 4) Parser parity controls

Cần có bộ test đảm bảo CDN/proxy/origin thống nhất:

- Delimiter semantics (`;`, `%23`, `%3f`, `%00`, ...).
- Decode order.
- Dot-segment normalization.
- Route mapping cho path có segment dư thừa.

## 5) Input/path validation ở origin

- Chỉ chấp nhận route đúng schema mong đợi.
- Từ chối path bất thường (unexpected suffix, encoded traversal).
- Không fallback route quá linh hoạt cho endpoint nhạy cảm.

## 6) Logging và detection

Cần ghi log cho:

- Request có delimiter/traversal bất thường.
- URL dynamic có extension static giả.
- Đột biến cache hit trên endpoint nhạy cảm.

Cảnh báo sớm khi có mẫu payload thường gặp của WCD.

## 7) Mapping root cause -> fix

| Root cause                            | Giải pháp ưu tiên                                          |
| ------------------------------------- | ---------------------------------------------------------- |
| Path mapping discrepancy              | Route strict + reject extra segments cho endpoint nhạy cảm |
| Delimiter discrepancy                 | Canonical parse policy + reject delimiter bất thường       |
| Delimiter decoding discrepancy        | Thống nhất decode order edge/origin                        |
| Normalization discrepancy             | Thống nhất normalization rule, chặn encoded traversal      |
| Extension/prefix cache rules quá rộng | Cache allow-list theo route + content-type validation      |

## 8) Verification sau khi fix

1. Chạy lại playbook detection trên toàn bộ endpoint nhạy cảm.
2. Xác minh payload cũ không còn tạo cache hit bất thường.
3. Xác minh victim-flow không còn leak data.
4. Bổ sung regression test vào CI/CD security pipeline.

## 9) Anti-pattern cần tránh

1. Chỉ chặn một payload cụ thể thay vì xử lý parser/rule gốc.
2. Phụ thuộc WAF đơn thuần mà bỏ qua config CDN.
3. Tin rằng static extension là đủ để kết luận static content.

## 10) Checklist vận hành

- [ ] Dynamic endpoint nhạy cảm: `no-store/private`.
- [ ] Edge không override policy nhạy cảm.
- [ ] Đã bật extension-content-type consistency check (nếu có).
- [ ] Đã có parser parity test bằng fuzz delimiter/traversal.
- [ ] Đã có regression test cho các payload WCD chính.

## Liên kết đọc tiếp

- [02-root-causes.md](02-root-causes.md)
- [07-cache-rules-key-and-oracles.md](07-cache-rules-key-and-oracles.md)
- [11-payloads-cheatsheet.md](11-payloads-cheatsheet.md)
