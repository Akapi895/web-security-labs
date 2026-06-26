# Prevention And Hardening

## 1. Nguyên tắc phòng thủ cốt lõi

1. Không tin URL do user cung cấp.
2. Giảm tối đa nhu cầu nhận full URL từ client.
3. Áp dụng defense-in-depth ở cả application layer và network layer.

## 2. Áp dụng theo 2 case của OWASP

### 2.1 Case 1: Chỉ gọi các ứng dụng đã xác định

Chiến lược:

1. Allowlist chặt cho host/IP đích.
2. Validate định dạng input bằng thư viện parser đáng tin cậy.
3. Canonicalize rồi so sánh strict với allowlist.
4. Tắt tự động follow redirect.
5. Kiểm tra DNS resolution và giám sát drift bản ghi.

### 2.2 Case 2: Bắt buộc gọi đích bên ngoài động

Chiến lược:

1. Chặn private/link-local/localhost/metadata range.
2. Chỉ cho phép `http/https`.
3. Hạn chế method, header và payload gửi ra ngoài.
4. Dùng cơ chế xác thực callback (token ràng buộc nghiệp vụ).
5. Bắt buộc outbound qua egress proxy có policy.

## 3. Application hardening checklist

1. Chỉ nhận identifier thay vì URL khi có thể.
2. Nếu phải nhận URL:
   - parse chuẩn,
   - chuẩn hóa,
   - validate host/IP/scheme/port,
   - resolve DNS và kiểm tra IP cuối cùng.
3. Chặn scheme nguy hiểm:
   - `file`, `gopher`, `dict`, `ldap`, `jar`, ...
4. Không forward trực tiếp header nhạy cảm đến đích ngoài.
5. Giới hạn timeout, response size, redirect depth.

## 4. Network hardening checklist

1. Egress firewall theo principle of least connectivity.
2. Chặn truy cập từ app tier tới:
   - localhost,
   - RFC1918/private ranges,
   - link-local,
   - metadata endpoints cloud.
3. Tách network segment giữa web tier và service quản trị.
4. Giám sát outbound bất thường theo host/port/protocol.

## 5. Cloud-specific hardening

1. AWS:
   - bật IMDSv2,
   - tắt IMDSv1,
   - chặn route metadata nếu không cần.
2. Azure/GCP:
   - kiểm soát truy cập metadata endpoint tương tự.
3. Gắn IAM role tối thiểu để giảm blast radius nếu lộ token.

## 6. Chống DNS rebinding và parser abuse

1. Resolve bằng resolver kiểm soát nội bộ.
2. Kiểm tra tất cả A/AAAA sau resolve.
3. Re-validate IP đích ngay trước khi kết nối.
4. Đồng nhất parser dùng cho validate và thực thi request.

## 7. Logging và detection

1. Log đầy đủ outbound destination:
   - scheme,
   - host,
   - resolved IP,
   - port,
   - redirect chain.
2. Cảnh báo khi truy cập địa chỉ nhạy cảm:
   - `127.0.0.0/8`, `::1`, `169.254.169.254`, RFC1918.
3. Correlate với input source để truy vết injection point.

## 8. SDLC và kiểm thử

1. Security review cho mọi chức năng fetch URL.
2. Unit/integration tests cho URL validation policy.
3. DAST/OAST test định kỳ cho SSRF.
4. SAST rules cho code pattern `requests.get(user_input)` và tương đương.

## 9. Anti-pattern cần loại bỏ

1. Chỉ blacklist `localhost` và `127.0.0.1`.
2. Validate bằng regex ad-hoc rồi gọi HTTP client khác parser.
3. Tin tưởng redirect vì "URL ban đầu hợp lệ".
4. Để app server truy cập tự do toàn bộ mạng nội bộ.
