# CMDi-001: Basic Semicolon Separator Injection

## 🎯 Mục Tiêu

Học cách phát hiện và khai thác lỗ hổng **Command Injection** cơ bản nhất - sử dụng semicolon (`;`) làm command separator để chạy lệnh tùy ý trên hệ thống.

## 📝 Mô Tả Kịch Bản

Bạn đang pentest một **Network Diagnostic Tool** nội bộ của công ty. Ứng dụng cho phép nhân viên IT kiểm tra kết nối mạng bằng cách ping đến các địa chỉ IP. Chức năng này nhận input từ người dùng và thực thi lệnh ping trên server.

**URL Target:** `http://localhost:5101/ping`

## 🔬 Bối Cảnh Kỹ Thuật

Ứng dụng web chạy trên Linux server với PHP backend. Khi người dùng submit một IP address, server sẽ thực thi lệnh `ping` với input đó và trả về kết quả.

**Câu hỏi cần trả lời:**
- User input được đưa vào command như thế nào?
- Có thể chèn thêm command khác không?
- Server đang chạy với quyền user nào?

## 🎓 Kiến Thức Cần Nắm

Trước khi bắt đầu, hãy đảm bảo bạn hiểu:

1. **Command Separators**: Các ký tự đặc biệt mà shell sử dụng để phân tách commands
2. **Shell Execution**: Cách ứng dụng web gọi OS commands (system(), exec(), etc.)
3. **In-band vs Blind**: Sự khác biệt giữa việc thấy output trực tiếp và không thấy

**Tham khảo Knowledge Base:**
- [Command Injection Overview](../../../../_knowledge_base/Web/Command%20Injection/00-overview.md)
- [Detection Techniques](../../../../_knowledge_base/Web/Command%20Injection/01-detection.md)

## 🚀 Hướng Dẫn Chạy Lab

```bash
# Khởi động lab
cd 01-Web-Security/02-Command-Injection/Module-01-In-band-Injection/CMDi-001
docker-compose up -d

# Truy cập: http://localhost:5101
# Dừng lab
docker-compose down
```

## 💡 Hints

<details>
<summary>Hint 1: Bắt đầu từ đâu?</summary>

Thử ping một IP address hợp lệ trước để hiểu behavior bình thường của ứng dụng:
```
127.0.0.1
```
Quan sát output - bạn thấy gì?

</details>

<details>
<summary>Hint 2: Shell behavior</summary>

Trong Linux shell, bạn có thể chạy nhiều commands liên tiếp trên cùng một dòng. Có những ký tự đặc biệt nào cho phép điều này?

Thử nghĩ về cách bạn thường chạy nhiều lệnh trong terminal.

</details>

<details>
<summary>Hint 3: Kiểm tra giả thuyết</summary>

Nếu giả thuyết của bạn đúng, bạn sẽ thấy output của command thứ hai xuất hiện trong response. Thử một command đơn giản trước để xác nhận:
- `id` - hiển thị user info
- `whoami` - hiển thị username

</details>

<details>
<summary>Hint 4: Exploitation workflow</summary>

Sau khi confirm được command execution:
1. Xác định user đang chạy web server
2. Khám phá file system
3. Tìm file flag

</details>

## 🏁 Flag

Sau khi khai thác thành công, tìm và đọc nội dung file flag trong hệ thống.

**Flag Format:** `FLAG{...}`

## 📋 Checklist

- [ ] Hiểu được behavior bình thường của chức năng ping
- [ ] Phát hiện được injection point
- [ ] Xác nhận command execution thành công
- [ ] Xác định user context (quyền của web server)
- [ ] Tìm và đọc được flag

## 🔗 Tài Liệu Tham Khảo

- [Shell Metacharacters](../../../../_knowledge_base/Web/Command%20Injection/00-overview.md#shell-metacharacters-quick-reference)
- [Detection Methodology](../../../../_knowledge_base/Web/Command%20Injection/01-detection.md#detection-methodology)
- [Exploitation Techniques](../../../../_knowledge_base/Web/Command%20Injection/02-exploitation.md)
