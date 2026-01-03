# SQLi-022: PostgreSQL Union-based - Multi Row (STRING_AGG)

## 🎯 Mục Tiêu

Khai thác SQL Injection trên PostgreSQL bằng kỹ thuật **Union-based** với `STRING_AGG()` để aggregate nhiều rows thành 1 string.

## 📝 Mô Tả

Ứng dụng Corporate Directory cho phép xem danh sách nhân viên theo phòng ban. Response hiển thị **tất cả employees** của department (multiple rows).

**URL:** `http://localhost:5022/department?id=1`

Database chứa các bảng:
- `departments`: Phòng ban (id, name, location)
- `employees`: Nhân viên (id, name, email, department_id, position)
- `admin_credentials`: Tài khoản admin (id, username, password, role, session_token)
- `flags`: Chứa flag bí mật

## 🎓 Kiến Thức Cần Biết

### STRING_AGG (PostgreSQL)

```sql
-- Aggregate nhiều rows thành 1 string (PostgreSQL 9.0+)
SELECT STRING_AGG(name, ', ') FROM employees;
-- Output: Alice, Bob, Carol, David

-- Với ORDER BY
SELECT STRING_AGG(name, ', ' ORDER BY name) FROM employees;
```

### So sánh với MySQL

| MySQL              | PostgreSQL         |
| ------------------ | ------------------ |
| GROUP_CONCAT()     | STRING_AGG()       |
| SEPARATOR 'x'      | 'x' (as 2nd param) |
| ORDER BY in func   | ORDER BY in func   |

### PostgreSQL-specific

```sql
-- || operator cho concatenation
SELECT username || ':' || password FROM admin;

-- Version check
SELECT version();
```

## 🚀 Hướng Dẫn Triển Khai

```bash
# Khởi động lab
docker-compose up -d

# Chờ PostgreSQL khởi động (khoảng 20s)
docker-compose logs -f db

# Test ứng dụng
curl "http://localhost:5022/department?id=1"

# Dừng lab
docker-compose down
```

## 💡 Gợi Ý

1. **Bước 1:** Tìm điểm injection trong parameter `id`
2. **Bước 2:** Xác định PostgreSQL qua error messages (ERROR:...)
3. **Bước 3:** Enumerate với `information_schema.tables`
4. **Bước 4:** Dùng STRING_AGG để aggregate all credentials
5. **Bước 5:** Extract session tokens và passwords
6. **Bước 6:** Lấy flag từ bảng flags

## 📚 Tài Liệu Tham Khảo

- [Writeup chi tiết](solution/writeup.md)
- [Exploit script](solution/exploit.py)
- [PostgreSQL STRING_AGG](https://www.postgresql.org/docs/15/functions-aggregate.html)

## 🏁 Flag Format

`FLAG{...}`
