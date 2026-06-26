# JWT Defense and Mitigation

## Mục tiêu

Đưa ra bộ kiểm soát kỹ thuật có thể triển khai thực tế để loại bỏ các nhóm lỗ hổng JWT từ design đến implementation.

## Nguyên tắc phòng thủ cốt lõi

1. Never trust token input before full verification.
2. Pin thuật toán và key source theo policy server-side.
3. Validate claims theo ngữ cảnh nghiệp vụ, không chỉ verify chữ ký.
4. Quản trị secret/key lifecycle như tài sản mật mã cấp cao.

## 1) Signature verification controls

### Bắt buộc

1. Chỉ dùng API verify (không decode-only cho quyết định authz).
2. Cấm `alg=none` trong production.
3. Enforce expected algorithm per issuer/client.
4. Fail-closed khi thiếu signature hoặc algorithm không hợp lệ.

### Anti-pattern cần loại bỏ

- Tin `alg` từ token mà không đối chiếu policy.
- Fallback tự động sang thuật toán khác khi verify fail.

## 2) Key management controls

### Với HS256/HS384/HS512

1. Secret random tối thiểu 256-bit.
2. Không hardcode secret trong source.
3. Rotation định kỳ, version hóa key (`kid`) rõ ràng.
4. Không dùng default/example secret.

### Với RS/ES

1. Private key lưu trong KMS/HSM hoặc vault bảo mật.
2. Public key distribution qua kênh đã kiểm soát.
3. Không dùng chung key material cho mục đích không liên quan.

## 3) Header parameter controls (`jwk`, `jku`, `kid`)

1. Không tin `jwk` từ client trừ khi có policy pinning mạnh.
2. Không chấp nhận `jku` tùy ý; chỉ allowlist endpoint cố định.
3. Không dùng `kid` làm path hoặc query trực tiếp.
4. Dùng map nội bộ `kid -> key` thay vì resolver động không kiểm soát.
5. Log và cảnh báo header bất thường.

## 4) Algorithm confusion controls

1. Tách riêng verifier symmetric và asymmetric.
2. Kiểm tra nhất quán giữa `alg`, key type (`kty`) và key source.
3. Chặn tuyệt đối downgrade `RS/ES -> HS` ngoài policy.

## 5) Claim validation controls

| Claim/Logic  | Control bắt buộc                                   |
| ------------ | -------------------------------------------------- |
| `exp`        | Reject token hết hạn                               |
| `nbf`        | Reject token dùng sớm                              |
| `iss`        | Match issuer allowlist                             |
| `aud`        | Match audience của service hiện tại                |
| `sub`/`role` | Không dùng mù; đối chiếu quyền server-side khi cần |
| `jti`        | Replay protection/denylist cho luồng nhạy cảm      |

## 6) Token transport and storage controls

1. Chỉ truyền token qua HTTPS.
2. Nếu dùng cookie: `HttpOnly`, `Secure`, `SameSite` phù hợp.
3. Tránh lưu access token dài hạn trong storage dễ bị XSS.
4. Access token ngắn hạn, refresh token quản trị chặt.

## 7) Monitoring, detection, response

1. Theo dõi token verify failures theo cụm nguyên nhân.
2. Cảnh báo đột biến `alg` bất thường hoặc header key-management lạ.
3. Gắn correlation ID cho các quyết định auth.
4. Có playbook rotate/revoke key khi incident.

## 8) Security testing baseline (CI/CD)

Bộ test regression nên bao gồm:

1. Tamper payload without resign -> phải fail.
2. `alg=none` -> phải fail.
3. `RS256` token đổi sang `HS256` -> phải fail.
4. Header chứa `jwk`/`jku`/`kid` bất thường -> phải fail theo policy.
5. Token sai `iss`/`aud`/`exp` -> phải fail.

## Checklist triển khai nhanh

| Kiểm soát                          | Mức ưu tiên | Trạng thái |
| ---------------------------------- | ----------- | ---------- |
| Enforce verify + pinned algorithm  | Critical    |            |
| Strong key/secret lifecycle        | Critical    |            |
| Disable unsafe header key sourcing | Critical    |            |
| Claim validation policy            | High        |            |
| Monitoring + alerting              | High        |            |
| Security regression tests          | High        |            |

## Related Files

- [Signature Verification Flaws](02-signature-verification-flaws.md)
- [Algorithm Confusion](07-algorithm-confusion.md)
- [Claim Validation Logic](09-claim-validation-logic.md)
