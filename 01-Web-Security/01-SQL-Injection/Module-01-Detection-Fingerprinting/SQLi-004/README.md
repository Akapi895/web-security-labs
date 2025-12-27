# SQLi-004: Comment-based SQL Injection Detection

## 🎯 Mục Tiêu

Học cách phát hiện lỗ hổng SQL Injection bằng phương pháp **Comment Testing** - sử dụng các ký tự comment để xác định vulnerability.

## 📝 Mô Tả Kịch Bản

Bạn đang pentest một **REST API** của hệ thống quản lý sản phẩm. API trả về thông tin sản phẩm theo ID. Backend sử dụng Oracle Database.

**URL Target:** `http://localhost:5004/api/product?id=1`

## 🎓 Kiến Thức Cần Học

1. **`--` Comment**: Single-line comment (Oracle, MSSQL, PostgreSQL)
2. **`#` Comment**: MySQL specific comment
3. **`/* */` Comment**: Multi-line comment (all DBMS)
4. **Oracle Specifics**: Không support `#`, bắt buộc `FROM dual`

## 🚀 Hướng Dẫn Chạy Lab

```bash
# Khởi động lab
docker-compose up -d

# Đợi Oracle XE khởi động (~120s - Oracle cần nhiều thời gian)
# Sau đó truy cập: http://localhost:5004

# Dừng lab
docker-compose down -v
```

> ⚠️ **Note**: Oracle XE image khá lớn (~2GB) và cần nhiều RAM. Đảm bảo Docker có ít nhất 4GB RAM.

## 💡 Hints

<details>
<summary>Hint 1: Test với comment cơ bản</summary>

```
http://localhost:5004/api/product?id=1--
http://localhost:5004/api/product?id=1/*
```

Nếu request vẫn work bình thường → comment được accept

</details>

<details>
<summary>Hint 2: Thử comment "ăn" phần query</summary>

```
http://localhost:5004/api/product?id=1 OR 1=1--
```

Nếu trả về nhiều products hơn → SQLi confirmed!

</details>

<details>
<summary>Hint 3: Oracle Detection</summary>

Oracle có đặc điểm:
- **Không** support `#` comment
- Error pattern: `ORA-XXXXX`
- Phải dùng `FROM dual` cho simple queries

</details>

## 🏁 Flag

Sử dụng comment-based technique để confirm SQLi, sau đó exploit Oracle để lấy flag.

**Flag Format:** `FLAG{...}`

## 📋 Checklist

- [ ] Test với `--` comment
- [ ] Test với `/* */` comment  
- [ ] Confirm `#` không work (Oracle indicator)
- [ ] Xác định Oracle qua error pattern
- [ ] Extract flag thành công

## 🔗 Tài Liệu

- [Detection Techniques](../../../../_knowledge_base/Web/SQLi/01-detection.md)
- [Oracle Cheatsheet](../../../../_knowledge_base/Web/SQLi/10-dbms-oracle.md)
