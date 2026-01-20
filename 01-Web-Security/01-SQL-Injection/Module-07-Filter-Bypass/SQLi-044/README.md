# SQLi-044: PostgreSQL Whitespace Filter Bypass

## 🎯 Mục Tiêu

Bypass WAF filter chặn tất cả whitespace characters để thực hiện SQL Injection trên PostgreSQL.

## 📝 Mô Tả

**Scenario:** Một REST API xác thực dữ liệu đầu vào được bảo vệ bằng filter loại bỏ tất cả whitespace (space, tab, newline). Filter này sử dụng regex để phát hiện và chặn.

**URL:** `http://localhost:5044/api/user?id=1`

**Filter Behavior:**
- Request có whitespace → ❌ "Whitespace characters are not allowed"
- Request không có whitespace → ✅ Query thực thi bình thường

## 🎓 Kiến Thức Cần Biết

### Bypass Whitespace với Parentheses

Trong SQL, parentheses có thể thay thế spaces trong nhiều trường hợp:

```sql
-- Original (cần space)
SELECT username FROM users

-- Bypass với parentheses
SELECT(username)FROM(users)

-- Boolean logic với parentheses
WHERE(1)=(1)
WHERE(id)=(1)OR(1)=(1)
```

### PostgreSQL Specific Techniques

```sql
-- Type casting không cần space
SELECT('test')::text

-- Subquery với parentheses
SELECT(SELECT(username)FROM(users)LIMIT(1))
```

## 🚀 Khởi Chạy Lab

```bash
cd Module-07-Filter-Bypass/SQLi-044
docker-compose up -d
```

Truy cập: `http://localhost:5044`

## 💡 Gợi Ý

1. Try các endpoint API, quan sát response format
2. Xác định injection point với `'`
3. Tìm cách xây dựng payload không có whitespace
4. Sử dụng parentheses để bọc các thành phần SQL

## 🏁 Flag Format

```
FLAG{...}
```

Flag nằm trong bảng `flags` của database.
