# Lab 5: JWT Authentication Bypass via `jku` Header Injection

## Mục tiêu

Chiếm quyền `administrator` bằng cách khiến server lấy khóa xác thực JWT từ nguồn do attacker kiểm soát (qua header `jku`), sau đó truy cập `/admin` và xóa user `carlos`.

## Ý tưởng lỗi

Ứng dụng cho phép JWT header chứa `jku` để chỉ tới JWKS URL. Nếu server không kiểm soát chặt domain/allowlist, attacker có thể:

1. Tự tạo cặp khóa RSA.
2. Public key lên một JWKS do mình kiểm soát.
3. Trỏ `jku` tới JWKS đó.
4. Ký token bằng private key tương ứng.

Kết quả: server verify hợp lệ theo key của attacker và tin luôn claim đã bị sửa.

## Writeup từng bước: từ detect đến exploit

### Bước 1: Baseline để xác nhận có kiểm soát quyền

1. Đăng nhập bằng tài khoản thường.
2. Gửi request `GET /my-account` sang Burp Repeater.
3. Đổi path thành `GET /admin` và gửi.
4. Quan sát bị từ chối truy cập.

Mục đích: xác nhận ban đầu account thường không có quyền admin.

### Bước 2: Detect dấu hiệu có thể dính `jku` injection

1. Mở JWT trong request và kiểm tra header có dùng cơ chế bất đối xứng (`RS256`).
2. Xem header có `kid` và khả năng server tra key theo JWKS.
3. Đặt giả thuyết: nếu thêm `jku` trỏ tới JWKS của mình, server có thể lấy key từ đó để verify.

Đây là detect có định hướng, không phải thử mù.

### Bước 3: Chuẩn bị hạ tầng kiểm chứng (JWKS độc hại)

1. Trong Burp JWT Editor, tạo RSA key mới: `New RSA Key` -> `Generate`.
2. Mở Exploit Server của lab.
3. Tạo JWKS rỗng:

```json
{
  "keys": []
}
```

4. Từ JWT Editor, copy public key dưới dạng JWK (`Copy Public Key as JWK`).
5. Dán JWK vào mảng `keys`, rồi lưu exploit.

Ví dụ JWKS:

```json
{
  "keys": [
    {
      "kty": "RSA",
      "e": "AQAB",
      "kid": "<kid-cua-ban>",
      "n": "<modulus-cua-ban>"
    }
  ]
}
```

### Bước 4: Test xác nhận lỗ hổng

1. Quay lại request `GET /admin` trong Repeater.
2. Mở tab JWT Editor (extension-generated).
3. Sửa header JWT:

- Đặt `kid` trùng `kid` trong JWK bạn vừa publish.
- Thêm `jku` là URL JWKS trên Exploit Server.

4. Sửa payload: đổi `sub` thành `administrator`.
5. Nhấn Sign, chọn RSA key đã tạo.
6. Giữ tùy chọn `Don't modify header` để không bị ghi đè phần `jku`/`kid`.
7. Gửi request.

Nếu vào được `/admin`, bạn đã xác nhận lỗ hổng `jku` header injection.

### Bước 5: Exploit để solve lab

1. Trong response admin panel, tìm đường dẫn xóa user carlos:

`/admin/delete?username=carlos`

2. Gửi request tới endpoint này để hoàn thành lab.

## Vì sao detect này đáng tin cậy?

Vì bạn kiểm chứng theo chuỗi có kiểm soát:

1. Chứng minh baseline không có quyền.
2. Chứng minh server chấp nhận token có nguồn key do attacker chỉ định qua `jku`.
3. Chứng minh tác động thật bằng leo thang quyền và thực thi hành động admin.

## Gợi ý phòng thủ

1. Không cho phép `jku` tùy ý; chỉ cho phép URL trong allowlist cứng.
2. Không tin key material từ token nếu chưa qua chính sách tin cậy.
3. Ràng buộc chặt `iss`, `aud`, thuật toán ký và mapping `kid`.
4. Cảnh báo khi token chứa header bất thường (`jku`, `jwk`, `x5u`) hoặc domain lạ.
