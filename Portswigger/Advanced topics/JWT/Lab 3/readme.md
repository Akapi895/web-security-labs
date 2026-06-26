# Lab 3: JWT Authentication Bypass via Weak Signing Key

## Mục tiêu

Tìm được secret HMAC yếu dùng để ký JWT, tự ký token với `sub=administrator`, truy cập `/admin`, rồi xóa user `carlos`.

## Ý tưởng lỗi

Ứng dụng dùng thuật toán đối xứng (`HS256`) nhưng secret quá yếu và đoán/crack được. Khi biết secret, attacker có thể ký JWT hợp lệ với claim tùy ý.

## Writeup từng bước: từ detect đến exploit

### Bước 1: Baseline để xác nhận có kiểm soát quyền

1. Đăng nhập account thường, gửi request chứa JWT sang Repeater.
2. Thử truy cập `GET /admin` với token gốc, quan sát bị từ chối.

### Bước 2: Detect dấu hiệu weak signing key

1. Decode JWT và xác nhận header dùng `HS256`.
2. Đặt giả thuyết: secret ký quá yếu, có thể brute-force theo wordlist.
3. Chạy kiểm thử bằng JWT Editor (`Weak HMAC secret`) hoặc hashcat.

![attack-secret](images/attack.png)

Ví dụ với hashcat:

```bash
hashcat -a 0 -m 16500 eyJraWQiOiJkNDFhYTQzMi0yNDg1LTRmYmUtOTk4YS0wNDI1ODZjMTVhZGIiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJwb3J0c3dpZ2dlciIsImV4cCI6MTc3NzI3ODY5NCwic3ViIjoid2llbmVyIn0.vgdQF8HuIjmjBeALDXcqDgn5dm5Q09tlM3D5UFZRGXY wordlist.txt
```

![hashcat](images/hashcat.png)

4. Kết quả thu được secret: `secret1`.

### Bước 3: Exploit bằng token tự ký

1. Vào JWT Editor -> `New Symmetric Key` và tạo key với secret tìm được (`secret1`).

![newKey](images/newKey.png)

2. Quay lại token trong Repeater, sửa payload `sub` thành `administrator`.
3. Nhấn `Sign`, chọn key vừa tạo, ký với `HS256`.

![sign](images/sign.png)

4. Gửi request với token mới để vào `/admin`.
5. Gọi endpoint xóa user:

`/admin/delete?username=carlos`

6. Lab được solve.

## Vì sao detect này đáng tin cậy?

Vì bạn không đoán mò claim. Bạn chứng minh được secret thật bằng việc crack ra khóa ký, sau đó tạo chữ ký hợp lệ và được server chấp nhận.

## Gợi ý phòng thủ

1. Dùng secret ngẫu nhiên đủ mạnh (ít nhất 256-bit) cho HMAC.
2. Không dùng secret dạng từ điển hoặc secret ngắn.
3. Rotate key định kỳ và có cơ chế thu hồi key cũ.
4. Giám sát các dấu hiệu brute-force/JWT tampering bất thường.
