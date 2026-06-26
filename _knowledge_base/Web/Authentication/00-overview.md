# Authentication Vulnerabilities Overview

## Definition

Authentication (Xác thực) là quá trình xác minh danh tính của người dùng hoặc hệ thống. Trong ứng dụng web, authentication là cơ chế đầu tiên và quan trọng nhất trong chuỗi bảo mật — nếu cơ chế này bị phá vỡ, toàn bộ kiến trúc authorization, session management và access control phía sau đều mất ý nghĩa.

**Bản chất kỹ thuật**: Lỗ hổng authentication không chỉ nằm ở việc "đoán mật khẩu" mà bao gồm mọi điểm yếu trong logic xác minh danh tính — từ brute-force, bypass MFA, đến lạm dụng chức năng phụ trợ như password reset hay remember-me cookie.

## Authentication vs Authorization

| Khái niệm | Câu hỏi trả lời | Ví dụ |
|------------|------------------|-------|
| **Authentication** | "Bạn là ai?" | Đăng nhập bằng username + password |
| **Authorization** | "Bạn được phép làm gì?" | Kiểm tra quyền truy cập tài nguyên |

Authentication xảy ra **trước** authorization. Nếu authentication bị bypass, attacker có thể mạo danh bất kỳ user nào và thừa hưởng toàn bộ quyền hạn của user đó.

## Authentication Factors

| Factor | Loại | Ví dụ | Điểm yếu |
|--------|------|-------|-----------|
| **Knowledge** | Something you know | Password, security question, PIN | Brute-force, social engineering, credential leak |
| **Possession** | Something you have | Phone, hardware token, smart card | SIM swapping, device theft, token interception |
| **Inherence** | Something you are | Fingerprint, face recognition | Khó triển khai trên web, spoofing |

Cơ chế xác thực mạnh kết hợp **nhiều factor khác nhau** (Multi-Factor Authentication). Tuy nhiên, xác minh cùng một factor theo hai cách khác nhau (ví dụ: password + email OTP khi email dùng cùng password) **không phải** là MFA thực sự.

## Impact Assessment

| Impact | Description | Severity |
|--------|-------------|----------|
| **Unauthorized Access** | Truy cập tài khoản và dữ liệu của người khác | Critical |
| **Privilege Escalation** | Chiếm quyền admin, kiểm soát toàn bộ ứng dụng | Critical |
| **Data Breach** | Đọc dữ liệu nhạy cảm: PII, tài chính, nội bộ | Critical |
| **Lateral Movement** | Từ tài khoản thấp, mở rộng attack surface bên trong | High |
| **Reputation Damage** | Mất niềm tin người dùng, vi phạm compliance | High |

Ngay cả khi chỉ chiếm được tài khoản low-privilege, attacker vẫn có thể truy cập các internal pages không public — nơi chứa các attack surface nghiêm trọng hơn.

## Classification by Vulnerability Type

| Category | Mô tả | File chi tiết |
|----------|--------|---------------|
| **Password-based Attacks** | Brute-force, credential stuffing, username enumeration | [01-password-based-attacks.md](01-password-based-attacks.md) |
| **Brute-force Protection Bypass** | Bypass account lock, rate limiting, IP blocking | [02-brute-force-protection-bypass.md](02-brute-force-protection-bypass.md) |
| **Multi-Factor Authentication** | Điểm yếu trong thiết kế MFA/2FA | [03-multi-factor-authentication.md](03-multi-factor-authentication.md) |
| **2FA Bypass Techniques** | Direct access, session manipulation, token abuse | [04-2fa-bypass-techniques.md](04-2fa-bypass-techniques.md) |
| **Password Reset Flaws** | Token prediction, poisoning, email-based weaknesses | [05-password-reset-vulnerabilities.md](05-password-reset-vulnerabilities.md) |
| **Session & Credential Mgmt** | Remember-me cookie, weak encoding, session fixation | [06-session-and-credential-management.md](06-session-and-credential-management.md) |
| **Authentication Logic Flaws** | State confusion, parameter tampering, incomplete verification | [07-authentication-logic-flaws.md](07-authentication-logic-flaws.md) |
| **Defense & Mitigation** | Best practices, secure implementation | [08-defense-mitigation.md](08-defense-mitigation.md) |

