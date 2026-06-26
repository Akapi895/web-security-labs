# Nền Tảng XML, DTD, và Parser

## XML Trong Kiến Trúc Ứng Dụng

XML là định dạng dữ liệu có cấu trúc, thường được dùng cho:

- Trao đổi dữ liệu giữa các service (SOAP, XML API)
- Tài liệu chứa thành phần XML con (DOCX/XLSX/SVG)
- Các pipeline nhập/xuất và nội địa hóa (XLIFF)

Trong bối cảnh bảo mật, XML parser là thành phần quyết định: nếu parser có quyền resolve external resource thì input XML có thể bị biến thành lệnh truy cập tài nguyên ngoài ý muốn.

## Parser XML Xử Lý Dữ Liệu Như Thế Nào

Một luồng xử lý điển hình:

```text
Nhận XML -> Parse phần mở đầu -> Xử lý DOCTYPE/DTD -> Mở rộng entity -> Dựng cây đối tượng -> Trả dữ liệu cho logic nghiệp vụ
```

Điểm nhạy cảm nằm ở giai đoạn xử lý DOCTYPE/DTD và mở rộng entity.

## Cơ Bản Về DTD và Entity

DTD (Document Type Definition) cho phép khai báo cấu trúc và entity.

### Thực Thể Internal

Entity được định nghĩa bên trong DTD:

```xml
<!DOCTYPE root [
  <!ENTITY company "Acme">
]>
<root>&company;</root>
```

### Thực Thể External

Entity lấy giá trị từ file/URL thông qua `SYSTEM`:

```xml
<!DOCTYPE root [
  <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<root>&xxe;</root>
```

Nếu parser resolve entity này, nội dung file được chèn vào tài liệu XML sau khi parse.

## General Entity và Parameter Entity

| Loại               | Cú pháp  | Dùng ở đâu         |
| ------------------ | -------- | ------------------ |
| Thực thể tổng quát | `&name;` | Trong nội dung XML |
| Thực thể tham số   | `%name;` | Chỉ trong DTD      |

Parameter entity đặc biệt hữu dụng cho blind XXE/OOB và external DTD chaining.

## Bề Mặt Include Tài Nguyên Bên Ngoài

Không chỉ external entity mới nguy hiểm. Các cơ chế dưới đây cũng có thể tạo đầu vào XXE-style:

- External DTD (`SYSTEM "http://.../evil.dtd"`)
- External schema/stylesheets
- XInclude (`xi:include`)
- Protocol handlers (`file:`, `http:`, `ftp:`, `jar:`, `php://...` tùy parser/runtime)

## Vì Sao DOCTYPE Là Ranh Giới Bảo Mật

Nếu ứng dụng không cần DTD nhưng parser vẫn cho phép DOCTYPE:

1. Attacker có thể khai báo entity mới
2. Parser có thể truy cập tài nguyên local/remote
3. Giá trị lấy được được nối vào XML data
4. Logic nghiệp vụ vô tình xử lý output đó như dữ liệu hợp lệ

Do đó, để bắt XXE cần xem DOCTYPE là một security boundary quan trọng.

## Mô Hình Tư Duy Tối Thiểu Cho XXE

```text
XML do người dùng kiểm soát + cấu hình parser không an toàn + khả năng chạm filesystem/network
= resolve external entity
= XXE impact
```

## Các Tùy Chọn Cấu Hình Parser Liên Quan Trực Tiếp Đến XXE

Những option parser thường liên quan trực tiếp đến XXE:

- Cho phép phân tích DTD
- Cho phép thực thể tổng quát bên ngoài
- Cho phép thực thể tham số bên ngoài
- Cho phép XInclude
- Cho phép truy cập mạng khi parse

Nếu các option này được tắt đúng cách, phần lớn XXE sẽ bị triệt tiêu ở gốc.

## Tệp Liên Quan

- [00-overview.md](00-overview.md)
- [02-root-causes-and-attack-conditions.md](02-root-causes-and-attack-conditions.md)
- [11-defense-mitigation.md](11-defense-mitigation.md)
