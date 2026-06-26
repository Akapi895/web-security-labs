# XML External Entity (XXE) - Báo Cáo Tổng Hợp

## 1. XXE là gì và bản chất kỹ thuật

XXE (XML External Entity) là lỗ hổng xảy ra khi ứng dụng phân tích XML với cấu hình parser không an toàn, cho phép resolve thực thể bên ngoài hoặc tài nguyên bên ngoài từ input do người dùng kiểm soát.

Bản chất:

- XML parser có khả năng tải file/URL bên ngoài tài liệu XML
- Dữ liệu đó tải về được chèn vào quá trình parse
- Ứng dụng vô tình xử lý kết quả như dữ liệu hợp lệ

## 2. Vai trò của XML, DTD và parser trong lỗi XXE

DTD cho phép khai báo entities, gồm cả entities trỏ đến nguồn bên ngoài (`SYSTEM`).

Khi parser cho phép:

- Xử lý DTD
- Resolve thực thể bên ngoài
- Tải external DTD
- XInclude

thì input XML độc hại có thể biến thành lệnh truy cập file hệ thống hoặc mạng nội bộ.

## 3. Nguyên nhân gốc rễ

1. Cấu hình parser không an toàn (bật external entities/DTD/XInclude).
2. Dữ liệu XML không tin cậy đi trực tiếp vào parser.
3. Bề mặt XML ẩn (file upload, SOAP, content-type conversion).
4. Xử lý lỗi và chính sách egress yếu (lộ parser errors, cho outbound requests).

## 4. Điều kiện hình thành khai thác

XXE thường cần:

- Có điểm xử lý XML
- Có khả năng điều khiển payload XML
- Parser cho resolve external resources
- Có kênh quan sát (response, error, OOB)

## 5. Trình tự khai thác chuẩn hóa

```text
1. Tìm bề mặt xử lý XML
2. Kiểm tra năng lực parser (internal/external/parameter entity)
3. Xác định tín hiệu (in-band, error, OOB)
4. Chọn mục tiêu khai thác (file read, SSRF, exfil)
5. Tối ưu payload theo parser constraints
6. Mở rộng impact và thu thập evidence
```

## 6. Các nhóm khai thác chính

### 6.1 Đọc File In-Band

- Đọc file cục bộ (`/etc/passwd`, `boot.ini`, file cấu hình)
- Có thể kết hợp bộ bao (context-dependent) để base64 data

### 6.2 XXE -> SSRF

- Dùng external entity trỏ đến URL nội bộ
- Truy cập metadata/internal service từ bối cảnh server

### 6.3 Blind XXE OOB

- Không có dữ liệu trả về trực tiếp
- Dùng collaborator + parameter entities + external DTD

### 6.4 XXE Dựa Trên Lỗi

- Kích hoạt parser error chứa dữ liệu nhạy cảm
- Hữu ích khi không có in-band reflection

### 6.5 Tái Mục Đích Local DTD

- Dùng DTD có sẵn trên host để bypass outbound restrictions
- Kỹ thuật nâng cao cho môi trường được gia cố một phần

## 7. Bề Mặt Tấn Công Ẩn Quan Trọng

- XInclude khi không kiểm soát được DOCTYPE
- SVG, DOCX, XLSX, XLIFF, RSS uploads
- SOAP wrappers
- Endpoint JSON/Form nhưng backend chấp nhận XML

## 8. Rủi ro kinh doanh

- Lộ thông tin xác thực, khóa API, PII
- Pivot vào hệ thống nội bộ qua SSRF
- Nguy cơ chiếm quyền đám mây qua lạm dụng metadata
- DoS parser/service với entity expansion payloads

## 9. Phòng thủ đúng bản chất

1. Tắt DTD/external entity/XInclude nếu không cần.
2. Tắt truy cập mạng khi parse XML.
3. Hạn chế quyền file và outbound của runtime.
4. Ẩn parser errors khỏi client, log nội bộ đầy đủ.
5. Kiểm thử bảo mật định kỳ cho bề mặt XML ẩn.

## 10. Ánh Xạ "nguyên nhân -> hậu quả -> giải pháp"

| Nguyên nhân                       | Hậu quả                    | Giải pháp ưu tiên                             |
| --------------------------------- | -------------------------- | --------------------------------------------- |
| Parser resolve thực thể bên ngoài | Đọc file, SSRF             | Vô hiệu hóa external entities và external DTD |
| Mạng outbound mở                  | Blind OOB exfiltration     | Lọc egress + phân đoạn mạng                   |
| Lộ parser error chi tiết          | Rò rỉ dữ liệu dựa trên lỗi | Lỗi chung cho client + ghi log nội bộ         |
| Bề mặt XML ẩn qua upload/tích hợp | Khó phát hiện, dễ bỏ sót   | Kiểm kê + kiểm thử toàn bộ luồng xử lý XML    |

## 11. Kết luận

XXE là lỗi ở tầng parser và kiến trúc, không chỉ là lỗi payload.

Nếu cần tóm gọn một câu:

Khi ứng dụng cho XML parser truy cập tài nguyên ngoài từ dữ liệu không tin cậy, attacker có thể biến parser thành công cụ đọc file, SSRF và exfiltration.

Do đó, fix bền vững phải bắt đầu từ parser hardening, network controls, và quản trị toàn bộ bề mặt tấn công XML ẩn.
