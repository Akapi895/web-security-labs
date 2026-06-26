# JWT Detection Workflow

## Mục tiêu

Xây dựng quy trình kiểm thử JWT có hệ thống để:

- Nhận diện đúng cơ chế ký/xác minh token
- Xác định điều kiện khai thác thực tế
- Tránh thử payload mù gây nhiễu kết quả

## Phase 1: Scope và baseline

1. Chọn request có kiểm soát truy cập rõ ràng (ví dụ `/my-account`, `/admin`, API profile).
2. Xác định token nào thật sự gate authorization (cookie, `Authorization`, custom header).
3. Thiết lập baseline:

- Request hợp lệ với token gốc
- Request vào tài nguyên đặc quyền với user thường (phải bị từ chối)

## Phase 2: Token triage

Decode header/payload và ghi nhận:

- `alg`, `kid`, `jwk`, `jku`, `x5u`, `x5c`
- Claims chuẩn: `iss`, `aud`, `exp`, `nbf`, `iat`, `sub`, `jti`
- Claims quyền: `role`, `scope`, `is_admin`, `tenant_id`
- Vị trí token trong luồng (client-side storage, cookie flags, refresh flow)

## Phase 3: Signature enforcement sanity check

Kiểm tra nhanh server có verify signature không:

1. Sửa payload (`sub`/`role`) nhưng giữ nguyên signature.
2. Gửi lại request.

Kết quả diễn giải:

| Kết quả          | Ý nghĩa                                     |
| ---------------- | ------------------------------------------- |
| Server chấp nhận | Khả năng cao missing signature verification |
| Server từ chối   | Có verify, chuyển sang test nâng cao        |

## Phase 4: Kiểm thử theo family lỗ hổng

### A. Signature verification flaws

- `alg=none`
- Biến thể viết hoa/thường (`None`, `nOnE`) nếu parser yếu
- Signature tamper đơn giản

### B. Secret/key management flaws

- HS256 secret yếu/default/hardcoded
- Secret lộ từ config/log/source leak

### C. Key selection flaws từ header

- `jwk` embedded key
- `jku` JWKS spoofing
- `kid` path traversal/injection

### D. Algorithm confusion

- Token gốc `RS256`/`ES256`
- Ép sang `HS256`
- Dùng public key làm HMAC secret

### E. Claim validation logic flaws

- Bỏ qua `exp`/`nbf`
- Không kiểm `iss`/`aud`
- Authorization chỉ dựa vào claim client-controlled

## Phase 5: Xác nhận tác động (impact validation)

Tối thiểu cần chứng minh 3 bước:

1. Baseline: user thường không có quyền.
2. Kỹ thuật bypass hoạt động (token giả được chấp nhận).
3. Hành động đặc quyền thực thi thành công (ví dụ truy cập `/admin`, thao tác admin).

## Decision Tree nhanh

```text
JWT found
  -> Decode header/payload
  -> Tamper payload without resign
      -> accepted? YES -> Unverified signature path
      -> NO -> Check alg
          -> HS256 -> Weak secret / leaked secret path
          -> RS/ES -> Check jwk/jku/kid + confusion path
  -> Validate claims handling (exp/iss/aud/nbf)
  -> Confirm privilege-impact
```

## Mẫu ghi nhận bằng chứng

| Trường            | Nội dung                               |
| ----------------- | -------------------------------------- |
| Endpoint kiểm thử | `/admin`                               |
| Token gốc         | Header/Payload snapshot                |
| Test case         | Mô tả chỉnh sửa cụ thể                 |
| HTTP result       | Status code, redirect, body marker     |
| Kết luận          | Vulnerable / Not vulnerable            |
| Impact            | Auth bypass, privilege escalation, ... |

## Sai lầm thường gặp khi test JWT

1. Chỉ decode mà không xác minh behavior qua request thật.
2. Không lưu baseline nên khó chứng minh impact.
3. Nhầm giữa key candidate và token tampered khi làm confusion attack.
4. Kết luận vội từ một phản hồi lỗi không ổn định.

## Related Files

- [Overview](00-overview.md)
- [Attack Workflows and Patterns](11-attack-workflows-patterns.md)
- [PortSwigger Labs Playbook](12-labs-portswigger-playbook.md)
