# Payload Patterns (Structured Reference)

## 1. Mục đích tài liệu

Tài liệu này không thay thế workflow khai thác, mà cung cấp "mẫu payload" theo nhóm kỹ thuật để chọn đúng công cụ cho đúng bối cảnh.

## 2. Baseline probes

1. Loopback:
   - `http://127.0.0.1`
   - `http://localhost`
2. Internal IP:
   - `http://192.168.x.x`
   - `http://10.x.x.x`
3. Metadata:
   - `http://169.254.169.254/latest/meta-data/`

## 3. Host/IP obfuscation patterns

1. IPv6 loopback/embedding.
2. Decimal/octal/hex IPv4 biểu diễn thay thế.
3. Short notation (`127.1`, `0`).
4. Domain wildcard trỏ loopback.

## 4. URL parser confusion patterns

1. Userinfo (`@`) confusion.
2. Fragment (`#`) confusion.
3. Encoded delimiter confusion.
4. Mixed slash/backslash.

## 5. Redirect patterns

1. URL hợp lệ ban đầu -> 30x -> internal target.
2. Thử cả `302`, `307`, `308` theo behavior HTTP client.

## 6. Scheme patterns

1. `http(s)://` cho recon nội bộ.
2. `file://` cho local file read (nếu runtime cho phép).
3. `dict://`, `ldap://` cho protocol-level probe.
4. `gopher://` cho TCP payload shaping.

## 7. Blind SSRF patterns

1. OAST domain callback.
2. Time-based probe theo port/service.
3. Side-effect probe vào endpoint có logging.

## 8. Gopher usage patterns (khái quát)

1. Chọn service đích (port/protocol) trước.
2. Mã hóa đúng byte sequence theo protocol đích.
3. Gửi payload xác minh an toàn trước payload thay đổi trạng thái.

## 9. Mapping pattern -> use case

1. Không có filter:
   - baseline probes + internal mapping.
2. Blacklist đơn giản:
   - host obfuscation + encoding.
3. Whitelist theo domain:
   - parser confusion + open redirect chain.
4. Blind only:
   - OAST + timing + deterministic side effects.
5. Có đường tới TCP service:
   - cân nhắc protocol abuse có kiểm soát.
