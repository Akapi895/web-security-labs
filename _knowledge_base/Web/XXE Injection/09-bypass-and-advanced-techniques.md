# Kỹ Thuật Bypass và XXE Nâng Cao

## Phạm Vi

File này tổng hợp các kỹ thuật nâng cao được quan sát trong tài liệu tham chiếu: bypass parser/filter, lạm dụng local DTD, mẹo giao thức, và các hướng exploitation đặc thù runtime.

## 1. Mã Hóa và Làm Rối Để Bypass

## Mẹo Mã Hóa Ký Tự

- UTF-16/UTF-7 payload để qua bộ lọc keyword đơn giản
- Numeric entity encoding để trì hoãn parse

Ví dụ chuyển payload UTF-8 sang UTF-16BE:

```bash
cat utf8exploit.xml | iconv -f UTF-8 -t UTF-16BE > utf16exploit.xml
```

## Thực Thể Số HTML Trong Quá Trình Dựng DTD

Có thể tạo entity bên trong entity bằng numeric encoding để bypass một số kiểm tra.

## 2. Biến Thể Giao Thức

| Giao thức              | Mục đích                               | Lưu ý                                        |
| ---------------------- | -------------------------------------- | -------------------------------------------- |
| `file://`              | Đọc file local                         | Cơ bản nhất                                  |
| `http://` / `https://` | SSRF, OOB                              | Phụ thuộc egress                             |
| `ftp://`               | Exfil payload dài/nhiều dòng           | Thường hữu ích cho blind exfil               |
| `php://filter/...`     | Base64 file content                    | Chỉ phù hợp stack PHP                        |
| `jar:`                 | Truy cập file bên trong archive (Java) | Hữu ích khi abuse local/system DTD scenarios |
| `expect://`            | Có thể dẫn tới command execution       | Chỉ khi module/runtime cho phép              |

## 3. Tái Mục Đích Local DTD

Khi không tải được remote DTD, có thể tải local DTD có sẵn và redefine entity:

- Linux thường gặp các DTD dưới `/usr/share/...`
- Windows có các DTD trong subsystem XML của hệ điều hành/ứng dụng

Kỹ thuật này đặc biệt quan trọng trong blind XXE không outbound.

## 4. Chuỗi Khai Thác Dựa Trên Lỗi

Error-based XXE dựa trên ý tưởng:

1. Nạp file cần leak vào parameter entity.
2. Tạo entity trỏ đến file path không tồn tại có chèn nội dung file.
3. Để parser throw exception kèm path bị lỗi.

Nếu ứng dụng lộ parser error, data sẽ bị lộ.

## 5. XXE Qua Các Định Dạng Không Hiển Nhiên

- SVG rasterization
- DOCX/XLSX XML subparts
- SOAP CDATA wrappers
- RSS/XLIFF importers

Đặc điểm chung: ứng dụng “không nghĩ mình parse XML” nhưng thư viện backend vẫn parse XML.

## 6. Ví Dụ Leo Thang Theo Runtime

## Lạm Dụng Java XMLDecoder (Rủi Ro Lân Cận)

Nếu ứng dụng sử dụng `java.beans.XMLDecoder` với input không tin cậy, có thể đặt payload tạo object và gọi method nguy hiểm (`Runtime.exec`, `ProcessBuilder`).

Đây là vector bên cạnh XXE, nhưng thường cũng xuất hiện trong cùng hệ sinh thái XML insecure.

## Ghi Chú Về Parameter-Entity Trong Python lxml

Tài liệu tham chiếu nêu case lxml/libxml2 cho thấy một số version/config có thể vẫn cho parameter-entity expansion trong bối cảnh tương tự error-based disclosure.

Ý nghĩa cho pentest:

- Cần test hành vi parser thực tế theo version/runtime
- Không giả định parser đã an toàn chỉ vì một flag config

## 7. Nhóm Payload Hướng DoS

- Billion Laughs
- Parameter Laughs
- External resource không kết thúc (`/dev/random` style)

Chỉ nên dùng trong lab hoặc môi trường được cấp phép rõ ràng.

## 8. Chiến Lược Bypass Thực Tiễn

```text
1. Payload DOCTYPE cơ bản
2. Fallback sang parameter entity
3. Chuyển hướng qua external DTD
4. Điều chỉnh mã hóa/làm rối
5. Dịch chuyển sang bề mặt ẩn (XInclude, upload, đổi content-type)
6. Tái mục đích local DTD khi outbound bị chặn
```

## Tệp Liên Quan

- [07-blind-xxe-and-oob-exfiltration.md](07-blind-xxe-and-oob-exfiltration.md)
- [08-hidden-attack-surface.md](08-hidden-attack-surface.md)
- [10-payloads-cheatsheet.md](10-payloads-cheatsheet.md)
- [11-defense-mitigation.md](11-defense-mitigation.md)