## How Authentication Vulnerabilities Arise

Lỗ hổng authentication thường phát sinh từ hai nguyên nhân gốc rễ:

| Nguyên nhân | Mô tả | Ví dụ |
|-------------|--------|-------|
| **Weak Protection** | Cơ chế xác thực không đủ mạnh để chống brute-force | Không có rate limiting, account lockout thiếu logic |
| **Broken Logic** | Lỗi logic trong implementation cho phép bypass hoàn toàn | 2FA verification không kiểm tra user consistency, password reset token không expire |

Đặc biệt, các chức năng phụ trợ (password reset, password change, remember-me) thường bị bỏ qua trong quá trình bảo mật — tạo ra những điểm tấn công mà developer không lường trước.

## Attack Workflow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                 AUTHENTICATION ATTACK WORKFLOW                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  1. RECONNAISSANCE ──► Thu thập thông tin: login form, endpoints,       │
│        │                error messages, user profiles                   │
│        ▼                                                                │
│  2. ENUMERATION    ──► Xác định valid usernames qua response            │
│        │                differences (status, message, timing)           │
│        ▼                                                                │
│  3. ANALYSIS       ──► Phân tích cơ chế: auth flow, MFA logic,          │
│        │                session handling, protection mechanisms         │
│        ▼                                                                │
│  4. HYPOTHESIS     ──► Xây dựng giả thuyết tấn công:                    │
│        │                brute-force? logic bypass? token abuse?         │
│        ▼                                                                │
│  5. EXPLOITATION   ──► Thực thi attack: credential brute-force,         │
│        │                2FA bypass, password reset abuse                │
│        ▼                                                                │
│  6. ESCALATION     ──► Từ user thường → admin, pivot sang               │
│        │                internal systems, access sensitive data         │
│        ▼                                                                │
│  7. PERSISTENCE    ──► Duy trì access: tạo backdoor account,            │
│                         steal session tokens, plant credentials         │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## Authentication Attack Surface Map

```
                        ┌──────────────────┐
                        │   LOGIN FORM     │
                        │  (Primary Auth)  │
                        └────────┬─────────┘
                                 │
          ┌──────────────────────┼──────────────────────┐
          ▼                      ▼                      ▼
   ┌──────────────┐    ┌─────────────────┐    ┌─────────────────┐
   │  Brute-force │    │   2FA/MFA       │    │  HTTP Basic     │
   │  Credential  │    │   Verification  │    │  Authentication │
   │  Stuffing    │    │   Logic         │    │                 │
   └──────────────┘    └─────────────────┘    └─────────────────┘
          │                      │
          ▼                      ▼
   ┌──────────────┐    ┌─────────────────┐
   │  Rate Limit  │    │  Token Handling │
   │  Bypass      │    │  Session Mgmt   │
   └──────────────┘    └─────────────────┘
                                 │
          ┌──────────────────────┼──────────────────────┐
          ▼                      ▼                      ▼
   ┌──────────────┐    ┌─────────────────┐    ┌─────────────────┐
   │  Password    │    │  Remember Me    │    │  Password       │
   │  Reset       │    │  Cookie         │    │  Change         │
   └──────────────┘    └─────────────────┘    └─────────────────┘
```

## Related Files

- [Password-based Attacks](01-password-based-attacks.md)
- [Brute-force Protection Bypass](02-brute-force-protection-bypass.md)
- [Multi-Factor Authentication](03-multi-factor-authentication.md)
- [2FA Bypass Techniques](04-2fa-bypass-techniques.md)
- [Password Reset Vulnerabilities](05-password-reset-vulnerabilities.md)
- [Session & Credential Management](06-session-and-credential-management.md)
- [Authentication Logic Flaws](07-authentication-logic-flaws.md)
- [Defense & Mitigation](08-defense-mitigation.md)
