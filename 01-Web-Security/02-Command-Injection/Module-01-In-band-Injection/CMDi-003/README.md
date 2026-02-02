# CMDi-003: Command Substitution Injection

## 🎯 Mục Tiêu

Học cách khai thác Command Injection thông qua **Command Substitution** (`$(...)` hoặc `` `...` ``) - kỹ thuật lồng command bên trong một command khác.

## 📝 Mô Tả Kịch Bản

Bạn đang pentest một **DNS Lookup Service** nội bộ của công ty hosting. Ứng dụng cho phép nhân viên tra cứu DNS records bằng cách nhập hostname. Kết quả nslookup được trả về trong response.

**URL Target:** `http://localhost:5103/lookup`

## 🔬 Bối Cảnh Kỹ Thuật

Ứng dụng đã implement filtering khá chặt chẽ, chặn hầu hết các command separators phổ biến. Tuy nhiên, developer quên rằng shell có cơ chế **command substitution** cho phép lồng commands.

**Câu hỏi cần trả lời:**
- Những separators nào đã bị chặn?
- Command substitution hoạt động như thế nào?
- Làm sao để "leak" output của injected command?

## 🎓 Kiến Thức Cần Nắm

Trước khi bắt đầu, hãy hiểu về Command Substitution:

**Concept:**
```bash
# $(command) hoặc `command` sẽ được thay thế bằng output của command
echo "Hello $(whoami)"    # → "Hello www-data"
echo "Hello `whoami`"     # → "Hello www-data" (legacy syntax)
```

**Trong context của injection:**
- Output của injected command trở thành **argument** của original command
- Không cần separator để thực thi command

**Tham khảo Knowledge Base:**
- [Command Substitution](../../../../_knowledge_base/Web/Command%20Injection/02-exploitation.md#command-substitution)
- [Detection Techniques](../../../../_knowledge_base/Web/Command%20Injection/01-detection.md)

## 🚀 Hướng Dẫn Chạy Lab

```bash
# Khởi động lab
cd 01-Web-Security/02-Command-Injection/Module-01-In-band-Injection/CMDi-003
docker-compose up -d

# Truy cập: http://localhost:5103
# Dừng lab
docker-compose down
```

## 💡 Hints

<details>
<summary>Hint 1: Test các separators đã học</summary>

Thử các payloads từ lab trước:
```
google.com; id
google.com | id
```
Quan sát response - có bị chặn không?

</details>

<details>
<summary>Hint 2: Phương pháp khác để thực thi command</summary>

Trong shell, có cách để thực thi command mà **không cần separator**. 
Command substitution cho phép bạn lồng command vào bên trong input.

Syntax:
- `$(command)` - Modern syntax
- `` `command` `` - Legacy syntax (backticks)

</details>

<details>
<summary>Hint 3: Output sẽ hiển thị ở đâu?</summary>

Với command substitution, output trở thành một phần của original command:
```
nslookup $(whoami)
→ nslookup www-data
```

Output có thể "leak" qua:
- Error message của nslookup
- Nếu output là valid hostname → có thể thấy trong DNS response

</details>

<details>
<summary>Hint 4: Tận dụng error message</summary>

Nếu injected command output không phải valid hostname, nslookup sẽ fail và có thể hiển thị error message chứa output của bạn.

Thử:
```
$(whoami).google.com
```
Điều gì xảy ra?

</details>

## 🏁 Flag

Sử dụng command substitution để đọc flag file và tìm cách leak nội dung.

**Flag Format:** `FLAG{...}`

## 📋 Checklist

- [ ] Xác định các separators bị chặn
- [ ] Hiểu được command substitution hoạt động như thế nào
- [ ] Tìm cách inject command mà không dùng separators
- [ ] Leak được output của injected command
- [ ] Đọc được flag

## 🔗 Tài Liệu Tham Khảo

- [Command Substitution](../../../../_knowledge_base/Web/Command%20Injection/02-exploitation.md#command-substitution)
- [Exploitation Techniques](../../../../_knowledge_base/Web/Command%20Injection/02-exploitation.md)
- [Detection Methodology](../../../../_knowledge_base/Web/Command%20Injection/01-detection.md)
