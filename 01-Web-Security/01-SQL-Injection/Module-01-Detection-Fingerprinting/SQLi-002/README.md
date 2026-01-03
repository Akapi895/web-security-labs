# SQLi-002: Logic-based SQL Injection Detection

## 🎯 Mục Tiêu

Học cách phát hiện lỗ hổng SQL Injection bằng phương pháp **Logic-based Testing** - sử dụng các điều kiện TRUE/FALSE để xác định vulnerability.

## 📝 Mô Tả Kịch Bản

Bạn đang pentest một website **News Portal** có chức năng lọc bài viết theo category. Ứng dụng sử dụng PostgreSQL làm database.

**URL Target:** `http://localhost:5002/articles?category=technology`

## 🎓 Kiến Thức Cần Học

1. **OR 1=1**: Điều kiện luôn TRUE - bypass authentication hoặc lấy tất cả records
2. **AND 1=2**: Điều kiện luôn FALSE - không có kết quả trả về
3. **Response Analysis**: So sánh response giữa TRUE và FALSE conditions

## 🚀 Hướng Dẫn Chạy Lab

```bash
# Khởi động lab
docker-compose up -d

# Đợi PostgreSQL khởi động (~20s)
# Sau đó truy cập: http://localhost:5002

# Dừng lab
docker-compose down -v
```

## 💡 Hints

<details>
<summary>Hint 1: Test TRUE condition</summary>

Thử thêm `' OR '1'='1` vào parameter:
```
http://localhost:5002/articles?category=technology' OR '1'='1
```
Bạn sẽ thấy **tất cả** bài viết (vì condition luôn TRUE)

</details>

<details>
<summary>Hint 2: Test FALSE condition</summary>

Thử với FALSE condition:
```
http://localhost:5002/articles?category=technology' AND '1'='2
```
Bạn sẽ thấy **không có** kết quả (vì condition luôn FALSE)

</details>

<details>
<summary>Hint 3: Xác nhận vulnerability</summary>

So sánh 2 responses:
- `' OR '1'='1` → Nhiều kết quả
- `' AND '1'='2` → Không có kết quả

Nếu có sự khác biệt rõ ràng → Confirmed SQLi!

</details>

## 🏁 Flag

Flag được lưu trong bảng `secrets` với điều kiện đặc biệt.
Sử dụng logic-based detection để xác nhận vulnerability, sau đó khai thác để lấy flag.

**Flag Format:** `FLAG{...}`

## 📋 Checklist

- [ ] Test với `' OR '1'='1` - quan sát số lượng kết quả tăng
- [ ] Test với `' AND '1'='2` - quan sát không có kết quả
- [ ] Xác định đây là PostgreSQL (dựa vào behavior)
- [ ] Extract flag thành công

## 🔗 Tài Liệu

- [Detection Techniques](../../../../_knowledge_base/Web/SQLi/01-detection.md)
- [PostgreSQL Cheatsheet](../../../../_knowledge_base/Web/SQLi/11-dbms-postgresql.md)
