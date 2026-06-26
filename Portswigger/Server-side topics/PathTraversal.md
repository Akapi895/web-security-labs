# Path Traversal / LFI - Báo Cáo Tổng Hợp

## 1. Path Traversal / LFI là gì và bản chất kỹ thuật

Path Traversal (Directory Traversal) là lỗi cho phép attacker điều khiển đường dẫn file để thoát khỏi thư mục dự kiến của ứng dụng.

LFI (Local File Inclusion) là biến thể khi input đi vào cơ chế include/read file local.

Nếu tóm gọn trong 1 câu:

- Ứng dụng kỳ vọng input là tên file hợp lệ.
- Attacker biến input thành chỉ dẫn truy cập file ngoài phạm vi cho phép.

Bản chất kỹ thuật nằm ở việc mất ranh giới giữa:

- dữ liệu người dùng
- và đường dẫn hệ thống/tài nguyên nội bộ

## 2. Nguyên nhân gốc rễ

### 2.1 Nguyên nhân kỹ thuật phổ biến

- Dùng trực tiếp input vào filesystem API (`open`, `readfile`, `include`, `require`, `file_get_contents`...).
- Nối chuỗi đường dẫn nhưng không canonicalize.
- Chỉ filter chuỗi `../` bằng regex/string replace đơn giản.
- Validate sai thứ tự (lọc trước, decode sau).
- Chỉ check prefix/suffix mà không kiểm tra canonical path cuối cùng.
- Tin vào dữ liệu client (`filename`, `path`, `template`, `download`).

### 2.2 Pattern sai thiết kế thường gặp

- Chặn ở frontend nhưng không enforce ở backend.
- Chặn theo blacklist thay vì allowlist.
- Dùng nhiều lớp parse URL khác nhau (proxy/app/framework) gây mismatch.

## 3. Các biến thể khai thác chính

### 3.1 Arbitrary file read

Đọc file hệ thống, source code, config, secret.

### 3.2 LFI trong include context

Input không chỉ đọc file mà còn có thể khiến nội dung được execute (tùy runtime).

### 3.3 RFI (ít gặp hơn)

Include file từ URL remote, thường phụ thuộc cấu hình nguy hiểm.

### 3.4 Arbitrary file write qua traversal

Khi endpoint ghi file có path do user kiểm soát, attacker có thể ghi shell vào webroot và chiếm quyền thực thi.

## 4. Cách phát hiện theo tư duy hệ thống

Mục tiêu phát hiện:

1. Có đọc/include file ngoài phạm vi hay không.
2. Bypass xảy ra ở lớp nào (normalize, decode, route, extension check).
3. Có thể mở rộng sang leak secret hoặc RCE hay không.

### 4.1 Recon điểm tiềm năng

Ưu tiên tham số:

- `file`, `filename`, `path`, `page`, `template`, `include`, `download`, `doc`, `view`.

### 4.2 Oracle xác nhận

- Nội dung đặc trưng file hệ thống (`root:x:`, `daemon:`, `[extensions]`).
- Khác biệt status/length/body so với baseline.
- Lỗi filesystem (`No such file`, `failed to open stream`, `Permission denied`).

### 4.3 Quy trình test nhanh

1. Chụp baseline với input hợp lệ.
2. Thử traversal cơ bản.
3. Thử absolute path.
4. Thử payload bypass encode/nested.
5. So sánh phản hồi và chốt bằng chứng.

## 5. Bypass techniques quan trọng

### 5.1 Encoding/decoding mismatch

- URL encode, double encode, mixed encode.
- Khai thác trường hợp app decode nhiều lần hoặc decode lệch lớp.

### 5.2 Path normalization bypass

- Nested traversal (`....//`), slash confusion, dot mangling.
- Prefix-hold escape (`/var/www/images/../../../etc/passwd`).

### 5.3 Filter evasion

- Null byte trong hệ legacy.
- Case-insensitive protocol/wrapper trong PHP.
- Proxy mismatch kiểu `..;/` trong một số kiến trúc.

### 5.4 Client-side normalization

Một số HTTP client tự normalize `../`; cần giữ nguyên payload khi gửi request.

## 6. Mục tiêu khai thác dữ liệu (ưu tiên thực chiến)

### 6.1 Linux

- `/etc/passwd`, `/etc/shadow`, `/etc/hosts`
- `/proc/self/environ`, `/proc/self/cmdline`, `/proc/self/cwd/...`
- `/var/log/apache2/access.log`, `/var/log/nginx/access.log`
- `/run/secrets/kubernetes.io/serviceaccount/token`

### 6.2 Windows

- `C:\Windows\win.ini`
- `C:\windows\system32\license.rtf`
- `c:/inetpub/wwwroot/web.config`
- `c:/inetpub/logs/logfiles`

## 7. LFI -> RCE: các chuỗi leo thang điển hình

- Log poisoning -> include access/error log.
- `/proc/self/environ` poisoning qua header.
- PHP session poisoning rồi include session file.
- `php://input`, `data://`, `zip://`, `phar://` (phụ thuộc cấu hình/ngữ cảnh).
- File write traversal -> drop webshell vào webroot.

Lưu ý cốt lõi:

- Không phải mọi LFI đều thành RCE.
- Khả năng RCE phụ thuộc context include, runtime, quyền ghi file và cấu hình bảo mật.

## 8. Workflow pentest/CTF đề xuất

1. Tìm endpoint có dấu hiệu thao tác file.
2. Chụp baseline.
3. Bắn bộ payload xác nhận nhanh (Linux + Windows + encoded + nested).
4. Khi có primitive đọc file, ưu tiên loot file giá trị cao.
5. Đánh giá khả năng pivot sang RCE theo điều kiện thực tế.
6. Mở rộng bằng wordlist theo giai đoạn.
7. Chốt PoC với request/response rõ ràng và mô tả impact.

Wordlist thực hành trong repo:

- `_knowledge_base/Web/Path traversal/reference/LFI-LFISuite-pathtotest.txt`

## 9. Tác động bảo mật

### 9.1 Confidentiality

- Lộ source code, credential, secret, token.

### 9.2 Integrity

- Nếu có write primitive hoặc include execute, attacker có thể sửa hành vi ứng dụng.

### 9.3 Availability

- Có thể gây gián đoạn dịch vụ qua thao tác file nguy hiểm hoặc khai thác sâu hơn.

## 10. Phòng thủ đúng bản chất

### 10.1 Nguyên tắc cốt lõi

1. Không cho user input quyết định trực tiếp đường dẫn file.
2. Dùng allowlist định danh tài nguyên thay cho path thô.
3. Canonicalize path và kiểm tra path cuối cùng phải nằm trong base directory.
4. Enforce rule nhất quán ở backend, không dựa vào frontend.
5. Chạy service theo least privilege.

### 10.2 Kiểm soát bổ trợ

- Chuẩn hóa route/path handling giữa reverse proxy và application.
- Tắt/giới hạn wrapper/protocol nguy hiểm nếu không cần.
- Logging truy cập file bất thường và alert theo pattern traversal.
- Test định kỳ bằng SAST/DAST/pentest với tập payload đa dạng.

### 10.3 Anti-pattern cần tránh

- Chỉ replace `../` rồi cho rằng đã an toàn.
- Chỉ kiểm tra prefix/suffix mà bỏ qua canonical path.
- Dựa vào blacklist ký tự thay vì kiểm soát mô hình truy cập tài nguyên.
