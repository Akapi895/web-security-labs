# JWT Security Overview

## JWT là gì và vì sao quan trọng?

JSON Web Token (JWT) là định dạng chuẩn để truyền thông tin (claims) giữa các hệ thống dưới dạng JSON có chữ ký số. Trong thực tế web hiện đại, JWT thường được dùng cho:

- Authentication (xác thực danh tính người dùng)
- Session management (duy trì phiên theo kiểu stateless)
- Authorization (ủy quyền theo role/scope)
- Service-to-service token giữa API gateway, microservices, mobile app, SPA

Vì JWT thường nằm trong luồng xác thực/phân quyền, một lỗi xử lý JWT có thể dẫn tới chiếm quyền tài khoản hoặc takeover toàn bộ ứng dụng.

## Cấu trúc token

JWT thường ở dạng:

`Base64Url(Header).Base64Url(Payload).Base64Url(Signature)`

### Header

Chứa metadata của token, ví dụ:

- `alg`: thuật toán ký (`HS256`, `RS256`, `ES256`, ...)
- `kid`: key identifier
- `jwk`: public key nhúng trực tiếp
- `jku`: URL trỏ tới JWKS

### Payload

Chứa claims, gồm:

- Claims chuẩn: `iss`, `sub`, `aud`, `exp`, `nbf`, `iat`, `jti`
- Claims nghiệp vụ: `role`, `scope`, `is_admin`, `tenant_id`, ...

### Signature

Là phần đảm bảo tính toàn vẹn của header/payload. Nếu thay đổi 1 byte ở header/payload thì signature hợp lệ phải thay đổi tương ứng.

## JWT, JWS, JWE

| Thành phần | Mục đích         | Đặc trưng                               |
| ---------- | ---------------- | --------------------------------------- |
| JWT        | Định dạng claims | Khái niệm tổng quát                     |
| JWS        | Ký số            | Nội dung thường đọc được (không mã hóa) |
| JWE        | Mã hóa           | Nội dung đã mã hóa                      |

Trong pentest thực tế, "JWT" phần lớn là JWS.

## Mô hình tin cậy và điểm đứt gãy

JWT an toàn khi và chỉ khi server:

1. Verify signature đúng thuật toán và đúng key.
2. Không tin dữ liệu điều khiển bởi client trước khi verify.
3. Validate logic claims (`exp`, `iss`, `aud`, ...).

Lỗ hổng JWT xuất hiện khi một trong ba lớp trên bị triển khai sai.

## Phân loại lỗ hổng JWT

| Nhóm lỗ hổng                 | Bản chất kỹ thuật                  | Ví dụ                            |
| ---------------------------- | ---------------------------------- | -------------------------------- |
| Signature verification flaws | Verify chữ ký không đúng cách      | Unverified signature, `alg=none` |
| Secret/key management flaws  | Secret yếu hoặc key lộ             | Weak HMAC secret, key leakage    |
| Header parameter abuse       | Tin tham số key từ token           | `jwk`, `jku`, `kid` abuse        |
| Algorithm confusion          | Nhầm ngữ cảnh symmetric/asymmetric | RS256 -> HS256                   |
| Claim/logic validation flaws | Validate claims thiếu chặt chẽ     | Bỏ qua `exp`, `iss`, `aud`       |

## Tác động bảo mật

| Mức tác động          | Mô tả                                   |
| --------------------- | --------------------------------------- |
| Authentication bypass | Đăng nhập giả mạo user khác             |
| Privilege escalation  | Leo thang từ user lên admin             |
| Account takeover      | Chiếm quyền tài khoản mục tiêu          |
| Cross-tenant access   | Truy cập dữ liệu tenant khác            |
| Full compromise       | Chi phối luồng phân quyền toàn hệ thống |

## Lộ trình học/đánh giá khuyến nghị

1. Nắm cấu trúc và vòng đời JWT.
2. Chạy workflow detection chuẩn.
3. Thực hành từng family attack.
4. Tổng hợp pattern khai thác.
5. Áp dụng checklist phòng thủ.

## Related Files

- [Detection Workflow](01-detection-workflow.md)
- [Signature Verification Flaws](02-signature-verification-flaws.md)
- [Weak HMAC Secrets](03-weak-hmac-secrets.md)
- [JWK Header Injection](04-jwk-header-injection.md)
- [JKU Header Injection](05-jku-header-injection.md)
- [KID Manipulation](06-kid-manipulation.md)
- [Algorithm Confusion](07-algorithm-confusion.md)
- [Key Recovery Techniques](08-key-recovery-techniques.md)
- [Claim Validation Logic](09-claim-validation-logic.md)
- [Tools and Automation](10-tools-automation.md)
- [Attack Workflows and Patterns](11-attack-workflows-patterns.md)
- [PortSwigger Labs Playbook](12-labs-portswigger-playbook.md)
- [Defense and Mitigation](13-defense-mitigation.md)
- [Lab Design and Agent Training](14-lab-design-and-agent-training.md)
