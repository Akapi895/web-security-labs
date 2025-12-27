# SQLi-006: Version Query Fingerprinting

## 🎯 Mục Tiêu

Học cách xác định loại DBMS bằng cách sử dụng **version queries** đặc thù của từng database.

## 📝 Mô Tả Kịch Bản

Một **Login form** có lỗ hổng SQLi với verbose error messages. Nhiệm vụ là sử dụng version queries để fingerprint DBMS.

**URL Target:** `http://localhost:5006/login`

## 🎓 Kiến Thức Cần Học

### Version Queries

| DBMS | Query |
|------|-------|
| MySQL | `SELECT @@version` |
| MSSQL | `SELECT @@version` |
| PostgreSQL | `SELECT version()` |
| Oracle | `SELECT banner FROM v$version WHERE ROWNUM=1` |
| SQLite | `SELECT sqlite_version()` |

## 🚀 Hướng Dẫn Chạy Lab

```bash
docker-compose up -d
# Truy cập: http://localhost:5006
docker-compose down -v
```

## 💡 Hints

<details>
<summary>Hint 1: Test version queries</summary>

Thử các version queries trong error-based hoặc UNION:
```sql
' UNION SELECT version(),NULL--
' UNION SELECT @@version,NULL--
```

</details>

<details>
<summary>Hint 2: PostgreSQL indicators</summary>

- `version()` function works
- Error pattern: `ERROR: syntax error at or near`
- Uses `||` for string concatenation

</details>

## 🏁 Flag

Xác định PostgreSQL version và extract flag.

**Flag Format:** `FLAG{...}`

## 📋 Checklist

- [ ] Test various version queries
- [ ] Identify which one works
- [ ] Confirm PostgreSQL
- [ ] Extract flag

## 🔗 Tài Liệu

- [PostgreSQL Cheatsheet](../../../../_knowledge_base/Web/SQLi/11-dbms-postgresql.md)
