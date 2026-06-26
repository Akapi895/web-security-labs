# Weak HMAC Secrets (HS256/HS384/HS512)

## Bản chất kỹ thuật

Với thuật toán HMAC, cùng một secret dùng cho cả sign và verify. Nếu secret yếu, mặc định, hoặc bị lộ, attacker có thể tự tạo token hợp lệ với mọi claim mong muốn.

## Nguyên nhân thường gặp

1. Dùng secret kiểu từ điển (`secret`, `secret1`, `changeme`).
2. Dùng secret ngắn, entropy thấp.
3. Hardcode secret trong source/config và bị leak.
4. Dùng chung secret giữa nhiều môi trường/dev-prod.

## Điều kiện khai thác

- Header token dùng họ HMAC (`HS256`, `HS384`, `HS512`).
- Có khả năng brute-force offline hoặc lấy được secret từ leak.

## Workflow detect -> exploit

### Bước 1: Nhận diện thuật toán

Decode header, xác định `alg` thuộc họ HS.

### Bước 2: Đánh giá khả năng crack secret

Sử dụng wordlist phổ biến hoặc attack rule-based.

Ví dụ Hashcat:

```bash
hashcat -a 0 -m 16500 <jwt_token> <wordlist>
```

Hoặc dùng Burp JWT Editor: `Weak HMAC secret`.

### Bước 3: Xác nhận secret đúng

1. Import secret thành symmetric key.
2. Sửa payload (`sub`, `role`, ...).
3. Ký lại token bằng HS tương ứng.
4. Gửi request, xác nhận quyền cao.

## Dấu hiệu nhận biết trong pentest

| Dấu hiệu                                   | Ý nghĩa                           |
| ------------------------------------------ | --------------------------------- |
| Token HS + secret crack nhanh              | Secret yếu/mặc định               |
| Re-sign token thành công và được chấp nhận | Compromise hoàn chỉnh trust model |
| Cùng secret giữa nhiều app                 | Rủi ro lateral movement           |

## Mapping PortSwigger lab

- Lab 3: JWT authentication bypass via weak signing key

## Lưu ý kỹ thuật khi thực hành

1. Không nhầm lẫn giữa decode token và verify token.
2. Dùng token còn hạn (`exp`) để tránh nhiễu do hết hạn.
3. Với nhiều candidate secret, xác nhận qua endpoint đặc quyền thay vì chỉ dựa decode.

## Phòng thủ

1. Dùng secret có entropy cao (ít nhất 256-bit random).
2. Quản lý secret bằng KMS/HSM/secret manager, không hardcode.
3. Rotation định kỳ và cơ chế revoke theo key-id/version.
4. Chặn thuật toán yếu và enforce policy theo issuer.
5. Theo dõi hành vi brute-force/signature anomaly trong telemetry.

## Related Files

- [Detection Workflow](01-detection-workflow.md)
- [Tools and Automation](10-tools-automation.md)
- [Defense and Mitigation](13-defense-mitigation.md)
