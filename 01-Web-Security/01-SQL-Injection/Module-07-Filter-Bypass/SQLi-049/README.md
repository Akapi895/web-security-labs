# SQLi-049: MySQL Quote Filter Bypass with Hex Encoding

## 🎯 Mục Tiêu

Bypass filter chặn quote characters (`'` và `"`) bằng hex encoding.

## 📝 Mô Tả

**Scenario:** URL validation filter chặn tất cả quote characters để ngăn string injection.

**URL:** `http://localhost:5049/login?user=admin&pass=test`

## 🎓 Kiến Thức Cần Biết

### Hex Encoding trong MySQL

```sql
-- Thay vì string literals
SELECT * FROM users WHERE username = 'admin'

-- Dùng hex encoding
SELECT * FROM users WHERE username = 0x61646D696E
-- 0x61646D696E = hex của 'admin'
```

### Ví dụ

```python
# Python convert string to MySQL hex
>>> 'admin'.encode().hex()
'61646d696e'
# Prefix 0x: 0x61646d696e
```

## 🚀 Khởi Chạy Lab

```bash
cd Module-07-Filter-Bypass/SQLi-049
docker-compose up -d
```

## 💡 Gợi Ý

1. Test injection với quote → bị block
2. MySQL hiểu hex literals như strings
3. `0x61646D696E` = 'admin'

## 🏁 Flag Format

```
FLAG{...}
```
