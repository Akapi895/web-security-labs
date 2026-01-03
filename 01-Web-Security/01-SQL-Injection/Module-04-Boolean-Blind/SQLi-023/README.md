# SQLi-023: PostgreSQL Boolean Blind - SUBSTRING Extraction

## 🎯 Mục Tiêu

Khai thác Boolean Blind SQL Injection trên PostgreSQL bằng kỹ thuật **SUBSTRING** để trích xuất data từng ký tự.

## 📝 Mô Tả

Ứng dụng Username Validation kiểm tra xem username có tồn tại hay không:

**URL:** `http://localhost:5023/check?username=john_doe`

- ✅ Username exists → "Username is taken"
- ❌ Username not exists → "Username is available"

Không có output trực tiếp, chỉ có TRUE/FALSE response!

## 🎓 Kiến Thức Cần Biết

### PostgreSQL SUBSTRING

```sql
-- Syntax: SUBSTRING(string FROM start FOR length)
SUBSTRING('hello' FROM 1 FOR 1) → 'h'
SUBSTRING('hello' FROM 2 FOR 1) → 'e'
```

### Character Extraction

```sql
-- Kiểm tra ký tự đầu tiên = 's'
' AND SUBSTRING(username FROM 1 FOR 1)='s'--

-- Kiểm tra với ASCII (binary search)
' AND ASCII(SUBSTRING(username FROM 1 FOR 1))>109--
```

## 🚀 Hướng Dẫn

```bash
docker-compose up -d
curl "http://localhost:5023/check?username=john_doe"
docker-compose down
```

## 💡 Gợi Ý

1. Tìm injection point với `' AND '1'='1` vs `' AND '1'='2`
2. Dùng subquery để truy cập bảng `admin_secrets`
3. Extract từng ký tự password với SUBSTRING
4. Lấy flag từ bảng `flags`

## 🏁 Flag Format

`FLAG{...}`
