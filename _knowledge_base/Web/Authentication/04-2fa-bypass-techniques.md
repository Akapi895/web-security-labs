# 2FA Bypass Techniques

## Overview

Dù 2FA tăng cường bảo mật đáng kể, implementation flaws có thể khiến nó bị bypass hoàn toàn. Phần này tổng hợp và phân loại các kỹ thuật bypass 2FA theo cơ chế khai thác, từ logic flaws đến brute-force và side-channel attacks.

## Classification

| Category | Kỹ thuật | Nguyên nhân gốc |
|----------|----------|-----------------|
| **Logic Bypass** | Direct endpoint access, session manipulation | Incomplete verification |
| **Token Abuse** | Reuse, cross-account, exposure | Weak token management |
| **Brute-force** | Code enumeration, rate limit bypass | Insufficient protection |
| **Side-channel** | CSRF/Clickjacking disable, OAuth compromise | Attack surface mở rộng |
| **Legacy Abuse** | Older API versions, subdomain testing | Inconsistent enforcement |

---

## 1. Direct Endpoint Access

### Bản chất

Sau khi login (step 1), user ở trạng thái "partially authenticated". Nếu server **không kiểm tra** việc hoàn thành step 2 trước khi cho truy cập protected pages, attacker bỏ qua 2FA bằng cách navigate thẳng đến trang đích.

### Flow khai thác

```
Normal flow:
  /login → credentials → /login2 → 2FA code → /dashboard

Bypass flow:
  /login → credentials → [skip /login2] → /dashboard
                                           ↑
                               Nếu server không check 2FA completion
```

### Kỹ thuật bổ trợ

Nếu redirect bị chặn, thử thay đổi **Referer header** để giả mạo navigation từ 2FA page:

```http
GET /dashboard HTTP/1.1
Referer: https://target.com/login2
```

---

## 2. Flawed Two-Factor Verification Logic

### Bản chất

Server không đảm bảo **cùng một user** thực hiện cả hai bước authentication. User identity ở step 2 được xác định qua **cookie hoặc parameter** có thể bị attacker thay đổi.

### Ví dụ chi tiết

```http
# Step 1: Attacker login với credential hợp lệ
POST /login-steps/first HTTP/1.1
username=attacker&password=attackerpass

# Server set cookie xác định account cho step 2
HTTP/1.1 200 OK
Set-Cookie: account=attacker

# Step 2: Attacker thay đổi cookie thành victim
POST /login-steps/second HTTP/1.1
Cookie: account=victim
verification-code=123456

# Nếu server chỉ dựa vào cookie để xác định account
# → Attacker bypass 2FA của victim
```

### Tại sao nghiêm trọng

Kết hợp với brute-force verification code (chỉ 4-6 digits):
- Attacker **không cần biết password của victim**
- Chỉ cần biết username
- Brute-force 6-digit code = tối đa 1,000,000 attempts
- 4-digit code = chỉ 10,000 attempts

---

## 3. Token Reuse và Cross-Account Abuse

### Token Reuse

Token 2FA đã dùng trước đó có thể vẫn valid nếu server **không invalidate** after use:

```
1. Login → nhận OTP: 123456
2. Submit 123456 → success
3. Logout
4. Login lại → submit 123456 lần nữa → có thể vẫn thành công
```

### Unused Token Cross-Account

Extract token từ **account của attacker** và thử dùng cho **account khác**:

```
1. Attacker login → nhận OTP: 789012
2. Không submit OTP cho attacker account
3. Victim login (attacker biết credentials)
4. Submit OTP 789012 cho victim account
   → Nếu server không bind token với specific user → bypass
```

### Token Exposure

Kiểm tra response từ server có leak token không:

```http
# Một số app trả token trong response body hoặc header
HTTP/1.1 200 OK
X-OTP-Token: 485723

# Hoặc trong JSON response
{"status": "otp_sent", "debug_token": "485723"}
```

---

## 4. Session Manipulation

### Bản chất

Exploit backend session management khi xử lý multiple concurrent sessions:

### Flow khai thác

```
Browser A (Attacker account):          Browser B (Victim account):
1. Login: attacker/pass                1. Login: victim/pass
2. Được redirect đến 2FA page          2. Được redirect đến 2FA page  
3. Complete 2FA thành công
4. Lấy session cookie sau 2FA
5. Apply session cookie vào Browser B
                                        → Có thể bypass 2FA cho victim
```

---

## 5. Brute-forcing Verification Codes

### Code Space Analysis

| Code Length | Total Combinations | Thời gian (100 req/s) |
|-------------|-------------------|----------------------|
| 4 digits | 10,000 | ~1.7 phút |
| 6 digits | 1,000,000 | ~2.8 giờ |
| 8 digits | 100,000,000 | ~11.6 ngày |

### Bypass Auto-Logout on Failed Attempts

Nhiều app logout user sau N lần nhập sai code. Attacker bypass bằng automation:

```
Macro/Script flow:
1. Login (username + password)
2. Nhận 2FA page
3. Submit OTP guess
4. Nếu fail → bị logout
5. Tự động re-login → quay lại step 2
6. Submit OTP guess tiếp theo
... lặp cho đến khi đúng
```

