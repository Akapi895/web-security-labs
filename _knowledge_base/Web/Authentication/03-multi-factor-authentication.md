# Multi-Factor Authentication

## Overview

Multi-Factor Authentication (MFA) yêu cầu người dùng chứng minh danh tính qua **nhiều factor khác nhau** — tạo defense-in-depth cho quá trình xác thực. Tuy nhiên, MFA chỉ mạnh bằng implementation của nó. Hiểu rõ kiến trúc và điểm yếu inherent của từng phương thức MFA là nền tảng để đánh giá bảo mật hệ thống.

## Nguyên tắc cốt lõi

### True MFA vs False MFA

MFA chỉ thực sự hiệu quả khi xác minh **các factor khác nhau**, không phải cùng một factor theo hai cách:

| Kết hợp | True MFA? | Lý do |
|----------|-----------|-------|
| Password + Hardware token | ✓ | Knowledge + Possession |
| Password + SMS OTP | ✓ (yếu) | Knowledge + Possession (nhưng SMS có thể bị intercept) |
| Password + Email OTP | ✗ | Knowledge + Knowledge — email thường dùng cùng password |
| Password + Security question | ✗ | Knowledge + Knowledge |

**Key insight**: Email-based 2FA **không phải** true 2FA vì truy cập email code chỉ yêu cầu **biết** login credentials email — vẫn là knowledge factor.

## Two-Factor Authentication Tokens

### Các phương thức phổ biến

| Phương thức | Factor | Cách hoạt động | Security Level |
|-------------|--------|-----------------|----------------|
| **Hardware Token** (RSA, YubiKey) | Possession | Generate code trực tiếp trên device | Rất cao |
| **TOTP App** (Google Authenticator, Authy) | Possession | App generate code dựa trên shared secret + time | Cao |
| **SMS OTP** | Possession | Server gửi code qua SMS | Trung bình |
| **Email OTP** | Knowledge | Server gửi code qua email | Thấp |
| **Push Notification** | Possession | Approve/deny trên device | Cao |

### Tại sao Hardware Token mạnh nhất

```
Hardware Token:
  ┌────────────┐
  │ Seed (bí mật) │──► Generate code nội bộ
  │ chỉ ở trên   │    Không truyền qua mạng
  │ device        │    Không thể intercept
  └────────────┘

SMS OTP:
  Server ──► SMS Gateway ──► Cell Tower ──► Phone
        │                │              │
        Có thể intercept ở bất kỳ điểm nào
```

## SMS-based 2FA — Phân tích điểm yếu

### Vấn đề kiến trúc

SMS OTP vi phạm nguyên tắc "code được generate bởi device" — code được tạo ở server và **truyền** qua kênh không an toàn.

### Attack Vectors

| Vector | Mô tả | Khả thi |
|--------|--------|---------|
| **SIM Swapping** | Attacker thuyết phục nhà mạng chuyển số điện thoại sang SIM mới | Cao — social engineering |
| **SMS Interception** | Exploit SS7 protocol để đọc SMS | Trung bình — cần kỹ năng cao |
| **Malware trên phone** | App độc hại đọc SMS | Cao — phổ biến trên Android |
| **SIM Cloning** | Clone physical SIM card | Thấp — cần physical access |
| **Voicemail hijack** | Nếu OTP gửi qua voice call, truy cập voicemail | Trung bình |

### SIM Swapping Flow

```
1. Attacker thu thập thông tin nạn nhân (name, DOB, address)
2. Gọi nhà mạng, mạo danh nạn nhân
3. Yêu cầu chuyển số sang SIM mới (báo mất phone)
4. Nhà mạng kích hoạt SIM mới → SIM cũ bị vô hiệu
5. Toàn bộ SMS (bao gồm OTP) gửi đến attacker
6. Attacker dùng OTP để bypass 2FA
```

## TOTP (Time-based One-Time Password)

### Cách hoạt động

```
Setup:
  Server ──► Generate shared secret ──► Hiển thị QR code ──► User scan vào app

Mỗi lần login:
  App:    HMAC-SHA1(shared_secret, floor(time/30)) → 6-digit code
  Server: HMAC-SHA1(shared_secret, floor(time/30)) → 6-digit code
  
  Nếu khớp → xác thực thành công
```

### Điểm yếu của TOTP

| Vấn đề | Mô tả |
|---------|--------|
| **Shared secret exposure** | Nếu secret bị lộ (backup, screenshot QR), attacker generate code tùy ý |
| **Time window** | Code valid trong 30s — nếu bị phishing real-time, attacker dùng ngay |
| **No revocation** | Không thể revoke một code cụ thể đã generate |
| **Replay within window** | Code có thể dùng lại trong cùng time window nếu server không track |

## Backup Codes — Rủi ro thường bị bỏ qua

### Bản chất

Backup codes là **static passwords dùng một lần** — về bản chất quay lại knowledge factor và mất tính chất "something you have".

### Rủi ro

| Rủi ro | Mô tả |
|--------|--------|
| **Immediate generation** | Backup codes generate ngay khi enable 2FA — có thể bị capture |
| **CORS misconfiguration** | API trả backup codes có thể bị cross-origin read |
| **XSS** | Nếu có XSS, attacker đọc backup codes từ settings page |
| **No separate auth** | Nhiều app không yêu cầu re-auth khi xem backup codes |
| **Storage** | User thường lưu plaintext (notes app, screenshot) |

## 2FA Activation — Xử lý Previous Sessions

### Vấn đề

Khi user enable 2FA, các session **đã tồn tại** (đã login trước đó) có thể vẫn active — nghĩa là attacker đã có session token trước khi 2FA bật sẽ **không bị ảnh hưởng**.

### Best Practice

```
Enable 2FA → Invalidate tất cả existing sessions
           → Buộc re-login với 2FA trên mọi device
           → Chỉ giữ lại session hiện tại (đang enable 2FA)
```

## Information Disclosure trên 2FA Page

Trang 2FA verification có thể vô tình tiết lộ:

| Thông tin | Ví dụ |
|-----------|-------|
| **Phone number** | "Code sent to ***-***-1234" |
| **Email** | "Code sent to t***@gmail.com" |
| **2FA method** | Phân biệt SMS vs TOTP |
| **Account status** | Xác nhận account tồn tại |

## Related Files

- [2FA Bypass Techniques](04-2fa-bypass-techniques.md)
- [Authentication Logic Flaws](07-authentication-logic-flaws.md)
- [Defense & Mitigation](08-defense-mitigation.md)
