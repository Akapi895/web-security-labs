# Defense & Mitigation

## Overview

Phần này tổng hợp các biện pháp phòng thủ cho toàn bộ attack surface của authentication — từ password storage, brute-force protection, đến MFA implementation và session management. Mỗi biện pháp được giải thích **tại sao** nó cần thiết, không chỉ **làm gì**.

## 1. Secure Password Storage

### Hashing — Nguyên tắc cốt lõi

Password **không bao giờ** được lưu plaintext hoặc encrypted (reversible). Phải dùng **one-way hash function** chuyên dụng cho password.

| Algorithm | An toàn? | Tốc độ | Lý do |
|-----------|----------|--------|-------|
| **Plaintext** | ✗✗✗ | — | Breach = full exposure |
| **MD5** | ✗✗ | Rất nhanh | Rainbow table, collision attacks |
| **SHA-256** | ✗ (unsalted) | Nhanh | GPU brute-force khả thi |
| **SHA-256 + salt** | Medium | Nhanh | Tốt hơn nhưng vẫn fast hash |
| **bcrypt** | ✓ | Chậm (tunable) | Cost factor chống GPU |
| **scrypt** | ✓ | Chậm + memory-hard | Chống ASIC/GPU |
| **Argon2id** | ✓✓ | Chậm + memory-hard | Modern standard, winner of PHC |

### Implementation

```python
# Python — bcrypt
import bcrypt

# Hash password
salt = bcrypt.gensalt(rounds=12)  # cost factor 12
hashed = bcrypt.hashpw(password.encode(), salt)

# Verify password
if bcrypt.checkpw(input_password.encode(), stored_hash):
    authenticate()
```

```python
# Python — Argon2
from argon2 import PasswordHasher

ph = PasswordHasher(
    time_cost=3,       # iterations
    memory_cost=65536,  # 64MB
    parallelism=4
)

# Hash
hash = ph.hash(password)

# Verify
try:
    ph.verify(hash, input_password)
except argon2.exceptions.VerifyMismatchError:
    deny_access()
```

### Salt — Tại sao bắt buộc

```
Không có salt:
  user1: password123 → 482c811da5d5b...
  user2: password123 → 482c811da5d5b...  ← cùng hash!
  → Rainbow table crack cả hai cùng lúc

Có salt (unique per user):
  user1: password123 + salt_a → 7f2b3c4d5e...
  user2: password123 + salt_b → 9a8b7c6d5e...  ← khác hash
  → Phải brute-force từng user riêng
```

## 2. Brute-force Protection

### Multi-layer Defense

```
Layer 1: Rate Limiting
  └─► Giới hạn requests/phút per IP
  └─► Progressive delay (1s → 2s → 4s → 8s)

Layer 2: Account Lockout
  └─► Temporary lock sau N failed attempts
  └─► Unlock sau cooldown period (KHÔNG permanent lock → DoS)
  └─► Notify user qua email

Layer 3: CAPTCHA
  └─► Trigger sau M failed attempts
  └─► reCAPTCHA v3 (invisible) cho UX tốt hơn

Layer 4: Monitoring
  └─► Alert on unusual login patterns
  └─► Geo-IP anomaly detection
  └─► Device fingerprinting
```

### Generic Error Messages

```
# VULNERABLE — leaked information
"Invalid username"                    → Username không tồn tại
"Invalid password"                    → Username tồn tại, password sai
"Account locked"                      → Username tồn tại + confirm lockout

# SECURE — generic message
"Invalid username or password"        → Không phân biệt
"Invalid username or password"        → Luôn cùng message
```

**Quan trọng**: Response phải identical về **status code, body length, response time**, không chỉ text message.

### Implementation Best Practices

| Measure | Recommended Value | Notes |
|---------|-------------------|-------|
| Rate limit | 10-20 attempts / 5 min | Per IP + per account |
| Account lockout | After 5-10 failures | Temporary (15-30 min), not permanent |
| Lockout duration | 15-30 minutes | Progressive increase |
| CAPTCHA trigger | After 3-5 failures | reCAPTCHA v3 preferred |
| Password complexity | Min 8 chars + complexity | Check against breached password lists |

## 3. Multi-Factor Authentication — Secure Implementation

### Server-side Session Binding

```python
# VULNERABLE — user identity in client-controlled cookie
@app.route('/verify-2fa', methods=['POST'])
def verify_2fa():
    username = request.cookies.get('account')  # ← attacker-controlled!
    code = request.form['code']
    if verify_otp(username, code):
        login(username)

# SECURE — user identity in server-side session
@app.route('/verify-2fa', methods=['POST'])
def verify_2fa():
    username = session.get('pending_2fa_user')  # ← server-side only
    if not username:
        return redirect('/login')
    code = request.form['code']
    if verify_otp(username, code):
        session['authenticated'] = True
        session['2fa_verified'] = True
        login(username)
```

### 2FA Verification Checklist

| Control | Mô tả |
|---------|--------|
| **Server-side user binding** | User identity stored in session, NOT cookie/parameter |
| **One-time use tokens** | Mark token as used immediately after verification |
| **Time-limited tokens** | OTP expires after 30-60 seconds |
| **Rate limiting on verification** | Max 3-5 attempts per token |
| **Re-generate on resend** | Invalidate old token when resending |
| **Consistent response** | Same response for valid/invalid codes |
| **Session invalidation** | Invalidate all sessions when 2FA enabled |
| **Backup code security** | Require re-auth to view, hash storage |

