# PortSwigger JWT Labs Playbook

## Mục tiêu tài liệu

Chuẩn hóa cách thực hành và đối chiếu 8 lab JWT theo cùng framework:

1. Baseline
2. Detect hypothesis
3. Forge/re-sign
4. Impact validation

## Bảng mapping tổng quan

| Lab | Tên lab                                | Family lỗ hổng                     | Pattern chính            |
| --- | -------------------------------------- | ---------------------------------- | ------------------------ |
| 1   | Unverified signature                   | Signature verification flaw        | Pattern A                |
| 2   | Flawed signature verification (`none`) | Signature verification flaw        | Pattern B                |
| 3   | Weak signing key                       | Secret/key management flaw         | Pattern C                |
| 4   | `jwk` header injection                 | Header key abuse                   | Pattern D                |
| 5   | `jku` header injection                 | Header key abuse                   | Pattern D                |
| 6   | `kid` header path traversal            | Header key abuse                   | Pattern D                |
| 7   | Algorithm confusion (key exposed)      | Algorithm confusion                | Pattern E                |
| 8   | Algorithm confusion (no exposed key)   | Algorithm confusion + key recovery | Pattern E + key recovery |

## Playbook chi tiết theo lab

## Lab 1 - Unverified Signature

1. Baseline: user thường không vào được `/admin`.
2. Chỉnh `sub=administrator`, giữ nguyên signature.
3. Gửi request, xác nhận admin access.
4. Thực thi endpoint xóa user để chốt impact.

## Lab 2 - `alg=none`

1. Baseline như Lab 1.
2. Chỉnh payload, giữ `RS256` -> thất bại.
3. Đổi `alg=none`, bỏ signature (`header.payload.`).
4. Xác nhận bypass và thực thi hành động admin.

## Lab 3 - Weak HMAC Secret

1. Decode token, thấy `HS256`.
2. Crack secret (`secret1`) bằng JWT Editor hoặc Hashcat.
3. Tạo symmetric key, re-sign token với `sub=administrator`.
4. Xác nhận quyền admin và thao tác đặc quyền.

## Lab 4 - `jwk` Injection

1. Tạo RSA keypair attacker.
2. Chỉnh payload quyền admin.
3. Nhúng public key vào `jwk` header (Embedded JWK), ký lại.
4. Xác nhận server trust key do attacker cung cấp.

## Lab 5 - `jku` Injection

1. Tạo JWKS attacker-controlled.
2. Header: `jku` trỏ JWKS attacker + `kid` khớp key.
3. Payload admin, ký token bằng private key tương ứng.
4. Xác nhận bypass và thao tác admin.

## Lab 6 - `kid` Path Traversal

1. Đặt `kid` thành traversal tới file predictable (`/dev/null`).
2. Tạo symmetric key phù hợp nội dung file mục tiêu.
3. Payload admin, ký lại và gửi request.
4. Xác nhận truy cập admin thành công.

## Lab 7 - Confusion với key lộ

1. Thu public key từ `/jwks.json`.
2. Đổi `alg` từ `RS256` sang `HS256`.
3. Dùng public key (Base64 PEM/JWK-compatible) làm HMAC secret.
4. Re-sign payload admin, xác nhận bypass.

## Lab 8 - Confusion không lộ key

1. Thu hai JWT hợp lệ khác nhau.
2. Dùng `sig2n` suy ra key candidates.
3. Test tampered JWT để chọn key đúng.
4. Dùng key đúng làm HMAC secret, `alg=HS256`, re-sign payload admin.
5. Xác nhận bypass và chốt impact.

## Checklist xác nhận thành công cho mọi lab

1. Có baseline từ chối truy cập admin.
2. Có mutation/token forge cụ thể gây thay đổi outcome.
3. Có bằng chứng hành động đặc quyền thành công.
4. Có đề xuất phòng thủ tương ứng với family lỗ hổng.

## Liên kết writeup lab chi tiết

- [Lab 1 Writeup](../../Portswigger/Advanced topics/JWT/Lab 1/readme.md)
- [Lab 2 Writeup](../../Portswigger/Advanced topics/JWT/Lab 2/readme.md)
- [Lab 3 Writeup](../../Portswigger/Advanced topics/JWT/Lab 3/readme.md)
- [Lab 4 Writeup](../../Portswigger/Advanced topics/JWT/Lab 4/readme.md)
- [Lab 5 Writeup](../../Portswigger/Advanced topics/JWT/Lab 5/readme.md)
- [Lab 6 Writeup](../../Portswigger/Advanced topics/JWT/Lab 6/readme.md)
- [Lab 7 Writeup](../../Portswigger/Advanced topics/JWT/Lab 7/readme.md)
- [Lab 8 Writeup](../../Portswigger/Advanced topics/JWT/Lab 8/readme.md)

## Related Files

- [Attack Workflows and Patterns](11-attack-workflows-patterns.md)
- [Defense and Mitigation](13-defense-mitigation.md)
