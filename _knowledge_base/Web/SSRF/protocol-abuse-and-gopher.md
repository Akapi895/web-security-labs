# Protocol Abuse And Gopher

## 1. Vì sao protocol abuse nguy hiểm

SSRF không giới hạn ở HTTP. Khi ứng dụng cho phép nhiều URL scheme, attacker có thể tương tác với giao thức nội bộ theo cách low-level.

Điểm then chốt:

- server là bên mở kết nối,
- attacker kiểm soát đích và đôi khi cả byte stream gửi đi.

## 2. Scheme matrix (từ tài liệu tham chiếu)

1. `http://` và `https://`:
   - internal API access,
   - port probing,
   - metadata retrieval.
2. `file://`:
   - local file read trong một số runtime.
3. `dict://`, `ldap://`, `tftp://`, `sftp://`:
   - giao tiếp dịch vụ phi HTTP.
4. `gopher://`:
   - gửi payload TCP tùy biến tới service nội bộ.
5. `jar:`/`netdoc:` trong ngữ cảnh Java:
   - bypass/parser edge-case và blind behavior.

## 3. Gopher exploitation model

Gopher cho phép định nghĩa:

1. host,
2. port,
3. selector/payload bytes.

Điều này biến SSRF thành primitive giao tiếp TCP nội bộ.

## 4. Nhóm dịch vụ nội bộ hay bị nhắm đến

Theo tài liệu advanced:

1. Redis.
2. FastCGI.
3. Memcached.
4. MySQL.
5. SMTP.
6. uWSGI/WSGI.
7. Zabbix agent.

Lưu ý:

- Khả năng khai thác phụ thuộc cấu hình dịch vụ, auth và quyền runtime.

## 5. Từ SSRF sang state manipulation

Ngay cả khi không đạt RCE tức thì, protocol abuse vẫn có thể:

1. thay đổi trạng thái service,
2. ghi dữ liệu độc hại,
3. mở đường cho chain tiếp theo.

Ví dụ điển hình trong tài liệu là thao tác Redis để ghi file vào webroot trong điều kiện cấu hình yếu.

## 6. Yêu cầu tiên quyết khi chain qua protocol

1. SSRF sink chấp nhận scheme tương ứng.
2. Network path từ app server đến service đích mở.
3. Payload được encode đúng với protocol framing.
4. Dịch vụ đích có cấu hình dễ bị lạm dụng.

## 7. Dấu hiệu phát hiện protocol abuse thành công

1. Side effect đo được (dịch vụ đổi trạng thái).
2. Callback hoặc phản hồi nội bộ thay đổi.
3. Artifact hệ thống xuất hiện (file ghi mới, user mới, config đổi).

## 8. Khuyến nghị thực hành an toàn trong lab/pentest

1. Tách môi trường lab khỏi hạ tầng production.
2. Chỉ test protocol abuse trong phạm vi được ủy quyền rõ ràng.
3. Ưu tiên payload xác minh (non-destructive) trước payload thay đổi trạng thái.
4. Log đầy đủ request và side effect để phục vụ phân tích hậu kiểm.

## 9. Defensive note

Để giảm rủi ro protocol abuse:

1. Chỉ cho phép `http/https` khi thực sự cần.
2. Chặn scheme lạ ở parser và HTTP client layer.
3. Egress firewall chặn truy cập nội mạng không cần thiết.
4. Cô lập ứng dụng khỏi dịch vụ nội bộ nhạy cảm theo nguyên tắc least connectivity.
