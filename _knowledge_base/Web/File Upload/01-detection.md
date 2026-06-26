# File Upload — Detection & Reconnaissance

## Mục tiêu giai đoạn Detection

Trước khi khai thác, attacker cần trả lời ba câu hỏi cốt lõi:

1. **Upload Vector**: Chức năng upload nằm ở đâu và hoạt động như thế nào?
2. **Validation Mechanism**: Server kiểm tra file bằng cơ chế nào?
3. **Storage & Execution Context**: File được lưu ở đâu và có thể thực thi không?

## Xác định Upload Vector

### Các vị trí upload phổ biến

| Vị trí                | Ví dụ                                   |
| --------------------- | --------------------------------------- |
| Profile/Avatar upload | `/profile/edit`, `/settings/avatar`     |
| Document attachment   | `/upload`, `/attach`, `/import`         |
| CMS media manager     | `/wp-admin/upload.php`, `/admin/media`  |
| API endpoint          | `POST /api/v1/files`, `PUT /api/upload` |
| Import/Export         | `/import/csv`, `/data/upload`           |
| Support/Ticket        | `/support/new`, `/ticket/attach`        |
| Registration form     | Form đăng ký có yêu cầu upload ID/ảnh   |

### HTTP Methods cho upload

| Method             | Mô tả                                                  |
| ------------------ | ------------------------------------------------------ |
| `POST` (multipart) | Phương thức phổ biến nhất, dùng `multipart/form-data`  |
| `PUT`              | Một số server cho phép PUT trực tiếp vào web directory |
| `PATCH`            | Cập nhật file qua API                                  |

**Kiểm tra PUT support:**

```http
OPTIONS /images/ HTTP/1.1
Host: target.com
```

Nếu response chứa `Allow: ... PUT ...`, có thể thử upload trực tiếp:

```http
PUT /images/shell.php HTTP/1.1
Host: target.com
Content-Type: application/x-httpd-php
Content-Length: 49

<?php echo file_get_contents('/etc/passwd'); ?>
```

### Cấu trúc HTTP multipart request

```http
POST /upload HTTP/1.1
Host: target.com
Content-Type: multipart/form-data; boundary=----Boundary123

------Boundary123
Content-Disposition: form-data; name="file"; filename="photo.jpg"
Content-Type: image/jpeg

[... binary content ...]
------Boundary123
Content-Disposition: form-data; name="description"

My photo
------Boundary123--
```

Các trường quan trọng cần chú ý khi phân tích:

- `filename`: Tên file do client gửi — có thể bị sanitize hoặc không
- `Content-Type`: MIME type do client khai báo — có thể bị validate hoặc không
- Binary content: Nội dung thực tế của file

## Fingerprint Validation Mechanism

Quy trình fingerprint validation là bước quan trọng nhất, quyết định chiến lược bypass. Mỗi thử nghiệm dưới đây giúp xác định một lớp validation cụ thể.

### Test 1: Baseline — Upload file hợp lệ

Upload file hợp lệ đúng định dạng được yêu cầu (ví dụ `.jpg` cho avatar). Quan sát:

- Response: File được lưu thành công? URL trả về?
- Tên file: Giữ nguyên hay bị đổi (random, hash)?
- Đường dẫn: Tiết lộ internal path hay hidden directory?

### Test 2: Extension-only change

Upload cùng nội dung hợp lệ (ảnh thật) nhưng đổi extension sang `.php`:

- **Bị từ chối** → Server kiểm tra extension
- **Được chấp nhận** → Extension không bị validate → thử upload web shell thực sự

### Test 3: MIME type manipulation

Upload file `.php` nhưng đổi `Content-Type` header sang `image/jpeg`:

- **Được chấp nhận** → Server chỉ kiểm tra Content-Type header (dễ bypass)
- **Vẫn bị từ chối** → Server kiểm tra extension hoặc content, không chỉ MIME

### Test 4: Content/Magic bytes check

Upload file có extension hợp lệ (`.jpg`) nhưng nội dung là PHP code:

- **Bị từ chối** → Server kiểm tra file content (magic bytes, image dimensions)
- **Được chấp nhận** → Server không kiểm tra nội dung thực tế

### Test 5: Polyglot test

Upload file là ảnh thật có chèn PHP code trong metadata (EXIF comment):

- **Được chấp nhận + code thực thi** → Server tin tưởng ảnh nhưng vẫn parse PHP
- **Được chấp nhận + code KHÔNG thực thi** → File không nằm trong execution context

### Ma trận kết quả fingerprinting

