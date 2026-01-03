# Module 3: Union-based SQL Injection

> **Mục tiêu**: Sử dụng UNION SELECT để ghép kết quả và lấy dữ liệu
>
> **Lưu ý:** Module này tập trung vào **advanced techniques** vì bạn đã nắm được basic union concepts từ Module 1 & 2.

## 📋 Danh Sách Labs

| Lab ID   | Sub-Topic             | DBMS       | Scenario                            | Learning Objective                                    | Complexity      |
| -------- | --------------------- | ---------- | ----------------------------------- | ----------------------------------------------------- | --------------- |
| SQLi-019 | Union - Single Column | MySQL      | Search results (1 column displayed) | CONCAT/CONCAT_WS để ghép nhiều giá trị trong 1 column | ⭐⭐ Trung bình |
| SQLi-020 | Union - Single Column | Oracle     | Invoice lookup                      | Concatenation với `\|\|` operator, FROM dual          | ⭐⭐ Trung bình |
| SQLi-021 | Union - Multi Row     | MySQL      | Comments section                    | GROUP_CONCAT() để aggregate nhiều rows                | ⭐⭐ Trung bình |
| SQLi-022 | Union - Multi Row     | PostgreSQL | User listing                        | STRING_AGG() aggregation technique                    | ⭐⭐⭐ Khó      |

## 🎓 Kiến Thức Cần Biết

### Union SELECT Cơ Bản

```sql
-- UNION kết hợp kết quả của 2 query
SELECT column1, column2 FROM table1
UNION
SELECT column1, column2 FROM table2
```

**Yêu cầu:**
- Số lượng columns phải giống nhau
- Kiểu dữ liệu phải tương thích

### Kỹ Thuật Single Column

Khi chỉ có 1 column được hiển thị, cần ghép nhiều giá trị:

| DBMS       | Kỹ thuật                           | Ví dụ                                      |
| ---------- | ---------------------------------- | ------------------------------------------ |
| MySQL      | `CONCAT()` / `CONCAT_WS()`         | `CONCAT_WS(':',username,password)`         |
| Oracle     | `\|\|` operator                    | `username\|\|':'\\|\|password`             |
| PostgreSQL | `\|\|` operator                    | `username\|\|':'\\|\|password`             |
| MSSQL      | `+` operator                       | `username+':'+password`                    |

### Kỹ Thuật Multi Row

Khi cần aggregate nhiều rows thành 1 string:

| DBMS       | Kỹ thuật                                    | Ví dụ                                                |
| ---------- | ------------------------------------------- | ---------------------------------------------------- |
| MySQL      | `GROUP_CONCAT()`                            | `GROUP_CONCAT(username SEPARATOR ',')`               |
| Oracle     | `LISTAGG()`                                 | `LISTAGG(username,',') WITHIN GROUP (ORDER BY ...)`  |
| PostgreSQL | `STRING_AGG()`                              | `STRING_AGG(username,',')`                           |
| MSSQL      | `STRING_AGG()` (2017+) hoặc `FOR XML PATH` | `STRING_AGG(username,',')`                           |

## 🚀 Cách Chạy Lab

```bash
# Chuyển vào thư mục lab
cd SQLi-019

# Khởi động containers
docker-compose up -d

# Kiểm tra logs
docker-compose logs -f

# Truy cập ứng dụng
# http://localhost:5019

# Dừng lab
docker-compose down
```

## 📚 Tài Liệu Tham Khảo

- [OWASP SQL Injection](https://owasp.org/www-community/attacks/SQL_Injection)
- [PortSwigger - UNION attacks](https://portswigger.net/web-security/sql-injection/union-attacks)
- [PayloadsAllTheThings - SQLi](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/SQL%20Injection)
