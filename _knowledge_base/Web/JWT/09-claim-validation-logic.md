# Claim Validation and Authorization Logic Flaws

## Bản chất kỹ thuật

Ngay cả khi signature được verify đúng, hệ thống vẫn có thể bị compromise nếu logic kiểm tra claims không chặt chẽ.

JWT security cần cả hai lớp:

1. Cryptographic validation (signature/key/algorithm)
2. Business validation (claims + context)

Thiếu lớp (2) sẽ tạo ra logic flaws.

## Claims quan trọng cần kiểm

| Claim | Ý nghĩa         | Rủi ro khi bỏ kiểm                        |
| ----- | --------------- | ----------------------------------------- |
| `exp` | Expiration time | Token hết hạn vẫn dùng được               |
| `nbf` | Not-before time | Token dùng trước thời điểm hợp lệ         |
| `iat` | Issued-at time  | Replay/token age bất thường               |
| `iss` | Issuer          | Token từ issuer giả mạo được chấp nhận    |
| `aud` | Audience        | Token của service A dùng được ở service B |
| `sub` | Subject         | Impersonation nếu authorize sai           |
| `jti` | Token id        | Replay nếu thiếu denylist/nonce policy    |

## Mẫu lỗi triển khai phổ biến

1. Chỉ kiểm signature, không kiểm `iss` và `aud`.
2. Cho phép clock skew quá lớn làm vô hiệu kiểm `exp`/`nbf`.
3. Dùng claim `role` từ token để phân quyền mà không ràng buộc session/user context.
4. Không kiểm tenant boundary (`tenant_id`, `org_id`) trong hệ multi-tenant.
5. Không có cơ chế revoke/replay protection cho token dài hạn.

## Điều kiện khai thác

| Lỗi                 | Điều kiện để khai thác                        |
| ------------------- | --------------------------------------------- |
| Bỏ kiểm `exp`       | Attacker có token cũ bị lộ                    |
| Bỏ kiểm `iss`/`aud` | Có token hợp lệ từ hệ thống khác              |
| Role-based trust mù | Có thể forge/tamper token hợp lệ              |
| Replay              | Token bị đánh cắp và không có context binding |

## Workflow kiểm thử claim logic

### Bước 1: Token lifetime tests

1. Dùng token đã hết hạn hoặc chỉnh `exp` về quá khứ.
2. Kiểm tra server còn chấp nhận không.

### Bước 2: Issuer/Audience tests

1. Thay `iss` và `aud` bằng giá trị sai.
2. Kiểm tra endpoint còn cho truy cập không.

### Bước 3: Authorization consistency tests

1. Chỉnh claim quyền (`role`, `scope`, `sub`) theo token đã sign hợp lệ.
2. Kiểm tra cross-resource và cross-tenant behavior.

### Bước 4: Replay/sidejacking tests

1. Reuse token qua bối cảnh khác (thiết bị/IP/session context).
2. Quan sát hệ thống có ràng buộc fingerprint/context hay không.

## Khuyến nghị thiết kế an toàn

1. Enforce bắt buộc `iss`, `aud`, `exp`, `nbf` với policy rõ ràng.
2. Giới hạn thời gian sống token ngắn, tách access token/refresh token.
3. Ràng buộc token với user context (cookie fingerprint, device binding phù hợp).
4. Với nghiệp vụ nhạy cảm, kiểm tra quyền từ server-side source of truth.
5. Có cơ chế revoke/denylist khi cần logout cưỡng bức hoặc incident response.

## Related Files

- [Detection Workflow](01-detection-workflow.md)
- [Signature Verification Flaws](02-signature-verification-flaws.md)
- [Defense and Mitigation](13-defense-mitigation.md)
