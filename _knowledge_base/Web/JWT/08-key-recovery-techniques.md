# Key Recovery Techniques for JWT Assessment

## Mục tiêu

Tổng hợp kỹ thuật thu thập hoặc suy ra key/secret phục vụ đánh giá lỗ hổng JWT trong bối cảnh pentest và lab.

## 1) Thu key từ endpoint công khai

### JWKS endpoint

Các vị trí thường gặp:

- `/.well-known/jwks.json`
- `/jwks.json`

Nếu key public lộ, có thể dùng cho:

- Algorithm confusion (RS/ES -> HS)
- Tạo key object đúng định dạng để ký token giả

### TLS certificate/public key

Trong một số hệ thống dùng chung key material không an toàn, public key có thể lấy từ cert chain.

## 2) Brute-force secret (HMAC)

Áp dụng cho họ HS.

Kỹ thuật:

1. Dictionary attack (`secret`, `changeme`, ...)
2. Rule-based mutation
3. Kết hợp OSINT/config leak

Ví dụ công cụ:

- Hashcat (`-m 16500`)
- jwt_tool
- Burp JWT Editor (`Weak HMAC secret`)

## 3) Suy public key từ nhiều token hợp lệ

Khi server không lộ JWKS trực tiếp, có thể dùng hai token RS hợp lệ để suy ra modulus candidate.

Workflow lab-oriented:

1. Thu 2 JWT hợp lệ do server phát hành (khác signature).
2. Dùng công cụ suy key (ví dụ `portswigger/sig2n`).
3. Có thể nhận nhiều candidate key.
4. Test candidate bằng tampered token trên endpoint an toàn (`/my-account`).
5. Chọn candidate trả kết quả hợp lệ (`200`) làm key đúng.

## 4) Khai thác leak từ cấu hình/source/log

Các nguồn hay gặp:

1. File cấu hình backup (`.env`, `application.yml`, `config.json`)
2. Log debug in secret
3. Source code hardcoded key
4. CI/CD artifact lộ thông tin

## Phân biệt key vs token khi thực hành

Sai sót phổ biến: nhầm chuỗi key với chuỗi JWT tampered.

Checklist nhanh:

1. Chuỗi key thường là PEM/Base64/JWK component.
2. JWT luôn có dạng 3 phần tách bởi dấu chấm.
3. Khi tạo symmetric key `k`, phải dùng key material, không dùng toàn bộ JWT.

## Bằng chứng kỹ thuật cần lưu

| Bằng chứng           | Ví dụ                               |
| -------------------- | ----------------------------------- |
| Nguồn key            | JWKS URL, command output, leak path |
| Candidate validation | Response code trước/sau thay token  |
| Final impact         | Endpoint admin thao tác thành công  |

## Related Files

- [Weak HMAC Secrets](03-weak-hmac-secrets.md)
- [Algorithm Confusion](07-algorithm-confusion.md)
- [Tools and Automation](10-tools-automation.md)
