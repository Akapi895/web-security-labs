# Phòng Thủ và Giảm Thiểu XXE

## Mục Tiêu Bảo Mật

Mục tiêu phòng thủ XXE là loại bỏ khả năng parser truy cập tài nguyên ngoài khi xử lý XML untrusted.

Ngắn gọn:

- Không cho parser resolve external entities
- Không cho parser load external DTD/schema/include
- Hạn chế quyền hệ thống và egress network của runtime

## Kiểm Soát Chính (Bắt Buộc)

## 1) Gia Cố Cấu Hình XML Parser

Tắt các tính năng không cần thiết:

- DTD processing
- External general entities
- External parameter entities
- External DTD loading
- XInclude
- Network access khi parse

### Ví Dụ Java (DocumentBuilderFactory)

```java
DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
factory.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);
factory.setFeature("http://xml.org/sax/features/external-general-entities", false);
factory.setFeature("http://xml.org/sax/features/external-parameter-entities", false);
factory.setFeature("http://apache.org/xml/features/nonvalidating/load-external-dtd", false);
factory.setXIncludeAware(false);
factory.setExpandEntityReferences(false);
```

### Ví Dụ .NET (XmlReaderSettings)

```csharp
var settings = new XmlReaderSettings
{
    DtdProcessing = DtdProcessing.Prohibit,
    XmlResolver = null
};

using var reader = XmlReader.Create(stream, settings);
```

### Ví Dụ Python lxml

```python
from lxml import etree

parser = etree.XMLParser(
    resolve_entities=False,
    load_dtd=False,
    no_network=True
)
root = etree.fromstring(xml_data, parser=parser)
```

Nếu ứng dụng không bắt buộc XML, cân nhắc chuyển sang JSON + schema validation.

## 2) Xử Lý Input Nghiêm Ngặt

- Tách biệt rõ trusted và untrusted XML sources
- Áp dụng schema validation theo allow-list cho fields cần thiết
- Không cho người dùng quyết định parser mode/protocol

## 3) Vô Hiệu Hóa Bề Mặt XML Ẩn

Kiểm soát đường parse XML trong:

- SVG/image processing pipeline
- Office document importers
- SOAP gateways
- XLIFF/RSS processing
- Content-type auto-conversion middleware

## Kiểm Soát Bổ Trợ (Phòng Thủ Nhiều Lớp)

## 4) Hạn Chế Mạng Outbound

- Chặn outbound DNS/HTTP/FTP từ service parse XML nếu không cần
- Dùng egress allow-list
- Tách subnet/routing cho parser workloads

## 5) Runtime Quyền Tối Thiểu

- Process account không được có quyền đọc file nhạy cảm
- Tách quyền config, secret và key material
- Hạn chế mount paths trong container/runtime

## 6) Xử Lý Lỗi An Toàn

- Không trả parser exception chi tiết ra client
- Log chi tiết nội bộ (có redaction)
- Theo dõi parser errors bất thường để phát hiện exploit attempts

## 7) Monitoring và Detection

Nên theo dõi:

- Request có `DOCTYPE`, `ENTITY`, `SYSTEM`, `PUBLIC`, `XInclude`
- Đột biến parser errors (`SAXParseException`, entity resolution errors)
- Outbound requests bất thường từ app parser

## Checklist Xác Minh

| Kiểm tra                      | Kỳ vọng                       |
| ----------------------------- | ----------------------------- |
| DOCTYPE payload               | Bị từ chối parse              |
| External entity payload       | Không resolve file/url        |
| Parameter entity payload      | Không có OOB interaction      |
| XInclude payload              | Không include file            |
| Upload XML-based file payload | Không trigger external access |

## Anti-Pattern Thường Gặp

| Anti-pattern                     | Vấn đề                                 |
| -------------------------------- | -------------------------------------- |
| Chỉ dùng WAF                     | Không sửa được parser behavior gốc     |
| Chỉ filter keyword `<!DOCTYPE`   | Dễ bị bypass encoding/obfuscation      |
| Tin rằng endpoint không nhận XML | Hidden XML surface vẫn tồn tại         |
| Trả parser error cho client      | Tạo điều kiện error-based exfiltration |

## Kế Hoạch Triển Khai Giảm Thiểu

1. Kiểm kê tất cả điểm parse XML trong hệ thống.
2. Áp dụng parser defaults an toàn theo framework.
3. Viết kiểm thử hồi quy với payload XXE mẫu.
4. Bật egress control và least-privilege runtime.
5. Bổ sung monitoring/rules cho XML abuse pattern.

## Tệp Liên Quan

- [02-root-causes-and-attack-conditions.md](02-root-causes-and-attack-conditions.md)
- [03-detection.md](03-detection.md)
- [10-payloads-cheatsheet.md](10-payloads-cheatsheet.md)
- [13-reference-map.md](13-reference-map.md)
