# Origin Referer and Request Shape Bypass

## Mục tiêu của nhóm bypass này

Nhiều hệ thống không dựa hoàn toàn vào token mà dùng header checks hoặc ràng buộc hình dạng request. Khi các ràng buộc này triển khai sai, CSRF vẫn khai thác được.

## Bypass kiểm tra Origin/Referer

## 1. Validation phụ thuộc header có hiện diện

Anti-pattern:

- Chỉ validate khi có Origin/Referer.
- Nếu thiếu header thì cho qua.

Khai thác:

- Dùng cơ chế khiến browser không gửi Referer (ví dụ referrer policy phù hợp).

## 2. Matching domain ngây thơ

Anti-pattern:

- Kiểm tra kiểu `contains("trusted.com")` hoặc `startsWith("https://trusted.com")`.

Khai thác:

- Dùng lookalike domain hoặc đặt trusted string trong query/path.

## 3. Fail-open cho trường hợp null/absent

Nếu policy không xác định rõ xử lý khi thiếu cả Origin và Referer, attacker có thể tìm cách tạo request rơi vào nhánh cho qua.

## Bypass theo request shape

## 1. Method override

Nhiều framework hỗ trợ override method qua:

- `_method` trong query/body,
- `X-HTTP-Method`,
- `X-HTTP-Method-Override`,
- `X-Method-Override`.

Nếu CSRF filter chỉ nhìn `POST` ban đầu mà không nhìn effective method, attacker có thể né kiểm tra.

## 2. HEAD xử lý như GET

Một số router map HEAD vào logic GET (chỉ bỏ response body). Nếu GET nhạy cảm và không tokenized, HEAD có thể trở thành vector thay thế.

## 3. Content-Type confusion

Backend parse dữ liệu lỏng có thể cho phép:

- endpoint kỳ vọng JSON nhưng vẫn nhận text/plain hoặc form encoding,
- từ đó forged form truyền được dữ liệu state-changing.

## 4. Preflight avoidance

Request "simple" (form, text/plain, x-www-form-urlencoded, multipart/form-data) thường tránh preflight, thuận lợi cho CSRF hơn custom-header JSON request.

## Mô hình tấn công tổng hợp

```text
Header-check weakness OR request-shape weakness
   +
cookie-based authenticated action
   =>
forged request accepted as legitimate user intent
```

## Checklist kiểm thử thực hành

- [ ] Bỏ Origin/Referer có bị reject không?
- [ ] Giá trị Referer lookalike có qua được filter không?
- [ ] Đổi method qua `_method` hoặc override headers có qua được route nhạy cảm không?
- [ ] Đổi content-type nhưng giữ semantic dữ liệu có vẫn xử lý thành công không?
- [ ] HEAD request có side effect ngoài mong đợi không?

## Gợi ý hardening

1. Validate Origin ưu tiên, Referer là fallback có kiểm soát.
2. Nếu thiếu cả Origin và Referer: fail-closed cho action nhạy cảm.
3. So sánh host/scheme chính xác, không substring/regex lỏng.
4. Chuẩn hóa effective method trước khi áp rule CSRF.
5. Giới hạn parser theo content-type đúng thiết kế.

## Related Files

- [Root Causes and Conditions](02-root-causes-and-conditions.md)
- [Token Validation Bypasses](05-token-validation-bypasses.md)
- [SameSite and Browser Behavior](06-samesite-and-browser-behavior.md)
- [Payloads Cheatsheet](09-payloads-cheatsheet.md)
- [Defense and Mitigation](10-defense-mitigation.md)
