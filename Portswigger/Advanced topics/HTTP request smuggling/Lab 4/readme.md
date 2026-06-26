# Lab: HTTP request smuggling, confirming a TE.CL vulnerability via differential responses

## Mục tiêu

Bài này không chỉ là chọc cho server timeout, mà là quan sát sự khác nhau trong phản hồi để kết luận front-end và back-end đang đọc request theo hai cách khác nhau.

Nếu hai payload gần giống nhau nhưng phản hồi lại khác rõ rệt, đó là dấu hiệu rất mạnh của request smuggling.

## Payload kiểm tra

```http
POST / HTTP/1.1
Host: 0a6100b1034f3be781de1bbd00fd0000.web-security-academy.net
Content-Type: application/x-www-form-urlencoded
Content-Length: 4
Transfer-Encoding: chunked

a8
POST /throw404 HTTP/1.1
Host: 0a6100b1034f3be781de1bbd00fd0000.web-security-academy.net
Content-Type: application/x-www-form-urlencoded
Content-Length: 15

foo=bar
0
```

Payload này tạo một request nhìn giống chunked ở front-end, nhưng phần back-end đọc theo `Content-Length` lại thấy cấu trúc khác. Kết quả thu được thường là `500 Internal Server Error`, `Proxy error`, hoặc `Communication timed out`.

## Cách hiểu phản hồi

Điểm quan trọng của lab là so sánh phản hồi thay vì chỉ nhìn một response đơn lẻ:

- Nếu request bị timeout, rất có thể một tầng đang chờ dữ liệu còn tầng kia đã kết thúc parse.
- Nếu response thay đổi giữa `400 Bad Request`, `500 Internal Server Error`, hoặc lỗi proxy, đó là bằng chứng parser giữa front-end và back-end không đồng nhất.

Trong bài này, sự khác biệt đó xác nhận website tồn tại TE.CL vulnerability.

## Kết luận

Sau khi xác nhận TE.CL, có thể tiếp tục dùng cùng kiểu payload smuggling như ở các lab trước để đẩy request kế tiếp vào connection của back-end. Ở bài này, trọng tâm là chứng minh lỗ hổng thông qua differential responses.
