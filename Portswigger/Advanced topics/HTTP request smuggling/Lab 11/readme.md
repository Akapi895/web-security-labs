# Lab: Lấy API key qua Web cache deception bằng request smuggling

Mục tiêu: dùng request smuggling để khiến server cache lưu một response chứa thông tin nhạy cảm (ví dụ API key) và sau đó truy xuất cache từ chế độ client/không đăng nhập.

Yêu cầu trước: bạn có tài khoản test trên ứng dụng và có thể đăng nhập để xem trang `My account` (trong đó chứa API key). Trang trả về không có header chống cache (ví dụ `Cache-Control: no-store`).

1) Kiểm tra ban đầu

- Đăng nhập vào tài khoản test, mở trang `My account` và xác nhận rằng response không có header chống cache (Cache-Control, Pragma).

2) Ý tưởng khai thác

- Smuggle một request `GET /my-account` (hoặc endpoint chứa API key) vào cache của server, bằng cách đặt `Host`/request sao cho cache sẽ lưu bản trả về như một resource tĩnh.
- Sau đó, truy vấn resource cache từ một cửa sổ trình duyệt mới (incognito) hoặc tìm trong Burp để lấy nội dung đã cached, từ đó thu thập API key.

3) Payload mẫu để smuggle

```http
POST / HTTP/1.1
Host: YOUR-LAB-ID.web-security-academy.net
Content-Type: application/x-www-form-urlencoded
Content-Length: 42
Transfer-Encoding: chunked

0

GET /my-account HTTP/1.1
X-Ignore: X
```

Giải thích:

- Payload trên cố ý đặt một request `GET /my-account` ở phần dữ liệu sau cùng.
- Nếu front-end và back-end xử lý header body khác nhau, phần `GET /my-account` có thể được back-end hiểu là một request độc lập và lưu response vào cache.

4) Thực hiện và xác minh

- Gửi payload trên vài lần để đảm bảo cache nhận bản trả về.
- Mở trang chủ trong cửa sổ incognito hoặc gửi request tới các tài nguyên tĩnh (search trong Burp) để xem có xuất hiện chuỗi "Your API Key" trong nội dung tĩnh hay không.

5) Lấy API key và nộp kết quả

- Khi resource đã bị cached, nội dung sẽ chứa API key của người dùng (ví dụ xuất hiện trong HTML trả về). Lấy giá trị đó và submit làm kết quả lab.

> Nếu lần đầu không thấy kết quả, thử gửi lại payload, chờ một chút cho cache cập nhật, hoặc thử thay đổi header `Host`/tham số để phù hợp với cơ chế cache của ứng dụng.
