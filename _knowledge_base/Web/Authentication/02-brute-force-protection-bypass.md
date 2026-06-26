# Brute-force Protection Bypass

## Overview

Hầu hết ứng dụng web triển khai một số hình thức bảo vệ chống brute-force — nhưng mỗi cơ chế đều có điểm yếu logic có thể bị khai thác. Hiểu rõ bản chất từng loại protection giúp attacker xác định chiến lược bypass phù hợp.

## Các cơ chế Protection phổ biến

| Cơ chế | Mô tả | Điểm yếu tiềm ẩn |
|--------|--------|-------------------|
| **Account Locking** | Khóa account sau N lần đăng nhập sai | Username enumeration, password spraying |
| **IP Blocking** | Block IP sau nhiều request thất bại | Counter reset, header spoofing |
| **Rate Limiting** | Giới hạn tốc độ request | Slow brute-force, multi-IP |
| **CAPTCHA** | Yêu cầu giải captcha | Bypass service, logic flaws |
| **Login Delay** | Tăng delay sau mỗi lần sai | Chỉ hiệu quả nếu implement đúng |

## Account Locking Bypass

### Bản chất vấn đề

Account locking bảo vệ **một account cụ thể** khỏi bị brute-force. Tuy nhiên, nó **không** bảo vệ khi attacker không nhắm vào một account duy nhất.

### Password Spraying

Thay vì thử nhiều password cho một username, attacker thử **ít password cho nhiều username**:

```
Brute-force truyền thống (bị chặn):
  admin → password1, password2, password3, ... → LOCKED

Password Spraying (không bị chặn):
  user1 → Password1!
  user2 → Password1!
  user3 → Password1!
  ...
  user1 → Summer2024!    ← mỗi account chỉ bị thử 1-2 lần
  user2 → Summer2024!
```

### Chiến lược Password Spraying

| Bước | Hành động |
|------|-----------|
| 1 | Thu thập danh sách valid usernames (qua enumeration hoặc common names) |
| 2 | Chọn **rất ít** password phổ biến (≤ lockout threshold) |
| 3 | Thử từng password với **tất cả** usernames |
| 4 | Chỉ cần 1 user dùng 1 trong các password đó → thành công |

**Lưu ý**: Nếu lockout threshold là 3 lần, chỉ cần chọn tối đa 3 passwords nhưng spray cho hàng trăm usernames.

### Account Locking → Username Enumeration

Một hệ quả không mong muốn: response "Account is locked" xác nhận rằng username **tồn tại**. Attacker có thể lợi dụng điều này để xây dựng danh sách valid usernames.

## IP-based Blocking Bypass

### Counter Reset Flaw

Một số implementation reset bộ đếm failed attempts khi IP owner **đăng nhập thành công**. Attacker khai thác bằng cách xen kẽ login vào account của chính mình:

```
Request 1: admin:password1      → Failed (count=1)
Request 2: admin:password2      → Failed (count=2)
Request 3: attacker:validpass   → SUCCESS → counter reset!
Request 4: admin:password3      → Failed (count=1)  ← reset rồi
Request 5: admin:password4      → Failed (count=2)
Request 6: attacker:validpass   → SUCCESS → counter reset!
...
```

**Kỹ thuật**: Chèn credential hợp lệ của attacker vào wordlist ở mỗi N entries (N < lockout threshold).

### IP Header Spoofing

Một số ứng dụng xác định client IP qua header thay vì TCP connection:

```http
X-Forwarded-For: 1.2.3.4
X-Real-IP: 5.6.7.8
X-Originating-IP: 9.10.11.12
X-Client-IP: 13.14.15.16
```

**Khai thác**: Thay đổi giá trị header sau mỗi vài request để giả mạo IP mới.

> ⚠️ **Lưu ý**: Chỉ hoạt động khi server tin tưởng header thay vì IP thực từ TCP socket. Thường gặp khi ứng dụng đứng sau reverse proxy nhưng không cấu hình trust đúng.

## Rate Limiting Bypass

### Slow Brute-force

Khi rate limit kiểm tra **tốc độ** request thay vì tổng số:

```
Thay vì: 1000 requests/phút → BỊ CHẶN
Dùng:    1 request/3 giây   → Dưới ngưỡng rate limit
          = ~1200 attempts/giờ = ~28,800/ngày
```

### Code Resend Reset

Với OTP/2FA, resend code thường **reset rate limit counter**:

```
1. Thử 5 OTP codes → rate limit triggered
2. Request resend code → counter reset
3. Thử thêm 5 OTP codes
4. Request resend code → counter reset
... lặp vô hạn
```

### Multiple Passwords per Request

Nếu rate limit đếm theo **số request** thay vì **số attempts**, attacker có thể gửi nhiều password trong một request:

```json
POST /login
{
  "username": "victim",
  "password": ["password1", "password2", "password3", ...]
}
```

Hoặc exploit JSON array/parameter pollution tùy theo backend xử lý.

### Client-side Rate Limiting

Rate limiting implement ở client-side (JavaScript) có thể bypass hoàn toàn bằng cách gửi request trực tiếp qua Burp Suite hoặc curl, bỏ qua frontend validation.

## Rate Limiting vs Account Locking — So sánh

| Tiêu chí | Account Locking | Rate Limiting |
|----------|-----------------|---------------|
| **Username enumeration** | Có thể bị lợi dụng | Ít bị lợi dụng |
| **DoS potential** | Attacker lock account nạn nhân | Không gây DoS account |
| **Password spraying** | Không bảo vệ | Bảo vệ tốt hơn |
| **Bypass difficulty** | Dễ bypass với spraying | Khó hơn nhưng vẫn khả thi |

## Internal Actions Without Rate Limit

Một lỗi phổ biến: ứng dụng chỉ rate limit **login endpoint** nhưng không protect:

| Endpoint | Thường được protect? | Attack vector |
|----------|---------------------|---------------|
| `/login` | ✓ | — |
| `/api/login` | Không chắc | Brute-force qua API |
| `/forgot-password` | Thường không | Token enumeration |
| `/verify-otp` | Thường không | OTP brute-force |
| `/change-password` | Thường không | Current password brute-force |

## Response Behavior Analysis

Ngay cả khi có rate limit, attacker có thể phân biệt valid vs invalid credential qua **response khác biệt**:

```
Invalid OTP (rate limited):  → 401 Unauthorized
Valid OTP (rate limited):    → 200 OK  ← response khác!
```

**Key insight**: Rate limit có thể block request nhưng vẫn **leak** thông tin qua status code khác nhau khi credential đúng.

## Bypass Decision Tree

```
┌─────────────────────────┐
│ Protection mechanism?   │
└──────────┬──────────────┘
           │
     ┌─────┼──────────┐
     ▼     ▼          ▼
  Account  IP-based   Rate
  Locking  Blocking   Limiting
     │     │          │
     ▼     ▼          ▼
  Password Counter    Slow
  Spraying Reset?     brute-force
     │     │  │       │
     │    Yes  No     ▼
     │     │   │    Multi-password
     │     ▼   ▼    per request?
     │  Interleave  Header
     │  valid login spoofing
     │
     ▼
  Credential
  Stuffing
  (1 attempt/account)
```

## Related Files

- [Password-based Attacks](01-password-based-attacks.md)
- [2FA Bypass Techniques](04-2fa-bypass-techniques.md)
- [Defense & Mitigation](08-defense-mitigation.md)
