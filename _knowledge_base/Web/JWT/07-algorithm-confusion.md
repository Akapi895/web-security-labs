# Algorithm Confusion (RS/ES -> HS)

## Bản chất kỹ thuật

Algorithm confusion xảy ra khi server không ràng buộc chặt thuật toán và loại khóa trong quá trình verify. Kịch bản kinh điển:

1. Ứng dụng phát token bằng `RS256` (asymmetric).
2. Attacker đổi header sang `HS256`.
3. Attacker dùng public key của server làm HMAC secret để ký token.
4. Server verify pass do dùng cùng API verify cho cả asymmetric và symmetric mà thiếu guard.

## Điều kiện khai thác

| Điều kiện                    | Mô tả                                                |
| ---------------------------- | ---------------------------------------------------- |
| Token gốc dùng RS/ES         | Có public key tương ứng                              |
| Server không khóa cứng `alg` | Tin `alg` từ token hoặc fallback sai                 |
| Public key lấy được          | Từ `jwks.json`, TLS cert, leak, hoặc suy ra từ token |

## Nguồn public key thường gặp

1. `/.well-known/jwks.json` hoặc `/jwks.json`
2. TLS certificate/public endpoint
3. Config/source leak
4. Suy ra từ nhiều token hợp lệ (kỹ thuật sig2n)

## Workflow detect -> exploit

### Bước 1: Baseline

User thường không có quyền admin.

### Bước 2: Xác minh giả thuyết confusion

1. Thu thập public key server.
2. Đổi `alg` trong header thành `HS256`.
3. Tạo symmetric key từ public key (định dạng đúng như verifier kỳ vọng).
4. Chỉnh claim quyền trong payload và ký lại token.

### Bước 3: Xác nhận tác động

Gửi request, kiểm tra hành vi đặc quyền thực tế.

## Case có key lộ và không lộ

1. **Key lộ trực tiếp**: lấy từ JWKS endpoint, tấn công nhanh.
2. **Không lộ key**: suy ra key candidate từ 2 token hợp lệ, test candidate đến khi pass.

## Mapping PortSwigger labs

- Lab 7: Algorithm confusion với key lộ qua JWKS
- Lab 8: Algorithm confusion không lộ key trực tiếp (suy key từ token)

## Sai lầm phổ biến ở phía ứng dụng

1. Dùng chung hàm verify cho nhiều thuật toán nhưng không enforce expected alg.
2. Không kiểm tra tương thích giữa `alg` và `kty`.
3. Cho phép downgrade từ RS/ES sang HS trong cùng trust context.

## Phòng thủ

1. Pin thuật toán theo issuer/key-id server-side.
2. Tách riêng verifier cho symmetric và asymmetric.
3. Bắt buộc kiểm tra nhất quán `alg` + key type + key source.
4. Chặn mọi token có thuật toán ngoài allowlist của endpoint.
5. Thêm unit/integration tests cho confusion cases.

## Related Files

- [Key Recovery Techniques](08-key-recovery-techniques.md)
- [PortSwigger Labs Playbook](12-labs-portswigger-playbook.md)
- [Defense and Mitigation](13-defense-mitigation.md)
