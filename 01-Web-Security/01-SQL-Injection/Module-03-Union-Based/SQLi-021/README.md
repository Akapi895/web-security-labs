# SQLi-021: MySQL Union-based - Multi Row (GROUP_CONCAT)

## 🎯 Mục Tiêu

Khai thác SQL Injection trên MySQL bằng kỹ thuật **Union-based** với `GROUP_CONCAT()` để aggregate nhiều rows thành 1 string khi output hiển thị nhiều dòng.

## 📝 Mô Tả

Ứng dụng Blog có chức năng xem comments. Response hiển thị **tất cả comments** của một bài post (multiple rows).

**URL:** `http://localhost:5021/post?id=1`

Database chứa các bảng:
- `posts`: Bài viết blog (id, title, content, author)
- `comments`: Bình luận (id, post_id, username, comment_text)
- `admin_users`: Tài khoản admin (id, username, password, email, role, api_key)
- `secrets`: Chứa flag bí mật

## 🎓 Kiến Thức Cần Biết

### GROUP_CONCAT

```sql
-- Aggregate nhiều rows thành 1 string
SELECT GROUP_CONCAT(username) FROM users;
-- Output: admin,john,jane,bob

-- Với separator custom
SELECT GROUP_CONCAT(username SEPARATOR ' | ') FROM users;
-- Output: admin | john | jane | bob

-- Với DISTINCT để loại bỏ duplicate
SELECT GROUP_CONCAT(DISTINCT role) FROM users;
```

### Kết hợp GROUP_CONCAT với CONCAT_WS

```sql
-- Ghép nhiều columns VÀ nhiều rows
SELECT GROUP_CONCAT(CONCAT_WS(':',username,password) SEPARATOR '<br>') FROM users;
-- Output: admin:pass1<br>john:pass2<br>jane:pass3
```

## 🚀 Hướng Dẫn Triển Khai

```bash
# Khởi động lab
docker-compose up -d

# Chờ MySQL khởi động (khoảng 30s)
docker-compose logs -f db

# Test ứng dụng
curl "http://localhost:5021/post?id=1"

# Dừng lab
docker-compose down
```

## 💡 Gợi Ý

1. **Bước 1:** Tìm điểm injection trong parameter `id`
2. **Bước 2:** Xác định MySQL qua error messages
3. **Bước 3:** Dùng `ORDER BY` để tìm số columns
4. **Bước 4:** Enumerate database với UNION SELECT
5. **Bước 5:** Dùng GROUP_CONCAT để lấy tất cả users trong 1 query
6. **Bước 6:** Extract flag và API keys từ admin_users

## 📚 Tài Liệu Tham Khảo

- [Writeup chi tiết](solution/writeup.md)
- [Exploit script](solution/exploit.py)
- [MySQL GROUP_CONCAT](https://dev.mysql.com/doc/refman/8.0/en/aggregate-functions.html#function_group-concat)

## 🏁 Flag Format

`FLAG{...}`
