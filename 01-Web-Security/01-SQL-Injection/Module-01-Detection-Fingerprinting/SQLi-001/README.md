# SQLi-001: Quote-based SQL Injection Detection

## 🎯 Mục Tiêu

Học cách phát hiện lỗ hổng SQL Injection bằng phương pháp **Quote-based Testing** - kỹ thuật cơ bản nhất để xác định một tham số có vulnerable hay không.

## 📝 Mô Tả Kịch Bản

Bạn đang pentest một website **E-Commerce** có chức năng tìm kiếm sản phẩm. Chức năng search nhận input từ người dùng và truy vấn database để hiển thị kết quả.

**URL Target:** `http://localhost:5001/search?q=laptop`

## 🎓 Kiến Thức Cần Học

1. **Single Quote (`'`)**: Dấu quote đơn là ký tự phổ biến nhất để test SQLi
2. **Double Quote (`"`)**: Một số hệ thống dùng double quote cho string
3. **Backtick (`` ` ``)**: MySQL sử dụng backtick cho identifiers
4. **Kết hợp với parenthesis**: `')`, `")`, `'))` để đóng các subqueries

## 🚀 Hướng Dẫn Chạy Lab

```bash
# Khởi động lab
docker-compose up -d

# Đợi MySQL khởi động (khoảng 30s)
# Sau đó truy cập: http://localhost:5001

# Dừng lab
docker-compose down -v
```

## 💡 Hints

<details>
<summary>Hint 1: Bắt đầu từ đâu?</summary>

Thử thêm dấu `'` vào sau từ khóa search:
```
http://localhost:5001/search?q=laptop'
```

</details>

<details>
<summary>Hint 2: Quan sát response</summary>

Nếu vulnerable, bạn sẽ thấy:
- Error message từ MySQL
- Response khác biệt (blank page, 500 error, etc.)

</details>

<details>
<summary>Hint 3: Xác nhận vulnerability</summary>

Sau khi phát hiện error, thử "fix" query bằng cách thêm comment:
```
http://localhost:5001/search?q=laptop'--
http://localhost:5001/search?q=laptop'#
```

</details>

## 🏁 Flag

Sau khi hoàn thành detection, tìm flag bằng cách:
1. Xác nhận SQLi vulnerability tồn tại
2. Extract flag từ bảng `flags` trong database

**Flag Format:** `FLAG{...}`

## 📋 Checklist

- [ ] Phát hiện error khi inject `'`
- [ ] Xác định đây là MySQL (dựa vào error message)
- [ ] Bypass error bằng comment character
- [ ] Extract flag thành công

## 🔗 Tài Liệu

- [Detection Techniques](../../../../_knowledge_base/Web/SQLi/01-detection.md)
- [MySQL Cheatsheet](../../../../_knowledge_base/Web/SQLi/08-dbms-mysql.md)