| Test                                  | Kết quả            | Kết luận                                          |
| ------------------------------------- | ------------------ | ------------------------------------------------- |
| Extension `.php` bị chặn              | Extension blocked  | → Thử extension bypass (02)                       |
| MIME fake `image/jpeg` bypass         | MIME-only check    | → Thay Content-Type header                        |
| Nội dung PHP trong `.jpg` bị chặn     | Content inspection | → Polyglot / metadata injection                   |
| File hợp lệ nhưng không truy cập được | Restricted access  | → Tìm path, race condition                        |
| File accessible nhưng không execute   | No execution       | → Server config exploit (04), path traversal (05) |

## Xác định Storage & Execution Context

### Tìm đường dẫn file đã upload

Sau khi upload thành công, cần xác định URL hoặc path để truy cập file:

| Phương pháp           | Chi tiết                                                            |
| --------------------- | ------------------------------------------------------------------- |
| Response body         | URL trực tiếp trong response JSON/HTML                              |
| Response header       | `Location` header sau redirect                                      |
| Page source           | Tìm `<img src="...">` hoặc `<a href="...">` trên page hiển thị file |
| Predictable path      | `/uploads/filename.ext`, `/static/uploads/filename.ext`             |
| Error message         | Lỗi tiết lộ internal path                                           |
| Directory brute-force | Dùng wordlist tìm upload directory                                  |

### Phân tích execution context

Khi đã tìm được URL file, kiểm tra xem server có **thực thi** file hay chỉ **phục vụ** nội dung:

```http
GET /uploads/test.php HTTP/1.1
Host: target.com
```

| Response                           | Ý nghĩa                                             |
| ---------------------------------- | --------------------------------------------------- |
| Output của PHP code                | Server thực thi file → RCE khả thi                  |
| Source code PHP hiển thị dạng text | Server không execute → cần bypass execution context |
| 403 Forbidden                      | Directory bị restrict → thử path traversal          |
| 404 Not Found                      | File bị đổi tên hoặc lưu ở path khác                |
| File chỉ return qua proxy/CDN      | Cần tìm cách truy cập trực tiếp trên origin server  |

### Kiểm tra server technology

Xác định technology stack giúp chọn loại payload phù hợp:

| Indicator                                                     | Technology          |
| ------------------------------------------------------------- | ------------------- |
| `.php` extension trong URL                                    | PHP                 |
| `.asp` / `.aspx`                                              | ASP / ASP.NET       |
| `.jsp` / `.do` / `.action`                                    | Java (Tomcat, etc.) |
| `X-Powered-By: PHP/x.x`                                       | PHP version         |
| `Server: Apache/2.x`                                          | Apache              |
| `Server: Microsoft-IIS/x.x`                                   | IIS                 |
| `Server: nginx`                                               | Nginx               |
| Cookie names (`PHPSESSID`, `JSESSIONID`, `ASP.NET_SessionId`) | PHP, Java, ASP.NET  |

## Information Disclosure qua Upload

Quá trình upload — ngay cả khi thất bại — có thể tiết lộ thông tin hữu ích:

| Hành động                              | Thông tin tiết lộ                                |
| -------------------------------------- | ------------------------------------------------ | -------------------------- |
| Upload file trùng tên file đã có       | Error message chứa đường dẫn đầy đủ              |
| Upload file trùng tên thư mục          | Internal path structure                          |
| Upload file với tên rất dài            | Maximum path length, OS type                     |
| Upload nhiều file đồng thời cùng tên   | Race condition behavior                          |
| Upload file với tên `.`, `..`, `...`   | Server path handling logic                       |
| Upload file với ký tự đặc biệt (`      | <>\*?"`)                                         | OS type (Windows vs Linux) |
| Upload file có reserved name (Windows) | `CON`, `PRN`, `AUX`, `NUL`, `COM1`... tiết lộ OS |

## Checklist trinh sát

```
[ ] Xác định tất cả upload endpoints
[ ] Thử PUT method trên các directory
[ ] Upload file hợp lệ, ghi nhận response đầy đủ
[ ] Xác định tên file sau upload (giữ nguyên? đổi?)
[ ] Xác định URL/path truy cập file
[ ] Test extension validation (đổi extension giữ content)
[ ] Test MIME validation (đổi Content-Type header)
[ ] Test content validation (giữ extension đổi content)
[ ] Xác định server technology (Apache/IIS/Nginx, PHP/ASP/JSP)
[ ] Kiểm tra execution context (file có được thực thi không?)
[ ] Kiểm tra upload directory permissions
[ ] Tìm kiếm information disclosure qua error messages
```
