# SQLi-024: Oracle Boolean Blind - SUBSTR Extraction

## 🎯 Mục Tiêu

Khai thác Boolean Blind SQLi trên Oracle với kỹ thuật **SUBSTR()** và **ROWNUM** pagination.

## 📝 Mô Tả

Ứng dụng Session Validator kiểm tra session token có hợp lệ không:

**URL:** `http://localhost:5024/validate?token=sess_valid_abc123`

- ✅ Valid session → "Session is valid"
- ❌ Invalid/Expired → "Session is invalid"

## 🎓 Kiến Thức

### Oracle SUBSTR

```sql
SUBSTR(string, position, length)
SUBSTR('hello', 1, 1) → 'h'
```

### ROWNUM Pagination

```sql
-- Lấy row đầu tiên
SELECT password FROM admin_creds WHERE ROWNUM = 1
```

## 🚀 Hướng Dẫn

```bash
docker-compose up -d
# Đợi 2-3 phút cho Oracle khởi động
curl "http://localhost:5024/validate?token=sess_valid_abc123"
```

## 🏁 Flag Format

`FLAG{...}`
