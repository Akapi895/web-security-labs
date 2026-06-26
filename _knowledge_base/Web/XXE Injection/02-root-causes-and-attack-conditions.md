# Nguyên Nhân Gốc Rễ và Điều Kiện Hình Thành Tấn Công

## Đặt Vấn Đề Đúng Bản Chất

XXE không phải lỗi của XML bản thân, mà là lỗi thiết kế và cấu hình parser.

Bản chất gốc rễ:

- Ứng dụng cho phép input người dùng đi vào XML parser
- Parser được cấu hình để resolve external resources
- Hệ thống xung quanh (filesystem/network/error handling) cho phép attacker nhìn thấy tác động

## Các Nguyên Nhân Kỹ Thuật Chính

### 1. Parser Mặc Định hoặc Cấu Hình Không An Toàn

- Bật DTD processing dù không cần
- Bật external general entities / parameter entities
- Bật XInclude
- Không giới hạn protocol và truy cập network khi parse

### 2. Luồng Dữ Liệu XML Không Đáng Tin Cậy

- XML body từ API request
- XML sinh từ convert `application/json`/`x-www-form-urlencoded` sang XML
- XML trong file upload (SVG, DOCX, XLSX, XLIFF, RSS)
- XML được nối vào backend SOAP hoặc middleware processing

### 3. Sai Lầm Trong Giả Định Nghiệp Vụ

- Tin rằng payload XML “chỉ là data”
- Không tách biên trusted/untrusted trước parser
- Không giới hạn endpoint được phép nhận XML

### 4. Lộ Lỗi và Egress Quá Rộng

- Trả lỗi parser chi tiết ra client
- Cho phép outbound DNS/HTTP/FTP từ parser context
- Quyền đọc file quá rộng cho process account

## Điều Kiện Hình Thành Tấn Công

| Điều kiện                    | Mô tả                                       | Vai trò                       |
| ---------------------------- | ------------------------------------------- | ----------------------------- |
| Parser xử lý XML             | Ứng dụng parse XML trực tiếp hoặc gián tiếp | Bắt buộc                      |
| Bật resolve tài nguyên ngoài | Parser resolve DTD/entity/include           | Bắt buộc để XXE có tác dụng   |
| Attacker kiểm soát input     | Input chưa được ràng buộc schema tin cậy    | Bắt buộc                      |
| Có tín hiệu quan sát được    | Response/error/timing/OOB interaction       | Bắt buộc để khai thác thực tế |

## Mẫu Cấu Hình Sai Thường Gặp

| Cấu hình sai                             | Hệ quả                           |
| ---------------------------------------- | -------------------------------- |
| Cho phép DOCTYPE toàn cục                | Attacker định nghĩa entity mới   |
| Cho phép external entities               | Đọc file local/remote SSRF       |
| Cho phép external DTD + outbound network | Blind OOB exfiltration           |
| Lộ parser error chi tiết                 | Error-based data leakage         |
| Process account có quyền file rộng       | Impact mở rộng thành data breach |

## Mapping Nguyên Nhân -> Kỹ Thuật Khai Thác

| Nguyên nhân                         | Pattern khai thác thường gặp                      |
| ----------------------------------- | ------------------------------------------------- |
| External entity enabled             | In-band file read, SSRF                           |
| Parameter entity enabled            | Blind OOB detection/exfil                         |
| External DTD allowed                | Dynamic payload và error-based leakage            |
| Có local DTD files + parser hybrids | Local DTD repurposing                             |
| XInclude enabled                    | XXE-style file read dù không control được DOCTYPE |

## Vì Sao “Chỉ Validate Input” Là Không Đủ

Validation thường thất bại vì:

- Có nhiều biến thể encoding/obfuscation
- XML parser có nhiều feature khác ngoài external entity cơ bản
- Hidden surface trong file format có XML subcomponents

Kiểm soát đúng gốc vẫn là parser hardening + architecture constraints.

## Nguyên Tắc Thiết Kế An Toàn (Tóm Tắt)

1. Tắt DTD và external entity nếu không bắt buộc.
2. Tắt XInclude và external resource loading.
3. Không parse XML untrusted trong context có quyền network/file mở rộng.
4. Hạn chế outbound network và quyền file của process parser.
5. Ẩn error chi tiết, log nội bộ đầy đủ.

## Tệp Liên Quan

- [01-xml-dtd-parser-fundamentals.md](01-xml-dtd-parser-fundamentals.md)
- [03-detection.md](03-detection.md)
- [11-defense-mitigation.md](11-defense-mitigation.md)
