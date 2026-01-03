# SQLi-030: MSSQL Time-based - WAITFOR DELAY

## 🎯 Mục Tiêu

Khai thác Time-based Blind SQLi trên MSSQL dùng `WAITFOR DELAY`.

## 📝 Mô Tả

Email validation endpoint: `http://localhost:5030/validate?email=test@test.com`

## 🎓 Technique

```sql
-- MSSQL WAITFOR DELAY
'; IF (condition) WAITFOR DELAY '0:0:3'--
```

## 🏁 Flag: `FLAG{...}`
