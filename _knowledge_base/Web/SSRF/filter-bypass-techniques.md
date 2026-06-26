# Filter Bypass Techniques

## 1. Mục tiêu bypass trong SSRF

Filter bypass nhằm biến input "trông hợp lệ" theo logic validate, nhưng vẫn dẫn request đến đích bị cấm.

## 2. Bypass blacklist localhost/internal

Các biến thể thường dùng:

1. Dạng IP thay thế:
   - `127.1`, `127.0.1`, `0`, decimal/dword, octal, hex.
2. IPv6 loopback/embedding:
   - `[::1]`, `[::ffff:127.0.0.1]`.
3. Domain trỏ loopback:
   - domain wildcard/rebind như `nip.io`.

## 3. Bypass whitelist theo URL parsing

Kỹ thuật chính:

1. Userinfo confusion (`@`):
   - đặt host hợp lệ trước `@`, host thật sau `@`.
2. Fragment confusion (`#`):
   - đánh lạc hướng bộ lọc string-based.
3. Subdomain confusion:
   - `expected-host.attacker.tld`.
4. Encoding mismatch:
   - URL encode/double encode để parser validate và parser request hiểu khác nhau.

## 4. Redirect-based bypass

Điều kiện:

- URL ban đầu nằm trong allowlist,
- HTTP client follow redirect.

Mô hình:

1. Gửi URL hợp lệ theo policy.
2. Endpoint đó trả `30x` về internal target.
3. Server tự follow và truy cập đích bị cấm.

Từ tài liệu tham chiếu, `307/308` đặc biệt hữu ích khi cần giữ nguyên method/body.

## 5. DNS rebinding và DNS pinning bypass

1. Domain attacker trả IP công khai lúc validate.
2. Sau đó đổi bản ghi sang IP nội bộ lúc request thực thi.
3. Nếu hệ thống không khóa DNS behavior, có thể bypass domain control.

## 6. URL parser discrepancy bypass

Nhiều payload thành công nhờ sai khác giữa parser:

1. backslash và ký tự phân tách bất thường,
2. ký tự `@`, `#`, `;`,
3. URL thiếu `//` nhưng được parser tự chuẩn hóa,
4. kết hợp encoded ký tự để tạo nghĩa khác ở tầng dưới.

## 7. Protocol/scheme bypass

Nếu chỉ chặn `http/https` bằng regex yếu, attacker có thể thử:

1. `file://`
2. `dict://`
3. `gopher://`
4. `ldap://`
5. `jar:` hoặc wrapper tương đương ở runtime đặc thù.

## 8. Bypass qua thành phần phụ trợ

1. Open redirect nội bộ.
2. Reverse proxy xử lý absolute-form request line.
3. Framework route edge-case (`@`, `;`, `*` ở đầu path) dẫn tới đổi host đích.

## 9. Điều kiện khiến bypass thất bại

1. Không follow redirect.
2. Canonicalize rồi validate trên cùng một parser/runtime.
3. Resolve DNS và kiểm tra IP cuối cùng thuộc allowlist nghiêm ngặt.
4. Chặn egress mạng đến private/link-local/metadata.

## 10. Chiến lược kiểm thử bypass có kiểm soát

1. Bắt đầu từ bypass rủi ro thấp:
   - host notation,
   - URL encoding,
   - parser confusion nhẹ.
2. Chỉ thử protocol abuse/gopher khi có scope cho phép.
3. Ghi rõ parser path và điều kiện thành công để hỗ trợ fix triệt để.
