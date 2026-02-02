# CMDi-002: Pipe Operator Injection

## 🎯 Mục Tiêu

Học cách khai thác lỗ hổng Command Injection sử dụng **pipe operator (`|`)** để redirect output và chain commands trong trường hợp semicolon không hoạt động.

## 📝 Mô Tả Kịch Bản

Bạn đang pentest một **Document Preview System** của một công ty publishing. Hệ thống cho phép người dùng xem nội dung preview của các tài liệu bằng cách nhập tên file. Backend sử dụng lệnh `cat` để đọc và hiển thị nội dung file.

**URL Target:** `http://localhost:5102/preview`

## 🔬 Bối Cảnh Kỹ Thuật

Ứng dụng có implement một số basic filtering để ngăn chặn command injection. Tuy nhiên, việc filtering không đầy đủ tạo ra lỗ hổng.

**Câu hỏi cần trả lời:**
- Filter đang chặn những ký tự nào?
- Có separator nào không bị filter không?
- Pipe operator hoạt động khác gì so với semicolon?

## 🎓 Kiến Thức Cần Nắm

Trước khi bắt đầu, hãy hiểu sự khác biệt giữa các operators:

| Operator | Behavior | Example |
|----------|----------|---------|
| `;` | Sequential: chạy lần lượt | `cmd1; cmd2` |
| `\|` | Pipe: output cmd1 → input cmd2 | `cmd1 \| cmd2` |
| `\|\|` | OR: cmd2 chạy nếu cmd1 fail | `cmd1 \|\| cmd2` |
| `&&` | AND: cmd2 chạy nếu cmd1 success | `cmd1 && cmd2` |

**Tham khảo Knowledge Base:**
- [Command Chaining Operators](../../../../_knowledge_base/Web/Command%20Injection/02-exploitation.md#command-chaining-operators)
- [Detection Methodology](../../../../_knowledge_base/Web/Command%20Injection/01-detection.md)

## 🚀 Hướng Dẫn Chạy Lab

```bash
# Khởi động lab
cd 01-Web-Security/02-Command-Injection/Module-01-In-band-Injection/CMDi-002
docker-compose up -d

# Truy cập: http://localhost:5102
# Dừng lab
docker-compose down
```

## 💡 Hints

<details>
<summary>Hint 1: Quan sát behavior khi dùng semicolon</summary>

Thử inject với semicolon như lab trước:
```
test.txt; id
```
Kết quả như thế nào? Có error message hay response thay đổi không?

</details>

<details>
<summary>Hint 2: Thử các separator khác</summary>

Nếu semicolon bị filter, điều đó không có nghĩa là tất cả separators đều bị chặn.
Thử từng separator một:
- `|`
- `||`
- `&&`
- `&`

</details>

<details>
<summary>Hint 3: Pipe operator behavior</summary>

Pipe operator (`|`) có behavior đặc biệt:
- Command bên trái pipe có thể fail
- Command bên phải vẫn được execute
- Không cần command bên trái thành công

</details>

<details>
<summary>Hint 4: Tối ưu payload</summary>

Với pipe, bạn có thể bỏ qua file name hoàn toàn:
```
| command
```
Điều này force `cat` fail (không có file) nhưng command của bạn vẫn chạy.

</details>

## 🏁 Flag

Tìm và đọc file flag trong hệ thống.

**Flag Format:** `FLAG{...}`

## 📋 Checklist

- [ ] Xác định được filter đang chặn ký tự nào
- [ ] Tìm được separator bypass filter
- [ ] Hiểu được sự khác biệt giữa pipe và semicolon
- [ ] Khai thác thành công và đọc flag

## 🔗 Tài Liệu Tham Khảo

- [Command Chaining Operators](../../../../_knowledge_base/Web/Command%20Injection/02-exploitation.md#command-chaining-operators)
- [Filter Bypass Techniques](../../../../_knowledge_base/Web/Command%20Injection/04-filter-bypass.md)
