# CORS Protocol and Headers

## Protocol Purpose

CORS sử dụng bộ HTTP headers để browser xác định:

- Origin nào được phép đọc response.
- Request nào cần preflight.
- Có cho phép credentials hay không.

## Key Request Headers

| Header                           | Side                          | Purpose                                       |
| -------------------------------- | ----------------------------- | --------------------------------------------- |
| `Origin`                         | Browser -> Server             | Khai báo origin khởi tạo request cross-origin |
| `Access-Control-Request-Method`  | Browser -> Server (preflight) | Method dự kiến của request thật               |
| `Access-Control-Request-Headers` | Browser -> Server (preflight) | Header custom dự kiến gửi                     |

## Key Response Headers

| Header                             | Side              | Purpose                                                       |
| ---------------------------------- | ----------------- | ------------------------------------------------------------- |
| `Access-Control-Allow-Origin`      | Server -> Browser | Origin được phép đọc response                                 |
| `Access-Control-Allow-Credentials` | Server -> Browser | Cho phép browser gửi cookie/auth và đọc response credentialed |
| `Access-Control-Allow-Methods`     | Server -> Browser | Method được phép sau preflight                                |
| `Access-Control-Allow-Headers`     | Server -> Browser | Header được phép sau preflight                                |
| `Access-Control-Expose-Headers`    | Server -> Browser | Header response được phép JS đọc thêm                         |
| `Access-Control-Max-Age`           | Server -> Browser | TTL cache kết quả preflight                                   |

## Simple CORS Flow

Vi du:

```http
GET /data HTTP/1.1
Host: api.example.com
Origin: https://app.example.net
```

```http
HTTP/1.1 200 OK
Access-Control-Allow-Origin: https://app.example.net
```

Nếu `ACAO` trùng origin request, script tại `app.example.net` đọc được body response.

## Credentialed Cross-Origin Requests

Mặc định, browser không gửi credentials trong cross-origin XHR/fetch. Để gửi credentials:

- Client cần set `withCredentials = true` hoặc `credentials: "include"`.
- Server cần trả `Access-Control-Allow-Credentials: true`.
- `Access-Control-Allow-Origin` phải là origin cụ thể, không được là `*`.

## Wildcard Rules

| Configuration                                                               | Valid?                   | Risk                                                    |
| --------------------------------------------------------------------------- | ------------------------ | ------------------------------------------------------- |
| `Access-Control-Allow-Origin: *`                                            | Valid (non-credentialed) | Có thể lộ dữ liệu công khai/dữ liệu intranet không auth |
| `Access-Control-Allow-Origin: *` + `Access-Control-Allow-Credentials: true` | Browser block            | Thường là dấu hiệu cấu hình sai                         |
| `Access-Control-Allow-Origin: https://*.example.com`                        | Không theo chuẩn ACAO    | Có thể tạo logic whitelist lỗi nếu app tự xử lý         |

## Multi-Origin Misconception

`Access-Control-Allow-Origin` không hỗ trợ danh sách nhiều origin trong một header để browser xử lý. Các hệ thống cần hỗ trợ nhiều origin thường phải chọn 1 origin hợp lệ và trả về đúng 1 giá trị.

## Security Takeaway

Logic CORS an toàn là logic xác thực trust boundary, không phải logic "phản hồi cho chạy". Bất kỳ cơ chế reflect origin không xác thực chính xác đều có nguy cơ cao.

## Related Files

- [Preflight and Flows](03-preflight-and-request-flows.md)
- [Misconfiguration Root Causes](05-misconfiguration-root-causes.md)
- [Defense and Mitigation](13-defense-mitigation.md)
