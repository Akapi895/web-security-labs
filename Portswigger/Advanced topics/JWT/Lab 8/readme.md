# Lab 8: JWT Authentication Bypass via Algorithm Confusion with No Exposed Key

## Mục tiêu

Khai thác algorithm confusion trong bối cảnh không có endpoint lộ public key trực tiếp, từ đó nâng quyền lên `administrator`, truy cập `/admin`, rồi xóa user `carlos`.

Tài khoản lab: `wiener:peter`.

## Ý tưởng lỗi

Ứng dụng ký JWT bằng RSA, nhưng xác minh sai cách nên có thể bị ép sang `HS256` (đối xứng). Dù không lộ public key qua endpoint kiểu `/jwks.json`, attacker vẫn có thể suy ra public key từ hai token hợp lệ do server phát hành, sau đó dùng public key đó làm HMAC secret để ký token giả.

## Writeup từng bước: từ detect đến exploit

### Bước 1: Baseline để xác nhận có kiểm soát quyền

1. Đăng nhập bằng account thường `wiener:peter`.
2. Gửi `GET /my-account` sang Burp Repeater.
3. Đổi path thành `GET /admin` và gửi.
4. Quan sát bị từ chối truy cập.

### Bước 2: Thu thập 2 JWT hợp lệ từ server

1. Copy JWT session hiện tại và lưu lại thành `token1`.
2. Logout, rồi login lại để server phát token mới.
3. Copy JWT session mới và lưu lại thành `token2`.

Mục đích: dùng 2 chữ ký hợp lệ để suy ra modulus/public key phía server.

### Bước 3: Suy ra public key bằng công cụ `sig2n`

Chạy lệnh sau trong terminal:

```bash
docker run --rm -it portswigger/sig2n <token1> <token2>
```

Kết quả thường trả về:

1. Một hoặc nhiều giá trị `n` khả dĩ.
2. Public key ở định dạng Base64 cho X.509 và PKCS1.
3. Tampered JWT tương ứng từng candidate key.

### Bước 4: Xác nhận candidate key đúng

1. Lấy tampered JWT từ candidate X.509 đầu tiên.
2. Quay lại request trong Repeater, đổi path về `GET /my-account`.
3. Thay session cookie bằng tampered JWT và gửi request.
4. Nếu nhận `200` và vào được trang account, candidate key đó là đúng.
5. Nếu nhận `302` về `/login` và cookie bị xóa, candidate đó sai. Lặp lại với candidate khác.

### Bước 5: Tạo symmetric key độc hại trong JWT Editor

1. Từ output terminal, copy đúng chuỗi Base64 của X.509 key đã xác nhận đúng (không copy tampered JWT).
2. Vào Burp JWT Editor -> tab Keys -> `New Symmetric Key` -> `Generate`.
3. Thay trường `k` bằng chuỗi Base64 X.509 vừa copy.
4. Lưu key.

### Bước 6: Sửa token và ký lại để lên admin

1. Quay lại request Repeater, đổi path thành `GET /admin`.
2. Mở tab JSON Web Token (extension-generated).
3. Trong header, đặt `alg` thành `HS256`.
4. Trong payload, đổi `sub` thành `administrator`.
5. Nhấn `Sign`, chọn symmetric key ở bước 5.
6. Chọn `Don't modify header` để giữ nguyên `alg=HS256`.
7. Gửi request.

Nếu truy cập được `/admin`, lỗ hổng đã được xác nhận.

### Bước 7: Exploit để solve lab

1. Trong response admin panel, lấy endpoint xóa user:

`/admin/delete?username=carlos`

2. Gửi request tới endpoint trên để hoàn thành lab.

## Vì sao detect này đáng tin cậy?

Vì bạn xác minh theo chuỗi logic đầy đủ:

1. Baseline không có quyền admin.
2. Suy ra public key từ dữ liệu chữ ký thật do server phát hành.
3. Đổi thuật toán sang `HS256` và ký bằng key vừa suy ra được server chấp nhận.

Điều này chỉ ra rõ lỗ hổng algorithm confusion, không phải false positive.

## Gợi ý phòng thủ

1. Ràng buộc cứng thuật toán theo issuer/key, không cho client tự quyết `alg`.
2. Tách biệt hoàn toàn luồng xác minh asymmetric và symmetric.
3. Kiểm tra nhất quán giữa `alg`, `kty`, và loại khóa expected.
4. Chặn downgrade từ `RS256` sang `HS256` trong cùng trust context.
5. Bổ sung security test cho các trường hợp key confusion và algorithm confusion.
