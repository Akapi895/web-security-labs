# Lab 7: JWT Authentication Bypass via Algorithm Confusion

## Mục tiêu

Khai thác lỗi algorithm confusion để nâng quyền lên `administrator`, truy cập `/admin`, sau đó xóa user `carlos`.

Tài khoản lab: `wiener:peter`.

## Ý tưởng lỗi

Ứng dụng dùng cặp khóa RSA để xử lý JWT, nhưng triển khai sai khi cho phép đổi thuật toán từ bất đối xứng (`RS256`) sang đối xứng (`HS256`) và tái sử dụng key material không đúng ngữ cảnh. Khi đó attacker có thể lấy public key của server rồi dùng chính public key đó làm secret HMAC để ký token giả.

## Writeup từng bước: từ detect đến exploit

### Bước 1: Baseline để xác nhận có kiểm soát quyền

1. Đăng nhập bằng account thường `wiener:peter`.
2. Gửi `GET /my-account` sang Burp Repeater.
3. Đổi path thành `GET /admin` và gửi.
4. Quan sát bị từ chối truy cập.

### Bước 2: Detect dấu hiệu algorithm confusion

1. Kiểm tra JWT header, thấy token ban đầu dùng `RS256`.
2. Truy cập endpoint chuẩn `GET /jwks.json` và thấy server công khai public key dưới dạng JWK.
3. Đặt giả thuyết: nếu server không khóa chặt thuật toán theo key type, có thể ép `alg=HS256` và dùng public key làm HMAC secret.

Nếu giả thuyết đúng, đây chính là algorithm confusion.

### Bước 3: Lấy public key và chuẩn bị signing key độc hại

1. Copy JWK object từ mảng `keys` trong `/jwks.json` (chỉ copy object, không copy ký tự thừa).
2. Vào Burp JWT Editor -> tab Keys -> `New RSA Key`.
3. Chọn định dạng JWK, paste JWK vừa copy và lưu key.
4. Right-click key vừa tạo -> `Copy Public Key as PEM`.
5. Sang tab Decoder, Base64 encode PEM này và copy kết quả.
6. Quay lại JWT Editor -> `New Symmetric Key` -> `Generate`.
7. Thay giá trị trường `k` bằng chuỗi Base64 của PEM ở bước 5.
8. Lưu symmetric key.

### Bước 4: Sửa token và ký lại

1. Quay lại request `GET /admin` trong Repeater.
2. Mở tab JSON Web Token (extension-generated).
3. Sửa header: đổi `alg` thành `HS256`.
4. Sửa payload: đổi `sub` thành `administrator`.
5. Nhấn `Sign`, chọn symmetric key đã tạo ở bước trước.
6. Chọn `Don't modify header` để giữ nguyên `alg=HS256`.
7. Gửi request.

Nếu truy cập được `/admin`, lỗ hổng đã được xác nhận.

### Bước 5: Exploit để solve lab

1. Trong response admin panel, tìm endpoint xóa user:

`/admin/delete?username=carlos`

2. Gửi request tới endpoint trên để hoàn thành lab.

## Vì sao detect này đáng tin cậy?

Vì chuỗi kiểm chứng thể hiện rõ nguyên nhân kỹ thuật:

1. Token gốc dùng `RS256` (asymmetric).
2. Public key của server lộ qua `jwks.json`.
3. Đổi sang `HS256` và ký bằng key giả lập từ public key lại được chấp nhận.

Điều đó chứng minh server đang nhầm lẫn cách xử lý thuật toán và key type.

## Gợi ý phòng thủ

1. Ràng buộc cứng thuật toán theo từng issuer/key, không tin `alg` do client cung cấp.
2. Tách riêng đường xử lý HMAC và RSA/ECDSA, không dùng chung key material.
3. Khi xác minh, kiểm tra nhất quán giữa `alg`, `kty`, và loại khóa expected.
4. Không cho phép downgrade từ asymmetric sang symmetric trong cùng trust context.
5. Bổ sung test bảo mật cho các case algorithm confusion.
