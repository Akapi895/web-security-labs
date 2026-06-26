# File Upload Vulnerability — Overview

## Definition

File Upload Vulnerability là lớp lỗ hổng phát sinh khi một ứng dụng web cho phép người dùng tải file lên hệ thống mà không kiểm tra đầy đủ các thuộc tính của file — bao gồm tên, phần mở rộng (extension), kiểu nội dung (MIME type), nội dung thực tế (content/magic bytes) hoặc kích thước. Kẻ tấn công có thể lợi dụng điểm yếu này để tải lên file độc hại, từ đó thực thi mã tùy ý trên server, ghi đè file hệ thống, hoặc tấn công phía client.

Bản chất của lỗ hổng nằm ở sự bất đối xứng giữa **những gì ứng dụng tin tưởng** về file được upload và **những gì file đó thực sự có thể làm** khi được lưu trữ và xử lý bởi hệ thống.

## Vai trò của File Upload trong kiến trúc web

Chức năng upload file xuất hiện gần như ở mọi ứng dụng web hiện đại: avatar người dùng, đính kèm tài liệu, import dữ liệu CSV/Excel, upload hình ảnh sản phẩm, v.v. Luồng xử lý tổng quát:

```
Client (Browser)                    Server
     |                                |
     |-- HTTP POST multipart/form --> |
     |   (file binary + metadata)     |
     |                                |-- Validation (extension, MIME, content)
     |                                |-- Storage (filesystem / database / CDN)
     |                                |-- Response (URL / status)
     |<----- HTTP Response ---------- |
```

Khi server nhận file, nó thường phải xử lý hai loại dữ liệu:

| Loại dữ liệu      | Mô tả                                    | Rủi ro                                              |
| ----------------- | ---------------------------------------- | --------------------------------------------------- |
| **File metadata** | Tên file, đường dẫn, Content-Type header | Path traversal, ghi đè file, injection vào tên file |
| **File content**  | Nội dung binary thực tế của file         | Thực thi mã, khai thác parser, polyglot attack      |

## Cơ chế xử lý file tĩnh trên web server

Để hiểu lỗ hổng File Upload, cần nắm cách web server xử lý request đến file tĩnh:

1. Server phân tích đường dẫn request để xác định **file extension**
2. Extension được so khớp với danh sách **MIME type mappings** đã cấu hình
3. Tùy thuộc kết quả:
   - **Non-executable** (`.jpg`, `.html` tĩnh): Server trả nội dung file trực tiếp trong HTTP response
   - **Executable + configured** (`.php`, `.jsp`): Server thực thi file như script, gán biến từ headers/parameters, trả output
   - **Executable + NOT configured**: Server trả lỗi hoặc phục vụ nội dung dưới dạng plain text (có thể leak source code)

Điểm mấu chốt: **nếu attacker upload được file có extension mà server cấu hình để thực thi, file đó sẽ được chạy như code khi có request đến nó.**

## Impact

| Impact                     | Mô tả                                                           |
| -------------------------- | --------------------------------------------------------------- |
| **Remote Code Execution**  | Upload web shell → thực thi lệnh OS tùy ý trên server           |
| **System Takeover**        | Chiếm quyền điều khiển hoàn toàn server                         |
| **File Overwrite**         | Ghi đè file cấu hình (`.htaccess`, `web.config`), file hệ thống |
| **Data Breach**            | Đọc file nhạy cảm, truy cập database                            |
| **Client-side Attack**     | Upload HTML/SVG chứa XSS, phishing page                         |
| **Denial of Service**      | Upload file khổng lồ, tràn ổ đĩa                                |
| **Pivot/Lateral Movement** | Dùng server bị chiếm để tấn công hệ thống nội bộ                |
| **Information Disclosure** | Lỗi upload tiết lộ đường dẫn nội bộ server                      |

## Phân loại lỗ hổng

### Theo nguyên nhân gốc rễ (Root Cause)

| Nguyên nhân                   | Mô tả                                                         |
| ----------------------------- | ------------------------------------------------------------- |
| Không kiểm tra extension      | Cho phép upload `.php`, `.jsp`, `.asp` trực tiếp              |
| Blacklist không đầy đủ        | Bỏ sót extension thay thế (`.php5`, `.phtml`, `.cer`)         |
| Tin tưởng Content-Type header | Chỉ kiểm tra MIME type do client gửi, dễ giả mạo              |
| Không kiểm tra nội dung file  | Không verify magic bytes hoặc cấu trúc file thực tế           |
| Xử lý tên file không an toàn  | Cho phép path traversal (`../`), ký tự đặc biệt               |
| Cấu hình server sai           | Upload directory có quyền execute, thiếu handler restrictions |
| Race condition                | File được lưu trước khi validation hoàn tất                   |
| Xử lý archive không an toàn   | ZIP/TAR chứa symlink hoặc path traversal                      |

### Theo mục tiêu khai thác (Attack Goal)

| Mục tiêu               | Kỹ thuật điển hình                                           |
| ---------------------- | ------------------------------------------------------------ |
| Server-side RCE        | Upload web shell (PHP/JSP/ASP)                               |
| Configuration override | Upload `.htaccess`, `web.config`                             |
| Client-side attack     | Upload SVG/HTML chứa XSS                                     |
| File overwrite         | Path traversal trong filename                                |
| Information disclosure | Trigger error messages tiết lộ path                          |
| DoS                    | Upload file quá lớn hoặc file đặc biệt (NTFS reserved names) |
| SSRF/XXE               | Upload SVG/XML/PDF chứa external entity references           |

