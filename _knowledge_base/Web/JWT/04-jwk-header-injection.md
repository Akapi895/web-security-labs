# JWK Header Injection

## Bản chất kỹ thuật

JWS cho phép header chứa tham số `jwk` (public key). Lỗ hổng xảy ra khi server tin trực tiếp khóa do client nhúng trong token thay vì chỉ tin key từ trust store nội bộ.

Khi đó attacker:

1. Tự tạo keypair.
2. Chỉnh payload claim (ví dụ `sub=administrator`).
3. Nhúng public key vào `jwk` header.
4. Ký token bằng private key tương ứng.

Server verify thành công theo key do attacker cung cấp -> bypass.

## Điều kiện khai thác

- Ứng dụng dùng thuật toán bất đối xứng (`RS256`/`ES256`).
- Verifier chấp nhận `jwk` header mà không pin/allowlist key.
- Authorization phụ thuộc claim trong token.

## Workflow detect -> exploit

### Bước 1: Baseline

Xác nhận user thường không truy cập được endpoint admin.

### Bước 2: Kiểm tra khả năng trust `jwk`

1. Tạo RSA key mới.
2. Chỉnh claim quyền trong payload.
3. Dùng tính năng `Embedded JWK` để chèn public key vào header.
4. Ký lại token bằng private key vừa tạo.

### Bước 3: Xác nhận impact

Gửi token và kiểm tra hành động đặc quyền (không chỉ status code).

## Dấu hiệu nhận biết

| Dấu hiệu                                          | Diễn giải                               |
| ------------------------------------------------- | --------------------------------------- |
| Token chỉ thành công khi có `jwk` nhúng           | Server đang trust key từ client         |
| Thay key trong header làm thay đổi outcome verify | Key selection không neo vào trust store |

## Mapping PortSwigger lab

- Lab 4: JWT authentication bypass via `jwk` header injection

## Anti-pattern trong code

1. Dùng `jwk` từ header như nguồn key mặc định.
2. Không kiểm tra thumbprint/kid mapping trong kho khóa nội bộ.
3. Trộn lẫn logic parse header và trust policy.

## Phòng thủ

1. Không tin `jwk` từ token trừ khi có policy kiểm chứng nghiêm ngặt.
2. Chỉ lấy key verify từ trust store/JWKS endpoint đã allowlist.
3. Bắt buộc ràng buộc `iss` -> key set -> `kid` mapping.
4. Ghi log mọi token có `jwk`/`x5c` bất thường.

## Related Files

- [JKU Header Injection](05-jku-header-injection.md)
- [KID Manipulation](06-kid-manipulation.md)
- [Defense and Mitigation](13-defense-mitigation.md)
