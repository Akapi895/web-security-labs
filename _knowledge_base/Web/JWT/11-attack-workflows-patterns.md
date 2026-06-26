# JWT Attack Workflows and Patterns

## Mục tiêu

Trừu tượng hóa khai thác JWT thành các pattern tái sử dụng được, tương tự cách SQLi mô hình hóa injection process.

## Workflow tổng quát (framework-independent)

```text
1. SCOPE
   -> Chọn endpoint có authz rõ ràng
2. TOKEN TRIAGE
   -> Decode header/payload, xác định alg/key source/claims
3. HYPOTHESIS
   -> Chọn family lỗ hổng khả dĩ
4. CONTROLLED TEST
   -> Tamper tối thiểu, đo phản hồi
5. FORGE/RE-SIGN
   -> Tạo token theo cơ chế bypass tương ứng
6. IMPACT VALIDATION
   -> Chứng minh bypass authn/authz bằng hành động thật
7. HARDENING RECOMMENDATION
   -> Đưa control kỹ thuật và kiểm thử regression
```

## Pattern catalog

## Pattern A: Tamper-Without-Resign

### Ý tưởng

Sửa claims, giữ nguyên signature để kiểm tra server có verify hay không.

### Dùng khi

- Bất kỳ JWT nào, như bước sanity check đầu tiên.

### Dấu hiệu thành công

- Token tampered vẫn được chấp nhận.

## Pattern B: None-Algorithm Downgrade

### Ý tưởng

Đổi `alg=none`, bỏ signature, giữ format `header.payload.`.

### Dùng khi

- Server có dấu hiệu xử lý `alg` không chặt.

### Dấu hiệu thành công

- Bypass phiên hoặc quyền với token unsigned.

## Pattern C: Weak-Secret Re-sign

### Ý tưởng

Crack HMAC secret, ký lại token với claims mới.

### Dùng khi

- Header dùng `HSxxx`.

### Dấu hiệu thành công

- Token re-sign hợp lệ và thay đổi quyền được chấp nhận.

## Pattern D: Attacker-Controlled Key Source

### Ý tưởng

Làm server chọn key verify theo nguồn attacker kiểm soát (`jwk`, `jku`, `kid`).

### Dùng khi

- Header có tham số key-management mở.

### Dấu hiệu thành công

- Outcome verify phụ thuộc key do attacker cung cấp.

## Pattern E: Algorithm Confusion

### Ý tưởng

Đổi từ RS/ES sang HS, dùng public key làm HMAC secret.

### Dùng khi

- Có public key (lộ hoặc suy ra).
- Server không pin thuật toán theo key type.

### Dấu hiệu thành công

- Token HS ký bằng public key được verify pass.

## Pattern F: Claim Logic Abuse (sau verify)

### Ý tưởng

Khai thác thiếu kiểm `exp`/`iss`/`aud`/tenant context dù signature hợp lệ.

### Dùng khi

- Không tìm thấy bypass signature nhưng vẫn nghi ngờ authz design flaw.

### Dấu hiệu thành công

- Token technically valid nhưng trái policy vẫn được chấp nhận.

## Ma trận chọn pattern theo dấu hiệu ban đầu

| Dấu hiệu ban đầu            | Pattern ưu tiên         |
| --------------------------- | ----------------------- |
| Tamper payload mà vẫn pass  | A                       |
| Token RS có thể đổi `alg`   | B, E                    |
| Header có `jwk`/`jku`/`kid` | D                       |
| Header là HS256             | C                       |
| Không lộ key công khai      | E + kỹ thuật từ file 08 |

## Mẫu báo cáo ngắn theo pattern

1. **Hypothesis**: server trust sai lớp nào.
2. **Mutation**: sửa gì trong header/payload/signature.
3. **Observation**: response differential nào xác nhận.
4. **Impact**: hành động đặc quyền nào đạt được.
5. **Mitigation**: control cụ thể để loại bỏ pattern đó.

## Related Files

- [Detection Workflow](01-detection-workflow.md)
- [PortSwigger Labs Playbook](12-labs-portswigger-playbook.md)
- [Defense and Mitigation](13-defense-mitigation.md)