### Theo vị trí validation bị bypass

| Vị trí                       | Bypass                                      |
| ---------------------------- | ------------------------------------------- |
| Client-side (JavaScript)     | Intercept bằng proxy, gửi request trực tiếp |
| Content-Type header          | Thay đổi header trong request               |
| Extension blacklist          | Dùng extension thay thế, obfuscation        |
| Extension whitelist          | Double extension, null byte, special chars  |
| Magic bytes / file signature | Prepend magic bytes vào file độc hại        |
| Image dimension check        | Tạo polyglot file (image + code)            |
| File content scanning        | Encode payload, ẩn trong metadata           |

## Attack Workflow

```
1. RECONNAISSANCE   → Xác định chức năng upload, quan sát hành vi
2. FINGERPRINT      → Xác định cơ chế validation (extension? MIME? content?)
3. IDENTIFY STORAGE → Tìm nơi lưu file, URL truy cập, execution context
4. HYPOTHESIS       → Xây dựng giả thuyết bypass dựa trên validation type
5. CRAFT PAYLOAD    → Tạo file độc hại phù hợp với bypass strategy
6. UPLOAD & TEST    → Upload file, xác nhận file được lưu thành công
7. TRIGGER          → Request đến file để trigger execution
8. POST-EXPLOIT     → Web shell, đọc file, pivot, escalate
```

### Chi tiết từng giai đoạn

**Phase 1 — Reconnaissance**: Upload file hợp lệ, quan sát response — file được lưu ở đâu? URL truy cập có dạng gì? Tên file có bị thay đổi không? Có error message nào tiết lộ thông tin không?

**Phase 2 — Fingerprint Validation**: Thử upload file không hợp lệ (ví dụ `.php`) và phân tích response. Server từ chối vì extension? MIME type? Content? Kích thước? Từ đó xác định loại validation đang được áp dụng.

**Phase 3 — Identify Storage**: Xác định file được lưu trên cùng server hay CDN riêng? Có thể truy cập trực tiếp qua URL không? Upload directory có nằm trong web root không?

**Phase 4–5 — Bypass & Payload**: Dựa trên loại validation đã xác định, chọn kỹ thuật bypass phù hợp và craft payload tương ứng (chi tiết trong các file chuyên đề).

**Phase 6–7 — Upload & Trigger**: Upload file payload, sau đó gửi HTTP request đến URL của file để kích hoạt thực thi.

**Phase 8 — Post-Exploitation**: Sau khi có execution, triển khai web shell đầy đủ hơn, đọc file cấu hình, kết nối database, hoặc thiết lập reverse shell.

## Mô hình tấn công trừu tượng

Tương tự cách SQLi phân tách thành injection point → payload logic → execution context, File Upload vulnerability có thể được mô hình hóa qua ba thành phần:

```
┌─────────────────┐     ┌──────────────────┐     ┌────────────────────┐
│  UPLOAD VECTOR  │ ──> │  BYPASS STRATEGY  │ ──> │ EXECUTION CONTEXT  │
│                 │     │                   │     │                    │
│ • Upload form   │     │ • Extension trick │     │ • Same-origin exec │
│ • PUT method    │     │ • MIME spoof      │     │ • Reverse proxy    │
│ • URL fetch     │     │ • Magic bytes     │     │ • Decompression    │
│ • API endpoint  │     │ • Polyglot file   │     │ • Include/require  │
│ • Import func   │     │ • Race condition  │     │ • Config override  │
│ • Archive       │     │ • Path traversal  │     │ • Client-side      │
└─────────────────┘     └──────────────────┘     └────────────────────┘
```

- **Upload Vector**: Điểm vào — cách file được đưa lên server
- **Bypass Strategy**: Kỹ thuật vượt qua cơ chế kiểm soát
- **Execution Context**: Môi trường và cách thức file được xử lý/thực thi sau khi upload

## Cấu trúc Knowledge Base

| File                               | Nội dung                                                      |
| ---------------------------------- | ------------------------------------------------------------- |
| `00-overview.md`                   | Tổng quan, phân loại, workflow (file này)                     |
| `01-detection.md`                  | Trinh sát, xác định validation, fingerprint server            |
| `02-extension-bypass.md`           | Bypass kiểm tra extension (blacklist, whitelist, obfuscation) |
| `03-content-validation-bypass.md`  | Bypass Content-Type, magic bytes, polyglot                    |
| `04-server-config-exploitation.md` | Khai thác cấu hình server (.htaccess, web.config)             |
| `05-path-traversal-overwrite.md`   | Traversal qua filename, ghi đè file, NTFS tricks              |
| `06-race-conditions.md`            | Race condition trong upload flow                              |
| `07-archive-attacks.md`            | ZIP/TAR symlink, zip slip, decompression attacks              |
| `08-advanced-exploitation.md`      | ImageTragick, IDAT chunk, PDF polyglot, SSRF qua upload       |
| `09-platform-specific.md`          | PHP, ASP/.NET, JSP/Java, Python, uWSGI, Jetty                 |
| `10-secondary-impacts.md`          | XSS, XXE, SSRF, CSV injection qua file upload                 |
| `11-payloads-cheatsheet.md`        | Extension lists, magic bytes, web shell one-liners            |
| `12-defense-mitigation.md`         | Phòng thủ và khắc phục                                        |
