# Lab 6: JWT Authentication Bypass via `kid` Header Path Traversal

## Mục tiêu

Giả mạo JWT để nâng quyền thành `administrator`, truy cập `/admin`, sau đó xóa user `carlos`.

Tài khoản lab: `wiener:peter`.

## Ý tưởng lỗi

Server dùng giá trị `kid` trong JWT header để đọc key từ filesystem nhằm verify chữ ký. Nếu `kid` không được ràng buộc chặt, attacker có thể chèn path traversal để trỏ tới file có nội dung dự đoán được (ví dụ `/dev/null`). Khi đó attacker có thể tự ký token bằng secret tương ứng và bypass xác thực.

## Writeup từng bước: từ detect đến exploit

### Bước 1: Baseline để xác nhận có kiểm soát quyền

1. Đăng nhập bằng account thường `wiener:peter`.
2. Gửi request `GET /my-account` sang Burp Repeater.
3. Đổi path thành `GET /admin` và gửi.
4. Quan sát bị từ chối truy cập.

### Bước 2: Detect dấu hiệu có thể dính `kid` path traversal

1. Mở JWT và kiểm tra header có `kid`.
2. Đặt giả thuyết: `kid` đang được dùng như đường dẫn file để nạp key verify.
3. Nếu giả thuyết đúng, có thể điều khiển `kid` bằng path traversal đến file có nội dung biết trước.

Trong lab này, file mục tiêu là:

```text
../../../../../../../dev/null
```

### Bước 3: Chuẩn bị signing key phù hợp

1. Mở Burp JWT Editor -> tab Keys -> `New Symmetric Key`.
2. Nhấn `Generate` để tạo key dạng JWK.
3. Sửa trường `k` thành `AA==` (Base64 của null byte).

Lưu ý: đây là workaround do JWT Editor không cho ký với chuỗi rỗng trực tiếp.

4. Nhấn `OK` để lưu key.

### Bước 4: Sửa token và ký lại

1. Quay lại request `GET /admin` trong Repeater.
2. Mở tab JSON Web Token (extension-generated).
3. Sửa header JWT:

- Đổi `kid` thành `../../../../../../../dev/null`.

4. Sửa payload JWT:

- Đổi `sub` thành `administrator`.

5. Nhấn `Sign`, chọn symmetric key đã tạo ở bước trước.
6. Chọn `Don't modify header` để giữ nguyên giá trị `kid` đã chỉnh.
7. Gửi request.

Nếu vào được `/admin`, lỗ hổng đã được xác nhận.

### Bước 5: Exploit để solve lab

1. Trong response admin panel, tìm endpoint xóa user:

`/admin/delete?username=carlos`

2. Gửi request tới endpoint trên để hoàn thành lab.

## Vì sao detect này đáng tin cậy?

Vì bạn chứng minh theo chuỗi kiểm soát:

1. Account thường không có quyền admin.
2. Chỉ khi điều khiển `kid` sang đường dẫn traversal và ký theo key tương ứng thì token mới được chấp nhận.
3. Tác động thực tế được xác nhận bằng quyền admin và hành động xóa user.

## Gợi ý phòng thủ

1. Không dùng trực tiếp `kid` làm đường dẫn file.
2. Dùng mapping cố định `kid -> key` trong server-side key store.
3. Chặn path traversal bằng canonicalization và allowlist nghiêm ngặt.
4. Không dùng key/secret có nội dung dự đoán được hoặc fallback nguy hiểm.
5. Log và cảnh báo khi `kid` chứa ký tự/path bất thường.
