# Password-based Attacks

## Overview

Trong mô hình xác thực dựa trên mật khẩu, bảo mật phụ thuộc hoàn toàn vào việc giữ bí mật credential. Nếu attacker có thể **đoán**, **đánh cắp**, hoặc **suy luận** được username/password, toàn bộ cơ chế xác thực sụp đổ.

Phần này tập trung vào các kỹ thuật tấn công trực tiếp vào cơ chế password-based login — bao gồm brute-force, username enumeration, và credential stuffing.

## Brute-force Attack Fundamentals

### Bản chất

Brute-force là phương pháp thử sai (trial-and-error) tự động hóa để đoán credential. Attacker sử dụng wordlist chứa username và password phổ biến, kết hợp với công cụ như Burp Intruder, Hydra, hoặc custom scripts.

### Điều quan trọng cần hiểu

Brute-force **không chỉ** là thử ngẫu nhiên. Attacker áp dụng logic và kiến thức thực tế để tối ưu hóa:

| Chiến lược | Mô tả | Hiệu quả |
|------------|--------|-----------|
| **Wordlist-based** | Dùng danh sách password phổ biến (rockyou, SecLists) | Cao — phủ 80%+ password thực tế |
| **Pattern-based** | Dựa trên hành vi con người: `Mypassword1!`, `Summer2024!` | Rất cao khi policy yếu |
| **Hybrid** | Kết hợp từ điển + mutation rules | Cao với hashcat rules |
| **Credential reuse** | Dùng credential leak từ data breach khác | Rất cao — nhiều user dùng lại password |

## Username Enumeration

### Khái niệm

Username enumeration xảy ra khi ứng dụng **phản hồi khác nhau** tùy thuộc vào username có tồn tại hay không. Điều này cho phép attacker xây dựng danh sách valid usernames trước khi brute-force password.

### Các tín hiệu phát hiện

| Tín hiệu | Mô tả | Cách phát hiện |
|-----------|--------|----------------|
| **Status Code** | Response trả HTTP status khác nhau cho valid/invalid username | So sánh status code khi thử nhiều username |
| **Error Message** | Thông báo lỗi khác nhau: "Invalid username" vs "Invalid password" | Đọc kỹ nội dung error message |
| **Response Time** | Server chỉ check password khi username valid → response chậm hơn | Đo thời gian response, dùng password rất dài để khuếch đại sự khác biệt |
| **Response Length** | Body size khác nhau cho valid vs invalid | So sánh Content-Length header |

### Ví dụ phân tích Response

```
# Invalid username — server không check password
POST /login → 200 OK, 2341 bytes, 50ms
Body: "Invalid username or password"

# Valid username — server check password → mất thêm thời gian
POST /login → 200 OK, 2342 bytes, 180ms  
Body: "Invalid username or password."
                                  ^ dấu chấm khác — lỗi typing tinh vi
```

**Key insight**: Ngay cả một ký tự khác biệt (khoảng trắng, dấu chấm) cũng đủ để phân biệt — dù trên rendered page trông giống nhau.

### Các nguồn Username phổ biến

| Nguồn | Ví dụ |
|-------|-------|
| **User profiles** | Trang profile public có thể tiết lộ username |
| **HTTP responses** | Email address trong response headers hoặc body |
| **Pattern prediction** | Format `firstname.lastname@company.com` |
| **Common usernames** | `admin`, `administrator`, `root`, `test` |
| **Registration form** | "Username already taken" khi đăng ký |

## Password Brute-force — Hiểu hành vi người dùng

### Password Policy vs Human Behavior

Khi website yêu cầu password phức tạp, người dùng thường **không** tạo password thực sự random mà **biến tấu** từ password dễ nhớ:

| Policy yêu cầu | Password gốc | Biến tấu phổ biến |
|-----------------|--------------|---------------------|
| Uppercase + number + special | `mypassword` | `Mypassword1!` |
| Special character | `password` | `P@ssw0rd` |
| Periodic change | `Mypassword1!` | `Mypassword2!`, `Mypassword1?` |