## 4. Password Reset — Secure Flow

### Token Requirements

| Property | Requirement |
|----------|-------------|
| **Entropy** | Minimum 128 bits (32 hex chars) |
| **Generation** | Cryptographically secure random (CSPRNG) |
| **Lifetime** | Expire after 15-60 minutes |
| **One-time use** | Destroy after first use |
| **Re-validation** | Verify token on BOTH form display AND form submission |
| **No user info** | Token should not contain/reveal user identity |

### Prevent Password Reset Poisoning

```python
# VULNERABLE — uses Host header for URL generation
reset_url = f"https://{request.headers['Host']}/reset?token={token}"

# SECURE — uses configured domain
from config import APP_DOMAIN
reset_url = f"https://{APP_DOMAIN}/reset?token={token}"
```

### Secure Reset Flow

```
1. User requests reset → validate email exists (generic response either way)
2. Generate CSPRNG token → store hash(token) + user_id + expiry in DB
3. Send email with https://app.com/reset?token=<token>
4. User clicks link → server verify hash(token) exists + not expired
5. Show reset form (token trong hidden field hoặc session)
6. User submits new password → server verify token AGAIN
7. Update password → destroy token → invalidate all sessions
8. Send confirmation email
```

## 5. Session Management Best Practices

### Cookie Security Configuration

```
Set-Cookie: session_id=<random_value>;
  HttpOnly;          # Prevent XSS cookie theft
  Secure;            # HTTPS only
  SameSite=Lax;      # CSRF protection
  Path=/;            # Scope
  Max-Age=3600;      # 1 hour expiry
```

### Session Lifecycle

| Event | Action |
|-------|--------|
| **Login** | Generate new session ID (prevent fixation) |
| **Logout** | Destroy session server-side + clear cookie |
| **Password change** | Invalidate ALL other sessions |
| **2FA toggle** | Invalidate ALL other sessions |
| **Inactivity timeout** | 15-30 minutes for sensitive apps |
| **Absolute timeout** | 4-8 hours regardless of activity |

### "Remember Me" — Secure Implementation

```python
# Generate secure remember-me token
import secrets

def create_remember_token(user_id):
    selector = secrets.token_hex(12)   # 24 chars — for DB lookup
    validator = secrets.token_hex(32)   # 64 chars — for verification
    
    # Store in DB: selector + hash(validator) + user_id + expiry
    store_token(selector, hash(validator), user_id, expiry=30_days)
    
    # Send to client: selector:validator
    return f"{selector}:{validator}"

def verify_remember_token(cookie_value):
    selector, validator = cookie_value.split(':')
    record = db.find_by_selector(selector)
    if record and hash(validator) == record.validator_hash:
        if not record.expired:
            return record.user_id
    return None
```

**Key point**: Lưu **hash(validator)** trong DB — nếu DB bị breach, attacker không thể dùng stored values vì chỉ có hash.

## 6. HTTP Basic Authentication — Khi nào dùng

### Recommendations

| Tình huống | Dùng HTTP Basic Auth? | Alternative |
|------------|----------------------|-------------|
| Public website | ✗ | Token-based auth (JWT, session) |
| Internal API | Có thể (over HTTPS) | API keys, OAuth2 |
| Development/staging | Có thể | Better: VPN + auth |
| Production API | ✗ | OAuth2, API keys with rotation |

### Nếu bắt buộc dùng

- **HSTS required** — enforce HTTPS, prevent credential sniffing
- **Brute-force protection** — same as form-based login
- **Credential rotation** — periodic password changes
- **Logging** — monitor for unusual access patterns

## Defense Checklist

| # | Control | Priority | Category |
|---|---------|----------|----------|
| 1 | Use bcrypt/Argon2 for password hashing | Critical | Storage |
| 2 | Enforce strong password policy | Critical | Prevention |
| 3 | Check passwords against breach lists | High | Prevention |
| 4 | Implement multi-layer brute-force protection | Critical | Protection |
| 5 | Use generic error messages | High | Information leakage |
| 6 | Implement proper MFA with server-side binding | Critical | Authentication |
| 7 | Secure password reset with CSPRNG tokens | Critical | Reset flow |
| 8 | Prevent reset poisoning (hardcoded domain) | High | Reset flow |
| 9 | HttpOnly + Secure + SameSite cookies | High | Session |
| 10 | Invalidate sessions on auth events | High | Session |
| 11 | Implement session timeouts | Medium | Session |
| 12 | Secure "remember me" with selector:validator | High | Session |
| 13 | Consistent enforcement across all endpoints | High | Logic |
| 14 | Regular security testing | Medium | Verification |
| 15 | Monitor and alert on anomalous login patterns | Medium | Detection |

## Related Files

- [Overview](00-overview.md)
- [Password-based Attacks](01-password-based-attacks.md)
- [Brute-force Protection Bypass](02-brute-force-protection-bypass.md)
- [Multi-Factor Authentication](03-multi-factor-authentication.md)
- [2FA Bypass Techniques](04-2fa-bypass-techniques.md)
- [Password Reset Vulnerabilities](05-password-reset-vulnerabilities.md)
- [Session & Credential Management](06-session-and-credential-management.md)
- [Authentication Logic Flaws](07-authentication-logic-flaws.md)
