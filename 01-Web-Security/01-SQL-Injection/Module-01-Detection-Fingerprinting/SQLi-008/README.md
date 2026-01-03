# SQLi-008: Concatenation-based DBMS Fingerprinting

## 🎯 Mục Tiêu

Học cách xác định loại DBMS bằng **string concatenation syntax** - mỗi DBMS có cách nối chuỗi khác nhau.

## 📝 Mô Tả Kịch Bản

Một **Web Service** nhận XML input để truy vấn thông tin. Bạn cần xác định DBMS thông qua cách xử lý string concatenation.

**URL Target:** `http://localhost:5008/api/query`

## 🎓 Kiến Thức Cần Học

### String Concatenation Syntax

| DBMS | Syntax | Example |
|------|--------|---------|
| MySQL | `CONCAT()` or space | `CONCAT('a','b')` or `'a' 'b'` |
| MSSQL | `+` | `'a'+'b'` |
| Oracle | `\|\|` | `'a'\|\|'b'` |
| PostgreSQL | `\|\|` | `'a'\|\|'b'` |

### Differentiate Oracle vs PostgreSQL

- Oracle: Requires `FROM dual`
- PostgreSQL: `version()` function


## 🚀 Hướng Dẫn Chạy Lab

```bash
docker-compose up -d
# Truy cập: http://localhost:5008
docker-compose down -v
```

> ⚠️ Oracle XE cần ~2GB RAM và thời gian khởi động lâu (~120s)

## 💡 Hints

<details>
<summary>Hint 1: Test concatenation</summary>

```sql
-- Test || operator
' || 'test' || '

-- Test + operator (MSSQL)
' + 'test' + '

-- Test CONCAT (MySQL)
CONCAT('a','b')
```

</details>

<details>
<summary>Hint 2: Distinguish Oracle</summary>

Oracle requires `FROM dual`:
```sql
SELECT 'a'||'b' FROM dual  -- Oracle
SELECT 'a'||'b'            -- PostgreSQL
```

</details>

## 🏁 Flag

Identify Oracle via concatenation testing và extract flag.

**Flag Format:** `FLAG{...}`

## 📋 Checklist

- [ ] Test `||` concatenation
- [ ] Test `+` concatenation  
- [ ] Confirm Oracle (FROM dual test)
- [ ] Extract flag

## 🔗 Tài Liệu

- [Oracle Cheatsheet](../../../../_knowledge_base/Web/SQLi/10-dbms-oracle.md)
