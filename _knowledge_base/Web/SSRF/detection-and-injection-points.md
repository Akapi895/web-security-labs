# Detection And Injection Points

## 1. Mục tiêu của giai đoạn detection

1. Xác định nơi server có thực hiện outbound request.
2. Xác định mức kiểm soát input (full URL, host-only, path-only).
3. Xác nhận SSRF bằng tín hiệu in-band hoặc out-of-band.

## 2. Injection points điển hình

1. Query/body parameter chứa URL:
   - `url`, `uri`, `target`, `endpoint`, `callback`, `webhook`, `stockApi`.
2. Trường dữ liệu trong JSON/XML dùng để fetch tài nguyên ngoài.
3. Header-based surface:
   - `Referer` trong analytics/crawler.
4. Tính năng import/render:
   - HTML-to-PDF, CSS import, file conversion, feed import.
5. Partial URL features:
   - chỉ nhận hostname hoặc path nhưng vẫn có thể SSRF khi server tự ghép URL.

## 3. Detection workflow chuẩn

1. Gửi payload đến domain OAST kiểm soát bởi tester.
2. Theo dõi callback DNS/HTTP.
3. Nếu có callback:
   - xác nhận server đã thực hiện request thay user.
4. Nếu không callback:
   - thử thay protocol, thay port, thay encoding, thay phương thức submit.

## 4. In-band xác nhận

Dấu hiệu in-band:

1. Response trả về nội dung từ host attacker hoặc host nội bộ.
2. Response code/body thay đổi theo target (`127.0.0.1:22` vs `127.0.0.1:80`).
3. Có thể đọc endpoint quản trị nội bộ hoặc metadata.

## 5. Blind SSRF xác nhận

Dấu hiệu blind:

1. Chỉ thấy DNS query tới domain OAST.
2. Có DNS + HTTP callback.
3. Time-based chênh lệch khi gọi port mở/đóng.
4. Error pattern thay đổi theo target.

Lưu ý quan trọng:

- Chỉ có DNS callback vẫn là SSRF hợp lệ trong nhiều môi trường egress bị chặn HTTP.

## 6. Kỹ thuật reconnaissance nội bộ bằng SSRF

1. Port probing cơ bản qua HTTP scheme.
2. Dò private range theo batch nhỏ để tránh gây nhiễu.
3. Ưu tiên service phổ biến:
   - admin console,
   - metadata,
   - internal API,
   - cache/db HTTP interface.

## 7. Xác định mức độ kiểm soát URL

1. Full-control URL:
   - dễ khai thác nhất.
2. Host-only control:
   - cần tận dụng parser behavior hoặc redirect.
3. Path-only control:
   - dễ thành SSRF cục bộ vào service đã cố định host.
4. Scheme bị chặn:
   - thử chain qua redirect sang protocol khác nếu client hỗ trợ.

## 8. Tiêu chí chốt PoC detection

1. Chứng minh được server gửi request do attacker điều khiển.
2. Chứng minh được mức reachability (localhost/internal/cloud/external).
3. Có log bằng chứng:
   - request gốc,
   - callback OAST,
   - response hoặc side-channel liên quan.
