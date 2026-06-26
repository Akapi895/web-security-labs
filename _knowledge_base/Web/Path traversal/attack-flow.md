# Attack Flow (if -> else)

## Nếu đây là lab PortSwigger / CTF, làm gì đầu tiên?
- Tìm endpoint có param giống file path (`file`, `filename`, `path`, `page`).
- Chụp baseline response.
- Bắn 4 payload đầu tiên: `../../../etc/passwd`, `/etc/passwd`, `....//....//etc/passwd`, `%252e%252e%252fetc%252fpasswd`.

## Flowchart text
```
START
-> Có endpoint đọc/include file?
-> IF No:
-> Fuzz param name + endpoint download/view/template
-> Quay lại START
-> IF Yes:
-> Gửi baseline request
-> Thử payload Linux (`../../../etc/passwd`)
-> IF có marker file:
-> CONFIRMED Path Traversal/LFI
-> Chuyển sang loot high-value file
-> IF không có marker:
-> Thử absolute path (`/etc/passwd`, `C:\\Windows\\win.ini`)
-> IF pass:
-> CONFIRMED
-> IF fail:
-> Thử bypass nested (`....//`)
-> IF fail:
-> Thử URL encode/double encode
-> IF fail:
-> Thử separator Windows (`..\\`) + reverse proxy mismatch (`..;/`)
-> IF fail:
-> Thử `curl --path-as-is` để tránh client normalize
-> IF vẫn fail:
-> Đánh giá false positive hoặc endpoint không phải file sink

CONFIRMED
-> Read reconnaissance files (`/etc/passwd`, `/proc/self/environ`, logs)
-> IF include executable context (PHP):
-> Thử wrapper payload (`php://filter`, `php://input`, `data://`, `zip://`)
-> IF command exec được:
-> RCE
-> ELSE:
-> Focus secret/token/config extraction + token replay

IF có write primitive qua path traversal
-> Drop webshell vào webroot
-> Trigger shell endpoint
-> RCE

END
- Kết quả tối thiểu cần có: 1 request + 1 response file-read rõ ràng + impact mô tả theo dữ liệu leak.
```