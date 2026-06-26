# Same-Origin Policy (SOP)

## What Is an Origin?

Origin được xác định bởi 3 thành phần:

- `scheme` (http/https)
- `host` (domain)
- `port`

Hai URL chỉ cùng origin khi cả 3 thành phần đều trùng khớp.

## SOP Decision Matrix

Giả sử trang gốc là `http://normal-website.com/example/example.html`:

| URL truy cập                              | Được phép đọc dữ liệu? | Lý do                          |
| ----------------------------------------- | ---------------------- | ------------------------------ |
| `http://normal-website.com/example/`      | Yes                    | Cùng scheme, host, port        |
| `http://normal-website.com/example2/`     | Yes                    | Cùng scheme, host, port        |
| `https://normal-website.com/example/`     | No                     | Khác scheme (và port mặc định) |
| `http://en.normal-website.com/example/`   | No                     | Khác host                      |
| `http://www.normal-website.com/example/`  | No                     | Khác host                      |
| `http://normal-website.com:8080/example/` | No                     | Khác port                      |

## Why SOP Is Necessary

Khi trình duyệt gửi request tới site B, cookie của site B (nếu hợp lệ) được gửi kèm. Không có SOP, site A đọc được response của site B trong session của người dùng, dẫn đến lộ thông tin nghiêm trọng (email, profile, giao dịch, dữ liệu cá nhân).

## How SOP Is Implemented in Practice

SOP chủ yếu hạn chế JavaScript đọc nội dung cross-origin. Trình duyệt vẫn cho phép load nhiều loại tài nguyên cross-origin như:

- `<img>`, `<video>`, `<script>`, `<link>`

Nhưng script tại trang không được đọc nội dung chi tiết của response cross-origin nếu không có cơ chế nới lỏng hợp lệ (như CORS).

## Important SOP Exceptions and Nuances

| Case                                | Behavior                                          |
| ----------------------------------- | ------------------------------------------------- |
| `window.location` giữa frame/window | Thường có thể ghi, bị hạn chế đọc                 |
| `window.length`, `window.closed`    | Có thể đọc một phần thông tin trạng thái          |
| `window.postMessage`                | Cho phép giao tiếp cross-origin có kiểm soát      |
| Cookies giữa subdomain              | Thường lỏng hơn SOP do domain scoping             |
| `document.domain` (legacy)          | Có thể nới lỏng giữa các subdomain trong một FQDN |

## SOP and CORS Relationship

- SOP là policy mặc định: chặn đọc cross-origin.
- CORS là cơ chế nới lỏng SOP theo khai báo của server qua HTTP headers.

## Security Takeaway

SOP là lớp phòng thủ cơ bản của browser sandbox. CORS không thay SOP, mà chỉ bổ sung logic cho phép ngoại lệ. Mỗi sai sót trong CORS đồng nghĩa với mở rộng trust boundary sai cách.

## Related Files

- [Overview](00-overview.md)
- [CORS Protocol and Headers](02-cors-protocol-and-headers.md)
- [Defense and Mitigation](13-defense-mitigation.md)
