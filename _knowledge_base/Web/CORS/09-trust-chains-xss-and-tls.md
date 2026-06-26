# Trust Chains: XSS and TLS Failures

## CORS Creates Trust Relationships

Ngay cả khi CORS "cấu hình đúng" theo allowlist, bản chất vẫn là tạo trust boundary giữa các origin. Nếu một origin được trust bị compromise, CORS trở thành kênh exfiltration.

## Case 1: XSS on Trusted Origin

### Pattern

`vulnerable-website.com` trust `subdomain.vulnerable-website.com`. Nếu subdomain có XSS, attacker chèn script để gọi API cross-origin và đọc response do CORS cho phép.

### Impact

- Lấy API key/token/profile từ main domain.
- Mở rộng impact từ XSS local thành compromise liên miền.

## Case 2: Trusted Insecure Protocol (HTTP)

### Pattern

Server cho phép origin `http://trusted-subdomain.vulnerable-website.com` và bật credentials.

### Why This Breaks TLS Guarantees

Dịch vụ chính dùng HTTPS vẫn có thể bị compromise do trust tới một HTTP origin không toàn vẹn đường truyền. Tấn công có thể chain qua MITM hoặc điểm chèn nội dung trên HTTP origin.

### Typical Attack Narrative

1. Nạn nhân truy cập một request HTTP.
2. Attacker chèn/nối hướng đến trusted HTTP subdomain.
3. Inject script tại trusted origin.
4. Script gọi API HTTPS của target với credentials.
5. Browser cho đọc response vì CORS trust đã hợp lệ theo policy.

## Risk Assessment Dimensions

| Dimension                       | Question                                            |
| ------------------------------- | --------------------------------------------------- |
| Trusted origin security posture | Origin được trust có XSS/takeover/legacy app không? |
| Protocol integrity              | Có origin HTTP trong allowlist không?               |
| Data sensitivity                | Endpoint expose token/API key/PII không?            |
| Credential dependence           | Có `ACAC: true` và session cookie không?            |

## Remediation

1. Chỉ trust origin HTTPS có kiểm soát chặt.
2. Loại bỏ origin HTTP khỏi allowlist.
3. Xem mỗi trusted origin như dependency bảo mật, cần đánh giá liên tục.
4. Giảm blast radius: API scope nhỏ, authZ theo resource, short-lived token.

## Related Files

- [Misconfiguration Root Causes](05-misconfiguration-root-causes.md)
- [Defense and Mitigation](13-defense-mitigation.md)
