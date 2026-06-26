# Bề Mặt Tấn Công Ẩn Cho XXE

## Vì Sao Bề Mặt Ẩn Quan Trọng

Nhiều hệ thống không có endpoint XML rõ ràng, nhưng vẫn parse XML ở backend thông qua:

- Định dạng file upload
- Giao thức tích hợp
- Content-type conversion
- Biến đổi ở lớp middleware

Vì vậy, XXE cần được test theo luồng dữ liệu, không chỉ theo API endpoint.

## Tấn Công XInclude

Khi attacker không kiểm soát được `DOCTYPE`, vẫn có thể chèn `XInclude` nếu parser hỗ trợ.

```xml
<foo xmlns:xi="http://www.w3.org/2001/XInclude">
  <xi:include parse="text" href="file:///etc/passwd"/>
</foo>
```

Thường xuất hiện khi dữ liệu người dùng được embed vào XML do server tự sinh.

## Bề Mặt Upload Tệp

## 1) SVG

SVG là định dạng ảnh dựa trên XML. Nếu backend image processor hỗ trợ SVG, payload có thể kích hoạt XXE.

```xml
<?xml version="1.0" standalone="yes"?>
<!DOCTYPE test [<!ENTITY xxe SYSTEM "file:///etc/hostname">]>
<svg xmlns="http://www.w3.org/2000/svg">
  <text>&xxe;</text>
</svg>
```

## 2) DOCX / XLSX / PPTX

OpenXML là ZIP chứa nhiều file XML. Parser có thể parse các XML bên trong để trích data.

Mẫu khai thác:

1. Giải nén file Office.
2. Chèn payload vào file XML phù hợp (`word/document.xml`, `xl/workbook.xml`, ...).
3. Nén lại bằng công cụ/tùy chọn compression đúng định dạng.
4. Upload và theo dõi signal OOB/in-band.

## 3) XLIFF / RSS / Phần Thân SOAP

- XLIFF upload pipelines
- RSS importers
- SOAP gateways

Các định dạng này đều có thể trở thành điểm parse XML thực thi entity.

## Đánh Tráo Content-Type Sang XML

Một endpoint có thể mong đợi JSON/form-data nhưng backend vẫn chấp nhận XML.

### Ví Dụ Chuyển Đổi

```http
Content-Type: application/x-www-form-urlencoded
foo=bar
```

chuyển thành:

```http
Content-Type: text/xml

<?xml version="1.0"?><foo>bar</foo>
```

Nếu hành vi nghiệp vụ không đổi nhưng parser được kích hoạt, bạn vừa tìm thấy bề mặt XXE ẩn.

## Mẫu Chuyển Đổi Endpoint JSON

Một số stack chấp nhận `application/xml` bên cạnh `application/json`.

- Chuyển object JSON sang XML root tree
- Giữ nguyên semantic fields
- Chèn payload entity vào field có khả năng reflected/processed

## Checklist Khảo Sát Bề Mặt Ẩn

1. Liệt kê toàn bộ chức năng upload/import.
2. Liệt kê integration protocol (SOAP/SAML/RSS/XLIFF).
3. Test content-type alternatives cho các endpoint business-critical.
4. Theo dõi parser errors (`SAXParseException`, XML validation errors).
5. Thử XInclude khi không control được full XML document.

## Tệp Liên Quan

- [03-detection.md](03-detection.md)
- [04-exploitation-workflow.md](04-exploitation-workflow.md)
- [09-bypass-and-advanced-techniques.md](09-bypass-and-advanced-techniques.md)
