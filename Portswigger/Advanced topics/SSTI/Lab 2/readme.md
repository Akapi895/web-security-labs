# Lab: Basic server-side template injection (code context)

## Mục tiêu

Lợi dụng Tornado template injection trong `blog-post-author-display` để thực thi lệnh và xóa `morale.txt` của Carlos.

## Ý tưởng lỗi

Giá trị `blog-post-author-display` được chèn trực tiếp vào template hiển thị tên tác giả comment. Nếu thoát được khỏi biểu thức `{{ ... }}`, ta có thể inject thêm syntax của Tornado.

## Writeup từng bước: từ detect đến exploit

### Bước 1: Tìm request kiểm soát hiển thị

1. Đăng nhập bằng `wiener:peter`.
2. Post một comment trên blog.
3. Trong Burp, tìm request `POST /my-account/change-blog-post-author-display`.
4. Đây là request thay đổi giá trị hiển thị tên comment, nên là điểm kiểm tra tốt nhất.

### Bước 2: Detect SSTI

1. Thử phá vỡ biểu thức hiện tại bằng payload:

`blog-post-author-display=user.name}}{{7*7}}`

2. Nếu phần tên hiển thị đổi thành `49`, template đang evaluate expression của người dùng.

### Bước 3: Xác nhận có thể thực thi lệnh

1. Tornado dùng `{% ... %}` cho block Python.
2. Import `os` rồi dùng `popen()` để chạy lệnh:

`{% import os %}{{os.popen('whoami').read()}}`

3. Kết quả trả về `carlos` xác nhận có thể thực thi command trên server.

### Bước 4: Exploit để solve lab

1. Gửi payload xóa file:

`blog-post-author-display=user.name}}{% import os %}{{os.popen('rm /home/carlos/morale.txt').read()}}`

2. Reload trang chứa comment để template được render lại và lab được solve.

## Vì sao detect này đáng tin cậy?

Chuỗi `}}` thoát khỏi expression hiện tại, còn `{{7*7}}` và `os.popen()` chứng minh ta không chỉ chèn text mà đã điều khiển luồng render của Tornado.

## Gợi ý phòng thủ

1. Không ghép trực tiếp dữ liệu người dùng vào template.
2. Escape output theo đúng ngữ cảnh trước khi render.
3. Tách dữ liệu cấu hình hiển thị khỏi syntax của template engine.
