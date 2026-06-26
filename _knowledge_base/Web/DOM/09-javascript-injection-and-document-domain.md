# Chèn JavaScript và thao túng document.domain dựa trên DOM

## Chèn JavaScript dựa trên DOM

### Định nghĩa

Lỗ hổng này xuất hiện khi dữ liệu do attacker kiểm soát bị thực thi như mã JavaScript trong phiên trình duyệt của nạn nhân.

### Các điểm nhận chính

- `eval()`
- `Function()`
- `setTimeout()` / `setInterval()` với đối số dạng chuỗi
- `setImmediate()`, `msSetImmediate()`
- `execCommand()`, `execScript()`
- `range.createContextualFragment()`
- `crypto.generateCRMFRequest()`

### Tác động

Mã do attacker đưa vào có thể:

1. Đánh cắp session hoặc thông tin xác thực.
2. Thực hiện hành động trong ngữ cảnh của nạn nhân.
3. Thu thập dữ liệu nhạy cảm qua lạm dụng logic phía trình duyệt.

### Trọng tâm phòng ngừa

1. Không bao giờ thực thi chuỗi không đáng tin cậy như mã.
2. Thay cơ chế thực thi dạng chuỗi bằng callback có cấu trúc và luồng điều khiển chặt chẽ.
3. Kiểm tra và ràng buộc toàn bộ dữ liệu đầu vào trước mọi xử lý có liên quan thực thi script.

## Thao túng document.domain dựa trên DOM

### Định nghĩa

Lỗi này xảy ra khi dữ liệu không đáng tin cậy được dùng để đặt `document.domain`, làm thay đổi hành vi quan hệ origin.

### Vì sao quan trọng

`document.domain` ảnh hưởng cơ chế nới lỏng same-origin policy. Nếu attacker ép thay đổi domain về parent domain chung hoặc domain liên quan yếu bảo mật, ranh giới tương tác giữa các trang có thể bị phá vỡ.

### Điểm nhận

- `document.domain`

### Mô hình tác động

1. Ranh giới origin của trang mục tiêu bị suy yếu.
2. Trang do attacker kiểm soát trong domain context tương thích có thể tương tác với nội dung đáng lẽ được bảo vệ.
3. Trong một số kịch bản, mức độ khai thác có thể tiệm cận tác động kiểu XSS.

### Trọng tâm phòng ngừa

1. Không lấy `document.domain` từ dữ liệu không đáng tin cậy.
2. Tránh nới lỏng domain động nếu không thật sự bắt buộc.
3. Loại bỏ mẫu cũ phụ thuộc vào cơ chế nới lỏng same-origin trên phạm vi rộng.

## Tệp liên quan

- [DOM XSS](05-dom-xss.md)
- [Taint flow, nguồn và điểm nhận](02-taint-flow-sources-sinks.md)
- [Phòng thủ và giảm thiểu](14-defense-mitigation.md)
