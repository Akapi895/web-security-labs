# Password Reset Vulnerabilities

## Overview

Chức năng password reset tồn tại trong hầu hết mọi ứng dụng web — và vì bản chất nó phải cho phép truy cập account **mà không cần password hiện tại**, nó trở thành một trong những attack surface nguy hiểm nhất trong authentication system.

**Bản chất kỹ thuật**: Password reset phá vỡ mô hình "something you know" và thay thế bằng cơ chế xác minh thay thế (email, security question, phone). Nếu cơ chế thay thế này yếu, toàn bộ authentication bị bypass.

## Phân loại các phương thức Reset

| Phương thức | Mô tả | Rủi ro |
|-------------|--------|--------|
| **Gửi password mới qua email** | Server generate password mới và gửi plain text | Rất cao — persistent plaintext |
| **Reset URL với token** | Gửi link chứa token để đặt password mới | Phụ thuộc vào token quality |
| **Security questions** | Yêu cầu trả lời câu hỏi bảo mật | Cao — thường đoán được |
| **SMS/Phone verification** | Gửi code qua SMS | Trung bình — SIM swapping |

---

## 1. Gửi Password qua Email

### Vấn đề

Nếu website có thể gửi **current password** qua email, điều đó chứng tỏ password **không được hash** — vi phạm security principle cơ bản.

### Ngay cả khi gửi password MỚI

```
Rủi ro chain:
  Server generate password → gửi qua email → user nhận
       │                         │
       ▼                         ▼
  Email insecure:           Password persistent:
  - SMTP không encrypted    - Nằm trong inbox vĩnh viễn
  - Email sync nhiều device  - Accessible nếu email bị hack
  - Man-in-the-middle       - Backup email servers
```

### Điều kiện an toàn (nếu bắt buộc dùng phương thức này)

- Password mới phải **expire** sau thời gian rất ngắn
- Buộc user **đổi password** ngay lần login đầu
- Invalidate password cũ ngay lập tức

---

## 2. Password Reset URL — Token-based

### Cách hoạt động (đúng)

```
1. User request reset password
2. Server generate high-entropy token
3. Server gửi email chứa URL: 
   https://app.com/reset?token=a0ba0d1cb3b63d13822572fcff1a241895d893f659164d4cc550b421ebdd48a8
4. User click link → server verify token → cho phép đặt password mới
5. Token bị destroy sau khi sử dụng
```

### Vulnerability: Predictable Token

Nếu token được tạo từ data đoán được:

| Token Pattern | Predictability | Khai thác |
|---------------|---------------|-----------|
| `md5(username)` | Trivial | Tự generate token cho bất kỳ user |
| `md5(email + timestamp)` | Medium | Biết email + đoán timestamp |
| `sequential_id` | Trivial | Enumeration |
| `base64(username:email)` | Trivial | Decode structure |
| `HMAC(server_secret, random)` | Khó | Cần biết secret |

### Vulnerability: Predictable Parameter

```
# Insecure — user identity trong URL parameter
https://app.com/reset-password?user=victim-user
→ Attacker thay đổi ?user=admin → reset password admin

# Secure — chỉ dùng token, không expose user identity
https://app.com/reset-password?token=random_high_entropy_token
```

### Vulnerability: Token Not Re-validated on Submit

```
Flow bình thường:
1. User truy cập reset page với token
2. Server verify token → hiển thị form đặt password
3. User submit password mới
4. Server verify token LẦN NỮA → update password

Flow vulnerable:
1. User truy cập reset page với token  
2. Server verify token → hiển thị form
3. Attacker truy cập CÙNG form (hoặc xóa token khỏi request)
4. Server KHÔNG verify token lần 2 → chấp nhận password mới
   → Attacker chỉ cần biết reset page URL
```

### Kỹ thuật khai thác chi tiết

```http
# Step 1: Trigger reset cho attacker account, nhận valid token
POST /forgot-password
email=attacker@email.com

# Step 2: Dùng token để mở reset form
GET /reset-password?token=valid_token_here

# Step 3: Submit form NHƯNG thay đổi username/email
POST /reset-password
token=valid_token_here&username=victim&new_password=hacked123

# Hoặc xóa token hoàn toàn
POST /reset-password
username=victim&new_password=hacked123
```

