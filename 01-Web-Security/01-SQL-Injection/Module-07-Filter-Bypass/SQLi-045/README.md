# SQLi-045: MySQL UNION Keyword Filter Bypass

## 🎯 Mục Tiêu

Bypass IDS/WAF filter chặn từ khóa `UNION` (case-insensitive) để thực hiện UNION-based SQL Injection trên MySQL.

## 📝 Mô Tả

**Scenario:** Một hệ thống blog được bảo vệ bởi IDS phát hiện và chặn từ khóa `UNION` trong tất cả các dạng viết hoa/thường.

**URL:** `http://localhost:5045/article?id=1`

**IDS Behavior:**
- Request chứa "union" (any case) → ❌ "Potential SQL injection detected"
- Request không chứa "union" → ✅ Query thực thi

## 🎓 Kiến Thức Cần Biết

### UNION Bypass Techniques

```sql
-- Original (bị block)
UNION SELECT 1,2,3

-- Case variation với comments inline
Un/**/IoN SeLeCt 1,2,3

-- URL encoding mixed
U%4eION SELECT 1,2,3

-- Double keyword (nếu filter replace 1 lần)
UNunionION SELECT 1,2,3
```

### MySQL Version Comments

```sql
-- MySQL sẽ execute code trong /*!...*/
/*!50000UNION*/ SELECT 1,2,3

-- Hoặc kết hợp
UN/**/ION SELECT 1,2,3
```

## 🚀 Khởi Chạy Lab

```bash
cd Module-07-Filter-Bypass/SQLi-045
docker-compose up -d
```

Truy cập: `http://localhost:5045`

## 💡 Gợi Ý

1. Xác định injection point với `'`
2. Thử UNION bình thường để confirm filter
3. Sử dụng inline comments `/**/` để chia nhỏ keyword
4. Một số ký tự có thể được URL encode

## 🏁 Flag Format

```
FLAG{...}
```
