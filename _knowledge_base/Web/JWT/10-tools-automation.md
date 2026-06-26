# JWT Tools and Automation

## Mục tiêu

Chuẩn hóa bộ công cụ phục vụ vòng đời kiểm thử JWT:

1. Discover và triage token
2. Test signature/key handling
3. Tự động hóa brute-force/suy key
4. Xác nhận impact nhanh và có bằng chứng

## Công cụ cốt lõi

| Công cụ                              | Vai trò chính                                 | Ghi chú                                              |
| ------------------------------------ | --------------------------------------------- | ---------------------------------------------------- |
| Burp Repeater + JWT Editor           | Decode/edit/sign token, chạy attack templates | Trục chính cho thực hành lab                         |
| jwt_tool                             | Fuzz/test JWT headers/claims, audit mode      | Hữu ích cho batch testing                            |
| Hashcat                              | Crack HMAC secret offline                     | Mode phổ biến: `16500`                               |
| `portswigger/sig2n`                  | Suy public key candidate từ nhiều token RS    | Hữu ích cho confusion khi không lộ JWKS              |
| JOSEPH/SignSaboteur (tuỳ môi trường) | Hỗ trợ test confusion/none nhanh              | Dùng để tăng tốc, không thay cho kiểm chứng thủ công |

## Burp JWT Editor workflow khuyến nghị

1. Gửi request chứa JWT sang Repeater.
2. Mở tab `JSON Web Token` để xem header/payload/signature.
3. Chạy test theo pattern:

- Tamper payload không ký lại
- `alg=none`
- `Weak HMAC secret`
- `Embedded JWK`
- `HMAC Key Confusion Attack`

4. Ký lại token với key phù hợp (`Don't modify header` khi cần giữ payload/header custom).

## Lệnh tham khảo thường dùng

### Crack HMAC secret

```bash
hashcat -a 0 -m 16500 <jwt_token> <wordlist>
```

### Suy key candidate cho confusion khi không lộ JWKS

```bash
docker run --rm -it portswigger/sig2n <token1> <token2>
```

### jwt_tool (ví dụ workflow tổng quát)

```bash
python3 jwt_tool.py <JWT> -M at
```

## Automation strategy theo từng family lỗ hổng

| Family               | Manual trọng tâm                       | Automation phù hợp                        |
| -------------------- | -------------------------------------- | ----------------------------------------- |
| Unverified signature | So sánh baseline/tampered response     | Replay script, diff responses             |
| `alg=none`           | Tạo token không signature chuẩn format | Batch test casing/encoding variations     |
| Weak HMAC            | Xác thực claim impact                  | Crack offline + auto resign               |
| `jwk`/`jku`/`kid`    | Dựng key material và hạ tầng JWKS      | Script publish JWKS + replay matrix       |
| Confusion            | Xác nhận key format đúng               | Auto generate HS tokens từ candidate keys |

## Bằng chứng tối thiểu cần lưu khi tự động hóa

1. Token gốc và token sau chỉnh sửa.
2. Request/response baseline và request/response bypass.
3. Dấu hiệu impact (endpoint admin/action đặc quyền).
4. Metadata về key/secret candidate đã dùng.

## Pitfalls khi dùng tool

1. Nhầm thuật toán khi ký lại token.
2. Nhầm key string với tampered JWT string.
3. Tin 100% kết quả "green" từ tool mà không xác nhận impact thật.
4. Bỏ qua kiểm tra claim expiration gây nhiễu kết quả.

## Related Files

- [Detection Workflow](01-detection-workflow.md)
- [Attack Workflows and Patterns](11-attack-workflows-patterns.md)
- [PortSwigger Labs Playbook](12-labs-portswigger-playbook.md)
