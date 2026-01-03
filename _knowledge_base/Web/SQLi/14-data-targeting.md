# Data Targeting and Extraction Optimization

## Overview

Efficiently locate sensitive data to minimize time spent in compromised databases.

## MySQL Data Targeting

### Database Size Analysis

```sql
-- List databases by size
SELECT table_schema AS 'Database',
  ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS 'Size (MB)'
FROM information_schema.TABLES
GROUP BY table_schema
ORDER BY SUM(data_length + index_length) DESC;
```

### Keyword-based Search

```sql
-- Find databases with keywords
SELECT table_schema FROM information_schema.TABLES
WHERE table_schema LIKE '%password%'
  OR table_schema LIKE '%admin%'
  OR table_schema LIKE '%user%'
GROUP BY table_schema;

-- Find tables with keywords
SELECT table_schema,table_name FROM information_schema.tables
WHERE table_name LIKE '%admin%'
  OR table_name LIKE '%user%'
  OR table_name LIKE '%credit%'
  OR table_name LIKE '%payment%';

-- Find columns with keywords
SELECT table_name,column_name FROM information_schema.columns
WHERE column_name LIKE '%password%'
  OR column_name LIKE '%ssn%'
  OR column_name LIKE '%credit%'
  OR column_name LIKE '%card%';
```

### Regex Pattern Matching

```sql
-- Find credit card numbers (Visa starting with 4)
SELECT * FROM credit_cards
WHERE cc_number REGEXP '^4[0-9]{15}$';

-- Find all major credit cards
SELECT * FROM payments
WHERE card_number REGEXP '^(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13})$';

-- Find SSN patterns
SELECT * FROM users
WHERE ssn REGEXP '^[0-9]{3}-?[0-9]{2}-?[0-9]{4}$';
```

## MSSQL Data Targeting

### Non-default Database Discovery

```sql
-- List non-system databases
SELECT name FROM master..sysdatabases
WHERE name NOT IN ('master','model','msdb','tempdb','distribution',
                   'reportserver','reportservertempdb','resource')
ORDER BY name;
```

### Large Table Discovery

```sql
-- Find tables with most rows
SELECT t.name AS table_name,
  i.rows AS row_count
FROM sys.tables t
INNER JOIN sys.sysindexes i ON t.object_id = i.id AND i.indid < 2
WHERE i.rows > 0
ORDER BY i.rows DESC;
```

### Column Search

```sql
-- Find columns by keyword
SELECT table_name,column_name,data_type
FROM information_schema.columns
WHERE column_name LIKE '%password%'
  OR column_name LIKE '%ssn%'
  OR column_name LIKE '%credit%';
```

### Encrypted Database Detection

```sql
-- Find encrypted databases
SELECT name,is_encrypted FROM sys.databases
WHERE is_encrypted = 1;
```

## Oracle Data Targeting

### Find Sensitive Columns

```sql
-- Search column names
SELECT owner,table_name,column_name
FROM all_tab_columns
WHERE column_name LIKE '%PASS%'
  OR column_name LIKE '%SSN%'
  OR column_name LIKE '%CREDIT%';

-- Find by data type (for large text fields)
SELECT owner,table_name,column_name,data_type
FROM all_tab_columns
WHERE data_type IN ('VARCHAR2','CLOB')
  AND data_length > 100;
```

## Sensitive Data Keywords

Common column/table name patterns:

| Category | Keywords |
|----------|----------|
| Authentication | password, passwd, pwd, hash, salt, secret, token |
| Personal Info | ssn, social, dob, birth, address, phone, email |
| Financial | credit, card, cvv, pan, account, balance, payment |
| Internal | admin, root, system, config, key, api |
| Confidential | confidential, private, sensitive, restricted |

## Regex Patterns for Data Validation

### Credit Cards

```regex
# Visa (starts with 4, 16 digits)
^4[0-9]{15}$

# MasterCard (51-55, 16 digits)
^5[1-5][0-9]{14}$

# American Express (34 or 37, 15 digits)
^3[47][0-9]{13}$

# All major providers
^(?:4[0-9]{12}(?:[0-9]{3})?|(?:5[1-5][0-9]{2}|222[1-9]|22[3-9][0-9]|2[3-6][0-9]{2}|27[01][0-9]|2720)[0-9]{12}|3[47][0-9]{13}|3(?:0[0-5]|[68][0-9])[0-9]{11}|6(?:011|5[0-9]{2})[0-9]{12}|(?:2131|1800|35\d{3})\d{11})$
```

### Social Security Numbers

```regex
# Standard format (123-45-6789)
^\d{3}-\d{2}-\d{4}$

# With or without dashes
^\d{3}-?\d{2}-?\d{4}$

# Including masked (XXX-XX-XXXX)
^(\d{3}-?\d{2}-?\d{4}|XXX-XX-XXXX)$
```

### Email Addresses

```regex
^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$
```

## Quick Wins

Priority order for data targeting:

1. **User credentials**: `users`, `accounts`, `logins` tables
2. **Admin accounts**: WHERE `role='admin'` or `is_admin=1`
3. **API keys**: `config`, `settings`, `api_keys` tables
4. **Financial data**: `payments`, `transactions`, `credit_cards`
5. **Session tokens**: `sessions`, `tokens` tables
6. **Personal info**: `customers`, `profiles`, `members`

## Extraction Optimization

### Prioritize High-Value Data

```sql
-- Get admin credentials first
SELECT username,password FROM users WHERE role='admin' LIMIT 1;

-- Get newest/most active records
SELECT * FROM users ORDER BY last_login DESC LIMIT 10;

-- Get records with most data
SELECT * FROM customers ORDER BY LENGTH(notes) DESC LIMIT 10;
```

### Minimize Queries

```sql
-- Get everything in one shot with CONCAT
SELECT CONCAT_WS('|', username, email, password, ssn) FROM users;

-- Use GROUP_CONCAT for multiple rows (MySQL)
SELECT GROUP_CONCAT(username,':',password SEPARATOR '\n') FROM users;
```
