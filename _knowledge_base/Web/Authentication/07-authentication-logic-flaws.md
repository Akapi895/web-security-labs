# Authentication Logic Flaws

## Overview

Lỗi logic trong authentication không phải lỗi kỹ thuật đơn thuần (như thiếu input validation) mà là **sai sót trong thiết kế flow xác thực**. Server thực thi đúng từng bước riêng lẻ, nhưng tổng thể flow có thể bị attacker lạm dụng vì các bước không liên kết logic chặt chẽ với nhau.

**Bản chất**: Authentication là một **state machine** — user phải đi qua các trạng thái theo đúng thứ tự. Logic flaws xảy ra khi attacker có thể **nhảy trạng thái**, **thay đổi context giữa các bước**, hoặc **bypass điều kiện chuyển trạng thái**.

## Phân loại Logic Flaws

| Category | Mô tả | Ví dụ |
|----------|--------|-------|
| **State Confusion** | Attacker thay đổi trạng thái giữa các bước | Skip 2FA step |
| **Parameter Manipulation** | Thay đổi user identity giữa các bước | Cookie account swap |
| **Incomplete Verification** | Server không kiểm tra đầy đủ một bước | Không re-validate token |
| **Inconsistent Enforcement** | Policy áp dụng không đồng nhất | 2FA trên web nhưng không trên API |
| **Assumption Flaws** | Developer giả định sai về user behavior | "User sẽ không access URL trực tiếp" |

---

## 1. State Confusion — Multi-step Login

### Bản chất

Login process gồm nhiều bước (username/password → 2FA → dashboard). Mỗi bước nên **verify hoàn thành bước trước** — nhưng nhiều implementation không làm điều này.

### Authentication State Machine

```
Correct implementation:
  ┌─────────┐    verify     ┌──────────┐    verify     ┌───────────┐
  │ Step 1  │───credentials─►│  Step 2  │───2FA code───►│ Dashboard │
  │ Login   │               │  2FA     │               │ (authed)  │
  └─────────┘               └──────────┘               └───────────┘
       │                         │                          │
     State:                   State:                     State:
     UNAUTHENTICATED      PARTIALLY_AUTH              FULLY_AUTH

Flawed implementation:
  ┌─────────┐    verify     ┌──────────┐               ┌───────────┐
  │ Step 1  │───credentials─►│  Step 2  │               │ Dashboard │
  │ Login   │               │  2FA     │               │ (authed)  │
  └─────────┘               └──────────┘               └───────────┘
       │                                                    ▲
       └────────────── direct access ───────────────────────┘
                    (no state verification)
```

### Ví dụ cụ thể

```http
# Step 1: Login thành công
POST /login
username=victim&password=correct_password
→ 302 Redirect to /login/2fa

# Attacker KHÔNG vào /login/2fa mà truy cập thẳng:
GET /account/dashboard
→ 200 OK ← Server không check 2FA completion!
```

---

## 2. Parameter Manipulation — Identity Swap

### Bản chất

Server xác định user identity ở step 2 qua **parameter hoặc cookie** mà attacker có thể thay đổi, thay vì dùng server-side session binding.

### Flawed Cookie-based Verification

```http
# Attacker login (step 1) với account hợp lệ
POST /login
username=attacker&password=attackerpass
→ Set-Cookie: account=attacker

# Server gửi 2FA code cho attacker
GET /login/2fa
Cookie: account=attacker

# Attacker THAY ĐỔI cookie thành victim
POST /login/2fa
Cookie: account=victim          ← changed!
verification-code=bruteforced
→ Đăng nhập thành công vào account victim
```

### Hidden Field Manipulation

```html
<!-- Password change form -->
<form action="/change-password">
  <input type="hidden" name="username" value="current-user">
  <input type="password" name="current-password">
  <input type="password" name="new-password">
</form>
```

Attacker thay đổi hidden field `username` → đổi password user khác.

### Tại sao xảy ra

Developer **giả định** rằng:
- Client sẽ không modify cookies
- Hidden form fields không thể thay đổi
- Referrer header chứng minh user đến từ step trước

Tất cả đều sai — attacker kiểm soát hoàn toàn client-side data.

---

## 3. Incomplete Verification

### Token Re-validation

```
Flow đúng:
  1. Send token via email
  2. User click link → server verify token
  3. Show reset form
  4. User submit new password → server verify token AGAIN
  5. Reset password + destroy token

Flow vulnerable:
  1. Send token via email
  2. User click link → server verify token
  3. Show reset form  
  4. User submit new password → server DOES NOT verify token
  5. Reset password
  → Attacker chỉ cần POST trực tiếp đến step 4 không cần token
```

