# SQLi-003: Arithmetic-based SQL Injection Detection

## 🎯 Mục Tiêu

Học cách phát hiện lỗ hổng SQL Injection bằng phương pháp **Arithmetic Testing** - sử dụng các phép toán để detect vulnerability thông qua response behavior.

## 📝 Mô Tả Kịch Bản

Bạn đang pentest một ứng dụng **Corporate Directory** có chức năng xem profile nhân viên theo ID. Ứng dụng sử dụng MSSQL làm database.

**URL Target:** `http://localhost:5003/profile?id=1`

## 🎓 Kiến Thức Cần Học

1. **Division by 1 (`/1`)**: Phép chia hợp lệ, không thay đổi kết quả
2. **Division by 0 (`/0`)**: Gây ra lỗi hoặc response khác biệt
3. **Multiplication (`*1`)**: Phép nhân hợp lệ
4. **Subtraction (`-0`)**: Phép trừ hợp lệ

## 🚀 Hướng Dẫn Chạy Lab

```bash
# Khởi động lab
docker-compose up -d

# Đợi MSSQL khởi động (~60s - MSSQL cần thời gian lâu hơn)
# Sau đó truy cập: http://localhost:5003

# Dừng lab
docker-compose down -v
```

## 💡 Hints

<details>
<summary>Hint 1: Arithmetic Test cơ bản</summary>

So sánh các requests:
```
http://localhost:5003/profile?id=1/1   (hợp lệ - trả về profile)
http://localhost:5003/profile?id=1/0   (lỗi hoặc response khác)
```

</details>

<details>
<summary>Hint 2: Các phép tính khác</summary>

```
http://localhost:5003/profile?id=2-1   (tương đương id=1)
http://localhost:5003/profile?id=1*1   (tương đương id=1)
```

Nếu các phép tính được thực thi → SQLi confirmed!

</details>

<details>
<summary>Hint 3: Xác định MSSQL</summary>

MSSQL có một số đặc điểm:
- Error message chứa keywords như `MSSQL`, `SQL Server`
- `@@version` và `@@SERVERNAME`
- Comments: `--` (không cần space như MySQL)

</details>

## 🏁 Flag

Sau khi xác định vulnerability, sử dụng kỹ thuật phù hợp với MSSQL để extract flag.

**Flag Format:** `FLAG{...}`

## 📋 Checklist

- [ ] Test với `1/1` - xác nhận response bình thường
- [ ] Test với `1/0` - quan sát error hoặc response khác
- [ ] Test với `2-1` - xác nhận arithmetic được execute
- [ ] Xác định MSSQL qua error messages hoặc behavior
- [ ] Extract flag thành công

## 🔗 Tài Liệu

- [Detection Techniques](../../../../_knowledge_base/Web/SQLi/01-detection.md)
- [MSSQL Cheatsheet](../../../../_knowledge_base/Web/SQLi/09-dbms-mssql.md)