---

## 3. Password Reset Poisoning

### Bản chất

Khi ứng dụng tạo reset URL **dynamically** dựa trên HTTP headers (Host, X-Forwarded-Host), attacker có thể đầu độc URL để redirect victim đến server của attacker — từ đó đánh cắp reset token.

### Flow khai thác

```
1. Attacker gửi reset request VỚI Host header bị thay đổi:

POST /forgot-password HTTP/1.1
Host: attacker-server.com        ← poisoned
Content-Type: application/x-www-form-urlencoded

email=victim@email.com

2. Server tạo reset URL dùng Host header:
   https://attacker-server.com/reset?token=secret_token_here

3. Victim nhận email → click link → request gửi đến attacker server
   → Attacker capture token từ request

4. Attacker dùng token với target thật:
   https://real-app.com/reset?token=secret_token_here
   → Reset password victim thành công
```

### Các Header có thể dùng để Poison

| Header | Ví dụ |
|--------|-------|
| `Host` | `Host: attacker.com` |
| `X-Forwarded-Host` | `X-Forwarded-Host: attacker.com` |
| `X-Host` | `X-Host: attacker.com` |
| `X-Forwarded-Server` | `X-Forwarded-Server: attacker.com` |
| `Forwarded` | `Forwarded: host=attacker.com` |

---

## 4. Password Change Functionality

### Bản chất

Trang đổi password thường yêu cầu: (1) current password, (2) new password, (3) confirm new password. Về bản chất, nó thực hiện **cùng logic** với login form — và có thể chứa cùng vulnerabilities.

### Attack Vectors

#### Hidden Username Field

```html
<!-- Username trong hidden field — attacker có thể edit -->
<form action="/change-password" method="POST">
  <input type="hidden" name="username" value="victim-user">
  <input type="password" name="current-password">
  <input type="password" name="new-password">
</form>
```

```http
# Attacker thay đổi username trong request
POST /change-password
username=admin&current-password=test&new-password=hacked123
```

#### Brute-force Current Password

Nếu password change endpoint **không có rate limiting**, attacker brute-force current password:

```
POST /change-password
username=victim&current-password=attempt1&new-password=hacked

POST /change-password  
username=victim&current-password=attempt2&new-password=hacked

...
```

#### Access Without Authentication

Một số password change pages accessible **mà không cần login**:

```
# Direct access without session
GET /change-password?username=victim
→ Nếu server không verify session → attacker đổi password victim
```

---

## 5. Security Question Weaknesses

| Vấn đề | Mô tả |
|---------|--------|
| **Guessable answers** | "What city were you born in?" — hữu hạn, public info |
| **Consistent answers** | Người dùng trả lời giống nhau trên nhiều sites |
| **Social engineering** | OSINT có thể tìm answer (social media, public records) |
| **No rate limiting** | Brute-force answer cũng như brute-force password |

---

## Attack Workflow — Password Reset

```
┌──────────────────────────────────────────────────────────────────────┐
│               PASSWORD RESET ATTACK WORKFLOW                         │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  1. IDENTIFY      ──► Tìm reset mechanism: URL? Email? Question?     │
│        │                                                             │
│        ▼                                                             │
│  2. ANALYZE TOKEN ──► Token có predictable? Có trong response?       │
│        │               URL chứa user parameter?                      │
│        ▼                                                             │
│  3. TEST POISONING──► Thử thay đổi Host header                      │
│        │               Kiểm tra email chứa URL poisoned?             │
│        ▼                                                             │
│  4. TEST VALIDATION─► Token có bị re-validate khi submit?            │
│        │               Xóa token có bypass được không?               │
│        ▼                                                             │
│  5. CHECK CHANGE  ──► Password change endpoint accessible?           │
│        │               Hidden username field?                        │
│        ▼                                                             │
│  6. EXPLOIT       ──► Thực thi attack phù hợp                       │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

## Related Files

- [Authentication Logic Flaws](07-authentication-logic-flaws.md)
- [Session & Credential Management](06-session-and-credential-management.md)
- [Defense & Mitigation](08-defense-mitigation.md)