**Chiến lược khai thác**: Xây dựng mutation rules dựa trên các pattern trên — ví dụ với Hashcat rules hoặc John the Ripper mangling.

### Hiệu quả của Password Brute-force

```
Password entropy thấp (dictionary word + simple mutation):
  → Wordlist 10,000 entries có thể crack ~5% accounts

Password entropy cao (truly random 12+ chars):
  → Brute-force không khả thi trong thời gian hợp lý
```

## Credential Stuffing

### Khác biệt với Brute-force

| | Brute-force | Credential Stuffing |
|---|-------------|---------------------|
| **Input** | Wordlist generic | Credential pairs từ data breaches |
| **Tỷ lệ thành công** | Thấp (0.1-1%) | Cao hơn nhiều (1-5%) |
| **Mỗi username** | Thử nhiều passwords | Chỉ thử 1 password (original) |
| **Bypass lockout** | Bị chặn bởi account lock | Không bị — mỗi account chỉ 1 lần thử |

### Tại sao Credential Stuffing nguy hiểm

Credential stuffing khai thác thực tế rằng **nhiều người dùng cùng username + password trên nhiều website**. Một database bị breach ở site A có thể dùng để đăng nhập vào site B.

**Đặc điểm quan trọng**: Account locking **không** bảo vệ được trước credential stuffing vì mỗi username chỉ bị thử đúng 1 lần.

## HTTP Basic Authentication

### Cách hoạt động

Client gửi credential trong mỗi request qua header `Authorization`:

```http
Authorization: Basic base64(username:password)
```

Token được browser quản lý và tự động gửi kèm mọi subsequent request.

### Điểm yếu

| Vấn đề | Mô tả | Impact |
|---------|--------|--------|
| **Credential trong mọi request** | Username:password gửi lặp lại liên tục | MITM capture nếu không có HSTS |
| **Static token** | Token không thay đổi, dễ bị brute-force | Không có session rotation |
| **Không có CSRF protection** | Inherently vulnerable với CSRF | Cross-site attacks |
| **Credential reuse** | Password lộ ở basic auth endpoint có thể dùng cho context khác | Lateral movement |

### Ví dụ khai thác

```
# Decode Base64 token từ captured request
Authorization: Basic YWRtaW46cGFzc3dvcmQxMjM=

$ echo "YWRtaW46cGFzc3dvcmQxMjM=" | base64 -d
admin:password123
```

## Attack Decision Tree

```
                    ┌────────────────────┐
                    │ Có login form?     │
                    └─────────┬──────────┘
                              │ Yes
                    ┌─────────▼──────────┐
                    │ Username           │
                    │ enumeration có     │──── Yes ──► Xây dựng valid
                    │ hoạt động?         │             username list
                    └─────────┬──────────┘
                              │ No
                    ┌─────────▼──────────┐
                    │ Có brute-force     │
                    │ protection?        │──── No ───► Direct brute-force
                    └─────────┬──────────┘
                              │ Yes
                    ┌─────────▼──────────┐
                    │ Loại protection?   │
                    └──┬──────┬──────┬───┘
                       │      │      │
                  Account  IP-based  Rate
                  Lockout  Block     Limit
                       │      │      │
                       ▼      ▼      ▼
               Password  X-FF    Multiple
               Spraying  Header  passwords
                         Spoof   per request
```

## Công cụ phổ biến

| Tool | Mục đích | Đặc điểm |
|------|----------|-----------|
| **Burp Intruder** | Brute-force, enumeration | Sniper/Pitchfork/Cluster bomb modes |
| **Hydra** | Network login brute-force | Hỗ trợ nhiều protocol |
| **Turbo Intruder** | High-speed brute-force | Python scripting, race conditions |
| **ffuf** | Web fuzzing | Fast, flexible |
| **CeWL** | Custom wordlist generation | Crawl website để tạo wordlist |

## Related Files

- [Brute-force Protection Bypass](02-brute-force-protection-bypass.md)
- [Authentication Logic Flaws](07-authentication-logic-flaws.md)
- [Defense & Mitigation](08-defense-mitigation.md)
