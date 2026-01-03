# SQLi-020: Oracle Union-based - Single Column (|| Operator)

## 🎯 Mục Tiêu

Khai thác SQL Injection trên Oracle Database bằng kỹ thuật **Union-based** với `||` operator (pipe concatenation) để ghép nhiều giá trị trong 1 column.

## 📝 Mô Tả

Ứng dụng Invoice Lookup cho phép tra cứu hóa đơn. Kết quả chỉ hiển thị **invoice number** (1 column).

**URL:** `http://localhost:5020/invoice?id=1`

Database chứa các bảng:
- `invoices`: Hóa đơn công khai (id, invoice_number, amount, customer, status)
- `customers`: Thông tin khách hàng
- `admin_users`: Tài khoản admin (id, username, password, role)
- `secrets`: Chứa flag bí mật

## 🎓 Kiến Thức Cần Biết

### Oracle || Operator

```sql
-- Oracle dùng || để nối chuỗi (không phải + như MSSQL)
SELECT username || ':' || password FROM admin_users;
-- Output: admin:password123
```

### FROM dual

Oracle yêu cầu mệnh đề FROM trong mọi SELECT:

```sql
-- ❌ Lỗi trên Oracle
SELECT 'test'

-- ✅ Đúng trên Oracle
SELECT 'test' FROM dual
```

### LISTAGG cho Multi-row

```sql
-- Aggregate nhiều rows thành 1 string
SELECT LISTAGG(table_name, ',') WITHIN GROUP (ORDER BY table_name)
FROM user_tables;
```

## 🚀 Hướng Dẫn Triển Khai

```bash
# Khởi động lab (Oracle cần 2-3 phút để start)
docker-compose up -d

# Monitor initialization
docker-compose logs -f db

# Test ứng dụng
curl "http://localhost:5020/invoice?id=1"

# Dừng lab
docker-compose down
```

## 💡 Gợi Ý

1. **Bước 1:** Tìm điểm injection với single quote
2. **Bước 2:** Xác định Oracle qua error code `ORA-xxxxx`
3. **Bước 3:** Dùng `ORDER BY` và `UNION SELECT NULL FROM dual`
4. **Bước 4:** Enumerate `user_tables` và `all_tab_columns`
5. **Bước 5:** Dùng `||` operator để ghép username:password
6. **Bước 6:** Extract flag từ bảng secrets

## 📚 Tài Liệu Tham Khảo

- [Writeup chi tiết](solution/writeup.md)
- [Exploit script](solution/exploit.py)
- [Oracle String Functions](https://docs.oracle.com/en/database/oracle/oracle-database/19/sqlrf/Concatenation-Operator.html)

## 🏁 Flag Format

`FLAG{...}`
