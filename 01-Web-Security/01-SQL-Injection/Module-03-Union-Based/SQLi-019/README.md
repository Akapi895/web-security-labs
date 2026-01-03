# SQLi-019: MySQL Union-based - Single Column (CONCAT/CONCAT_WS)

## 🎯 Mục Tiêu

Khai thác SQL Injection trên MySQL bằng kỹ thuật **Union-based** với `CONCAT/CONCAT_WS` để ghép nhiều giá trị trong 1 column.

## 📝 Mô Tả

Ứng dụng E-commerce có chức năng tìm kiếm sản phẩm. Kết quả chỉ hiển thị **tên sản phẩm** (1 column duy nhất).

**URL:** `http://localhost:5019/search?q=iphone`

Database chứa các bảng:
- `products`: Sản phẩm công khai (id, name, price, description, category)
- `users`: Thông tin người dùng (id, username, password, email, role)
- `flags`: Chứa flag bí mật (id, name, value)

## 🎓 Kiến Thức Cần Biết

### CONCAT vs CONCAT_WS

```sql
-- CONCAT: Nối các chuỗi đơn giản
SELECT CONCAT(username, ':', password) FROM users;
-- Output: admin:password123

-- CONCAT_WS: Nối với separator (With Separator)
SELECT CONCAT_WS(':', username, password, email) FROM users;
-- Output: admin:password123:admin@mail.com
```

**CONCAT_WS** tiện lợi hơn khi cần ghép nhiều trường với cùng 1 separator.

### Xác Định Số Columns

```sql
-- Dùng ORDER BY để tìm số columns
' ORDER BY 1-- ✅
' ORDER BY 2-- ❌ (Error = chỉ có 1 column)

-- Hoặc dùng UNION SELECT NULL
' UNION SELECT NULL-- ✅
' UNION SELECT NULL,NULL-- ❌
```

## 🚀 Hướng Dẫn Triển Khai

```bash
# Khởi động lab
docker-compose up -d

# Chờ MySQL khởi động (khoảng 30s)
docker-compose logs -f db

# Test ứng dụng
curl "http://localhost:5019/search?q=iphone"

# Dừng lab
docker-compose down
```

## 💡 Gợi Ý

1. **Bước 1:** Tìm điểm injection bằng single quote `'`
2. **Bước 2:** Xác định số columns với `ORDER BY`
3. **Bước 3:** Test UNION SELECT với NULL
4. **Bước 4:** Enumerate database, tables, columns
5. **Bước 5:** Dùng CONCAT_WS để ghép username:password
6. **Bước 6:** Extract flag từ bảng flags

## 📚 Tài Liệu Tham Khảo

- [Writeup chi tiết](solution/writeup.md)
- [Exploit script](solution/exploit.py)
- [MySQL CONCAT Documentation](https://dev.mysql.com/doc/refman/8.0/en/string-functions.html#function_concat)

## 🏁 Flag Format

`FLAG{...}`
