# SQLi-005: Error-based DBMS Fingerprinting

## 🎯 Mục Tiêu

Học cách xác định loại DBMS thông qua **error message patterns** - mỗi DBMS có format error message riêng biệt.

## 📝 Mô Tả Kịch Bản

Bạn đã phát hiện một **Shop search box** có lỗ hổng SQLi. Nhiệm vụ là xác định chính xác loại DBMS đang được sử dụng bằng cách phân tích error messages.

**URL Target:** `http://localhost:5005/search?q=test`

## 🎓 Kiến Thức Cần Học

### Error Message Patterns

| DBMS | Error Pattern |
|------|---------------|
| MySQL | `You have an error in your SQL syntax...` |
| MSSQL | `Unclosed quotation mark...`, `Incorrect syntax near...` |
| Oracle | `ORA-XXXXX: ...` |
| PostgreSQL | `ERROR: syntax error at or near...` |
| SQLite | `SQLITE_ERROR: ...`, `near "...": syntax error` |

## 🚀 Hướng Dẫn Chạy Lab

```bash
docker-compose up -d
# Truy cập: http://localhost:5005
docker-compose down -v
```

## 💡 Hints

<details>
<summary>Hint 1: Trigger error</summary>

Inject một invalid syntax để trigger error:
```
http://localhost:5005/search?q='
```

</details>

<details>
<summary>Hint 2: Phân tích error</summary>

Tìm các pattern đặc trưng:
- "SQL syntax" → MySQL
- "quotation mark" → MSSQL
- "ORA-" → Oracle
- "syntax error at or near" → PostgreSQL

</details>

<details>
<summary>Hint 3: Confirm với version query</summary>

Sau khi xác định DBMS, dùng version query phù hợp:
```sql
-- MySQL
' UNION SELECT @@version--

-- PostgreSQL  
' UNION SELECT version()--
```

</details>

## 🏁 Flag

Xác định DBMS và sử dụng error-based extraction để lấy flag.

**Flag Format:** `FLAG{...}`

## 📋 Checklist

- [ ] Trigger SQL error bằng quote
- [ ] Phân tích error message pattern
- [ ] Xác định chính xác DBMS
- [ ] Sử dụng DBMS-specific technique để extract flag

## 🔗 Tài Liệu

- [Detection Techniques](../../../../_knowledge_base/Web/SQLi/01-detection.md)
- [Error-based SQLi](../../../../_knowledge_base/Web/SQLi/02-error-based.md)
