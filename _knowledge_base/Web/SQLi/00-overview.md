# SQL Injection Overview

## Definition

SQL Injection (SQLi) is a code injection technique that exploits vulnerabilities in applications that construct SQL queries using untrusted input. Attackers can manipulate queries to:

- Read/modify/delete sensitive data
- Bypass authentication
- Execute administrative operations
- Read/write files on the server
- Execute OS commands

## Impact

| Impact | Description |
|--------|-------------|
| Confidentiality | Access to passwords, credit cards, personal data |
| Integrity | Modify or delete data |
| Authentication | Login as any user without password |
| Authorization | Escalate privileges |
| Availability | DoS via resource exhaustion |

## Classification by Technique

| Type | Description | Data Visibility |
|------|-------------|-----------------|
| Error-based | Extract data via database error messages | Direct |
| Union-based | Append results using UNION SELECT | Direct |
| Boolean Blind | Infer data from true/false responses | Indirect |
| Time-based Blind | Infer data from response delays | Indirect |
| Out-of-Band | Exfiltrate via DNS/HTTP requests | External |

## Classification by Injection Point

| Location | Example |
|----------|---------|
| URL Parameter | `?id=1'` |
| POST Body | `username=admin'--` |
| Cookie | `Cookie: session=x' OR 1=1--` |
| HTTP Header | `User-Agent: '` |
| JSON/XML | `{"id": "1'"}` |

## Injection Context

| Context | Example Payload |
|---------|-----------------|
| String (single quote) | `' OR '1'='1` |
| String (double quote) | `" OR "1"="1` |
| Numeric | `1 OR 1=1` |
| Column/Table name | Need different approach |

## Comment Characters

| DBMS | Single Line | Multi Line |
|------|-------------|------------|
| MySQL | `-- ` (space required), `#` | `/* */` |
| MSSQL | `--` | `/* */` |
| Oracle | `--` | `/* */` |
| PostgreSQL | `--` | `/* */` |

## DBMS Fingerprinting Quick Reference

| DBMS | Detection Query |
|------|-----------------|
| MySQL | `SELECT @@version`, `SLEEP(5)` |
| MSSQL | `SELECT @@version`, `WAITFOR DELAY '0:0:5'` |
| Oracle | `SELECT banner FROM v$version`, `FROM dual` required |
| PostgreSQL | `SELECT version()`, `pg_sleep(5)` |

## Attack Workflow

```
1. DETECT      -> Find injection points
2. IDENTIFY    -> Determine DBMS type
3. ENUMERATE   -> Tables, columns, data
4. EXTRACT     -> Retrieve sensitive data
5. ESCALATE    -> Privileges, OS access
6. EXFILTRATE  -> Export data externally
```

## String Concatenation

| DBMS | Syntax |
|------|--------|
| MySQL | `CONCAT('a','b')` or `'a' 'b'` |
| MSSQL | `'a'+'b'` |
| Oracle | `'a'\|\|'b'` |
| PostgreSQL | `'a'\|\|'b'` |

## Substring Functions

| DBMS | Syntax |
|------|--------|
| MySQL | `SUBSTRING(str,pos,len)`, `MID()`, `SUBSTR()` |
| MSSQL | `SUBSTRING(str,pos,len)` |
| Oracle | `SUBSTR(str,pos,len)` |
| PostgreSQL | `SUBSTRING(str,pos,len)` |

## Related Files

- [Detection](01-detection.md)
- [Error-based](02-error-based.md)
- [Union-based](03-union-based.md)
- [Boolean Blind](04-boolean-blind.md)
- [Time-based Blind](05-time-based-blind.md)
- [Out-of-Band](06-out-of-band.md)
- [Filter Bypass](07-filter-bypass.md)
- [MySQL](08-dbms-mysql.md)
- [MSSQL](09-dbms-mssql.md)
- [Oracle](10-dbms-oracle.md)
- [PostgreSQL](11-dbms-postgresql.md)
- [Automation Tools](12-automation-tools.md)
- [Defense](13-defense-mitigation.md)
- [Data Targeting](14-data-targeting.md)
