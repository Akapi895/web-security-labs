# SQLi-048: MySQL Comment Filter Bypass

## 🎯 Mục Tiêu

Bypass filter chặn `--` comment bằng alternative comment syntax `#` hoặc `/**/`.

## 📝 Mô Tả

**Scenario:** WAF chặn SQL comment sequence `--` để ngăn comment injection.

**URL:** `http://localhost:5048/profile?user=admin`

## 🎓 Kiến Thức Cần Biết

### MySQL Comment Alternatives

```sql
-- Standard comment (bị block)
SELECT * FROM users WHERE id=1--

-- Hash comment (MySQL specific)
SELECT * FROM users WHERE id=1#

-- C-style comment
SELECT * FROM users WHERE id=1/*comment*/

-- Kết hợp
SELECT * FROM users WHERE id=1;-- (với semicolon)
```

## 🚀 Khởi Chạy Lab

```bash
cd Module-07-Filter-Bypass/SQLi-048
docker-compose up -d
```

## 💡 Gợi Ý

1. MySQL hỗ trợ nhiều loại comments
2. `#` là MySQL-specific comment
3. `/* */` có thể dùng cho inline và line comment

## 🏁 Flag Format

```
FLAG{...}
```
