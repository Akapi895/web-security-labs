# Lab: Server-side template injection in an unknown language with a documented exploit

## Mục tiêu

Nhận diện engine là Handlebars, dùng exploit đã được công bố để thực thi lệnh, rồi xóa `morale.txt` của Carlos.

## Ý tưởng lỗi

Endpoint `message` render lỗi theo cú pháp template. Khi fuzz nhiều syntax khác nhau mà server trả lỗi đặc trưng, ta có thể xác định engine, rồi tìm exploit phù hợp trên tài liệu/cộng đồng.

## Writeup từng bước: từ detect đến exploit

### Bước 1: Detect engine

1. Truy cập `GET /product?productId=1`.
2. Quan sát điều hướng về `/?message=Unfortunately%20this%20product%20is%20out%20of%20stock`.
3. Fuzz vào `message` bằng nhiều ký tự template khác nhau, ví dụ:

`${{<%[%'"}}%\\`

4. Error message đặc trưng cho biết website dùng Handlebars.

### Bước 2: Xác nhận có thể điều khiển template

1. Thử payload đơn giản:

`{{this}}`

2. Nếu thấy `[object Object]`, nghĩa là template đang render object của Handlebars chứ không chỉ hiển thị chuỗi tĩnh.

### Bước 3: Exploit để chạy lệnh

1. Tìm exploit Handlebars SSTI đã công bố và chỉnh phần command thành:

`require('child_process').exec('rm /home/carlos/morale.txt')`

2. Payload hoàn chỉnh dùng cấu trúc `#with` và `lookup` để dựng constructor rồi gọi command.
3. URL-encode payload rồi đặt vào `message`.
4. Load URL để thực thi và solve lab.

## Vì sao detect này đáng tin cậy?

Chuỗi fuzz đa cú pháp giúp định danh Handlebars từ error behavior. Sau đó `{{this}}` cho thấy object bị render trực tiếp, nên exploit public dành cho Handlebars là lựa chọn đúng hướng.

## Gợi ý phòng thủ

1. Không render input người dùng bằng template engine có khả năng thực thi.
2. Dùng escaping hoặc render text thuần nếu chỉ cần hiển thị nội dung.
3. Vô hiệu hóa helper/cú pháp nguy hiểm và không cho template tự do truy cập object nhạy cảm.
