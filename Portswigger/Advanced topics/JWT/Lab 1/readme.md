# Lab 1: JWT Authentication Bypass via Unverified Signature

## Mục tiêu

Nâng quyền lên `administrator` bằng JWT đã bị sửa claim nhưng không ký lại, sau đó truy cập `/admin` và xóa user `carlos`.

## Ý tưởng lỗi

Server không verify chữ ký JWT (hoặc verify sai cách), nên token bị chỉnh payload vẫn được chấp nhận.

## Writeup từng bước: từ detect đến exploit

### Bước 1: Baseline để xác nhận có kiểm soát quyền

1. Đăng nhập bằng tài khoản thường (ví dụ `wiener:peter`).
2. Gửi request `GET /my-account` sang Burp Repeater.
3. Đổi path thành `GET /admin` và gửi.
4. Quan sát bị từ chối truy cập.

Mục đích: xác nhận ban đầu account thường không có quyền admin.

### Bước 2: Detect lỗi unverified signature

1. Decode JWT từ cookie session.
2. Giữ nguyên header, chỉ đổi payload claim `sub` từ `wiener` thành `administrator`.
3. Không ký lại token, giữ nguyên phần signature cũ.
4. Gửi lại request với token mới.

Nếu server vẫn cho vào `/admin`, đây là dấu hiệu rõ ràng của lỗi không kiểm chữ ký.

### Bước 3: Exploit để solve lab

1. Truy cập `/admin` bằng token đã sửa.
2. Gọi endpoint xóa user:

`/admin/delete?username=carlos`

3. Lab được solve.

## Vì sao detect này đáng tin cậy?

Vì về nguyên tắc, chỉ cần đổi payload thì chữ ký cũ phải không còn hợp lệ. Nếu server vẫn chấp nhận, nghĩa là cơ chế verify đang bị bỏ qua hoặc triển khai sai.

## Gợi ý phòng thủ

1. Bắt buộc verify chữ ký cho mọi JWT trước khi đọc claim.
2. Tách rõ bước verify và bước authorize, không dùng claim khi verify chưa pass.
3. Dùng thư viện JWT chuẩn, không tự viết logic verify thủ công.
4. Log và chặn token có dấu hiệu bị chỉnh sửa nhưng signature không tương ứng.