### Partial Authentication Check

```python
# Vulnerable — chỉ check session tồn tại, không check auth state
@app.route('/dashboard')
def dashboard():
    if 'session_id' in request.cookies:  # ← chỉ check cookie tồn tại
        return render_dashboard()
    return redirect('/login')

# Secure — check cả auth completion state
@app.route('/dashboard')  
def dashboard():
    session = get_session(request.cookies.get('session_id'))
    if session and session.auth_completed and session.mfa_verified:
        return render_dashboard()
    return redirect('/login')
```

---

## 4. Inconsistent Enforcement

### Cross-endpoint Inconsistency

| Endpoint | 2FA Required? | Rate Limited? | Vấn đề |
|----------|--------------|---------------|---------|
| `POST /login` | ✓ | ✓ | — |
| `POST /api/v1/login` | ✗ | ✗ | Bypass 2FA + rate limit |
| `POST /mobile/login` | ✓ | ✗ | Bypass rate limit |
| `POST /login` (subdomain) | ✗ | ✗ | Legacy endpoint |

### Cross-feature Inconsistency

```
Login form:      ──► Requires 2FA ✓
Password reset:  ──► Login sau reset KHÔNG yêu cầu 2FA ✗
OAuth login:     ──► Bypass 2FA hoàn toàn ✗
API token:       ──► Không qua authentication flow ✗
```

---

## 5. OAuth/Third-party Integration Risks

### OAuth Platform Compromise

```
Normal OAuth flow:
  User → App → "Login with Google" → Google authenticates → Token → App

Attack:
  1. Attacker compromise victim's Google account
  2. Go to target app → "Login with Google"  
  3. Google auth succeeds (attacker controls Google account)
  4. Target app logs attacker in as victim
  → 2FA trên target app bị bypass hoàn toàn
```

### OAuth Misconfiguration

| Misconfiguration | Impact |
|-----------------|--------|
| **Missing state parameter** | CSRF → attacker link their OAuth account to victim's app account |
| **Open redirect in callback** | Token theft via redirect |
| **No email verification** | Attacker registers same email on OAuth provider |
| **Implicit grant type** | Token exposed in URL fragment |

---

## 6. Assumption-based Flaws

### Developer Assumptions vs Reality

| Assumption | Reality | Vulnerability |
|------------|---------|---------------|
| "Users follow the intended flow" | Attacker sends requests directly | State bypass |
| "Hidden fields can't be modified" | All client data is attacker-controlled | Parameter manipulation |
| "Rate limiting on login = safe" | Other endpoints unprotected | Brute-force via alternate path |
| "2FA is enabled = account is safe" | 2FA can be disabled, bypassed | False sense of security |
| "Session cookie = authenticated" | Session may be in partially-auth state | Incomplete verification |
| "Password reset = trusted action" | Can be triggered by attacker | Password reset abuse |

---

## Logic Flaw Detection Methodology

### Testing Checklist

```
1. MAP THE FLOW
   └─► Identify every step in authentication
   └─► Document expected state transitions
   └─► Note what data is passed between steps

2. TEST STATE TRANSITIONS
   └─► Skip steps (access step N+1 directly)
   └─► Repeat steps (replay step N)
   └─► Reverse steps (go back from step N to N-1)

3. TEST PARAMETER INTEGRITY
   └─► Modify cookies between steps
   └─► Change hidden form fields
   └─► Add/remove parameters
   └─► Change parameter values (user identity)

4. TEST ENFORCEMENT CONSISTENCY
   └─► Same action via different endpoints
   └─► Mobile vs desktop vs API
   └─► Different subdomains
   └─► Older API versions

5. TEST EDGE CASES
   └─► Concurrent sessions during auth
   └─► Race conditions between steps
   └─► Timeout behavior
   └─► Error handling paths
```

### Tool Support

| Tool | Use Case |
|------|----------|
| **Burp Suite Repeater** | Replay và modify individual requests |
| **Burp Intruder** | Automated parameter fuzzing |
| **Burp Session Handling** | Maintain complex multi-step flows |
| **Browser DevTools** | Cookie manipulation, hidden field editing |
| **Custom Scripts** | Complex state machine testing |

## Related Files

- [Password-based Attacks](01-password-based-attacks.md)
- [2FA Bypass Techniques](04-2fa-bypass-techniques.md)
- [Password Reset Vulnerabilities](05-password-reset-vulnerabilities.md)
- [Defense & Mitigation](08-defense-mitigation.md)