Công cụ: **Burp Intruder macros**, **Turbo Intruder** (Python scripting).

### Rate Limit Bypass cho OTP

| Kỹ thuật | Mô tả |
|----------|--------|
| **Code resend** | Request gửi lại code → reset rate limit counter |
| **Slow brute-force** | Gửi chậm để dưới flow rate limit |
| **Infinite OTP regeneration** | Mỗi lần request code mới, thử lại bộ codes cũ |
| **Race condition** | Gửi nhiều request cùng lúc trước khi rate limit activate |

---

## 6. Race Condition Exploitation

### Bản chất

Gửi **nhiều request xác minh OTP đồng thời** trước khi server kịp cập nhật counter failed attempts:

```
Thời điểm T:
  Request 1: OTP=000001 ─┐
  Request 2: OTP=000002 ─┤
  Request 3: OTP=000003 ─┼── Gửi cùng lúc
  Request 4: OTP=000004 ─┤
  Request 5: OTP=000005 ─┘
  
Server xử lý:
  Counter chưa kịp tăng → tất cả 5 request đều được check
  → Bypass rate limit "3 attempts max"
```

---

## 7. CSRF/Clickjacking để Disable 2FA

### Chiến lược

Thay vì bypass 2FA, **tắt 2FA** của victim qua CSRF hoặc Clickjacking:

```
1. Victim truy cập page chứa CSRF exploit
2. Request tự động gửi đến:
   POST /settings/disable-2fa
   Cookie: victim-session
3. 2FA bị tắt → attacker login bình thường
```

### Điều kiện

- Endpoint disable 2FA thiếu CSRF protection
- Hoặc settings page vulnerable với Clickjacking (thiếu X-Frame-Options)

---

## 8. "Remember Me" Cookie Exploitation

### Predictable Cookie Values

Nếu "remember me" cookie được tạo từ static values:

| Cookie Pattern | Predictability | Attack |
|----------------|---------------|--------|
| `base64(username)` | Trivial | Generate cho bất kỳ user |
| `md5(username)` | Trivial | Generate cho bất kỳ user |
| `md5(username + password)` | Medium | Dictionary attack |
| `base64(username + ":" + md5(password))` | Medium | Brute-force with hashcat |
| `hmac(username, server_secret)` | Khó | Cần biết server secret |

### IP Address Impersonation

Nếu remember-me validation kiểm tra IP:

```http
GET /dashboard HTTP/1.1
Cookie: remember=<stolen_cookie>
X-Forwarded-For: <victim_ip>
```

---

## 9. Older Versions và Subdomain Testing

### API Versioning

```
/api/v3/login → enforce 2FA ✓
/api/v2/login → enforce 2FA ✓
/api/v1/login → NO 2FA!  ← legacy endpoint
```

### Subdomain

```
app.target.com      → 2FA enforced ✓
staging.target.com  → 2FA not implemented ← dev environment
m.target.com        → 2FA has bugs ← mobile version
api.target.com      → Different auth logic
```

---

## 10. Password Reset Disabling 2FA

### Flow khai thác

```
1. Target account có 2FA enabled
2. Trigger password reset (chỉ cần email/username)
3. Reset password thành công
4. Login với password mới → 2FA bị disable tự động!
```

Nhiều implementation **tắt 2FA** khi password reset vì assume user mất access đến 2FA device.

---

## 11. OTP Construction Errors

### Bản chất

Nếu OTP được tạo dựa trên data mà user **đã biết** hoặc **có thể đoán**, attacker tự generate OTP:

| OTP based on | Attacker knowledge | Bypass? |
|--------------|-------------------|---------|
| `TOTP(secret)` | Secret leaked | ✓ |
| `hash(user_id + timestamp)` | User ID + server time | ✓ |
| `random()` on client | Client-side code visible | Có thể |
| `HMAC(server_secret, data)` | Server secret unknown | ✗ |

---

## 12. OAuth Platform Compromise

Nếu app cho phép login qua OAuth (Google, Facebook):

```
1. Compromise victim's Google account (separate attack)
2. Login to target app via "Sign in with Google"
3. 2FA trên target app bị bypass vì auth delegate cho Google
```

---

## Bypass Technique Selection Matrix

| Tình huống | Technique ưu tiên |
|------------|-------------------|
| App không check 2FA completion | Direct endpoint access |
| Cookie-based user identification | Flawed verification logic |
| Short OTP code + no rate limit | Brute-force |
| Rate limit nhưng có resend | Code resend + brute-force |
| Có CSRF vulnerability | Disable 2FA via CSRF |
| Legacy API endpoints exist | Older version testing |
| Password reset available | Password reset disabling 2FA |
| OAuth login available | OAuth platform compromise |

## Related Files

- [Multi-Factor Authentication](03-multi-factor-authentication.md)
- [Brute-force Protection Bypass](02-brute-force-protection-bypass.md)
- [Authentication Logic Flaws](07-authentication-logic-flaws.md)
- [Session & Credential Management](06-session-and-credential-management.md)
