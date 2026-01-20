# SQLi-052: PostgreSQL Equals Filter Bypass

## 🎯 Mục Tiêu

Bypass filter chặn ký tự `=` bằng các comparison alternatives như LIKE, BETWEEN, IN.

## 📝 Mô Tả

**Scenario:** WAF chặn ký tự `=` để ngăn condition manipulation và authentication bypass.

**URL:** `http://localhost:5052/user?id=1`

## 🎓 Kiến Thức Cần Biết

### Alternatives cho Equals

```sql
-- Standard equals (bị block)
WHERE username = 'admin'

-- LIKE (pattern matching)
WHERE username LIKE 'admin'

-- IN (list matching)
WHERE username IN ('admin')

-- BETWEEN (range matching)
WHERE id BETWEEN 1 AND 1

-- Regex (PostgreSQL)
WHERE username ~ '^admin$'

-- NOT comparison
WHERE NOT username <> 'admin'
```

## 🚀 Khởi Chạy Lab

```bash
cd Module-07-Filter-Bypass/SQLi-052
docker-compose up -d
```

## 💡 Gợi Ý

1. LIKE có thể thay thế = cho string comparison
2. BETWEEN x AND x = equals x
3. IN ('value') = equals 'value'

## 🏁 Flag Format

```
FLAG{...}
```
