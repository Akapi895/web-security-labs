# Thao túng đường dẫn tệp cục bộ và chèn truy vấn phía client

## Thao túng đường dẫn tệp cục bộ dựa trên DOM

### Định nghĩa

Input do attacker kiểm soát được truyền vào API xử lý tệp của trình duyệt dưới dạng tên tệp hoặc đích tệp.

### Các sink chính

- `FileReader.readAsArrayBuffer()`
- `FileReader.readAsBinaryString()`
- `FileReader.readAsDataURL()`
- `FileReader.readAsText()`
- `FileReader.readAsFile()`
- `FileReader.root.getFile()`

### Tác động

Tác động phụ thuộc cách ứng dụng sử dụng nội dung tệp được mở/chọn:

1. Truy xuất dữ liệu trái phép từ tệp cục bộ.
2. Ghi dữ liệu ngoài ý muốn trong một số quy trình xử lý tệp.

## Chèn SQL phía client dựa trên DOM

### Định nghĩa

Input do attacker kiểm soát bị nối vào truy vấn SQL phía client (ví dụ mô hình Web SQL) và được thực thi trong cơ sở dữ liệu cục bộ của trình duyệt.

### Sink

- `executeSql()`

### Tác động

1. Đọc hoặc chỉnh sửa dữ liệu có cấu trúc lưu trong trình duyệt.
2. Thao túng các hành động chờ xử lý được lưu phía client.

### Phòng ngừa

Dùng truy vấn tham số hóa trong API SQL phía client; tránh dựng query string từ input không đáng tin cậy.

## Chèn XPath phía client dựa trên DOM

### Điểm nhận

- `document.evaluate()`
- `element.evaluate()`

### Tác động

Attacker có thể thay đổi ngữ nghĩa truy vấn XPath và ảnh hưởng logic chọn dữ liệu/ra quyết định.

## Chèn JSON phía client dựa trên DOM

### Các điểm nhận

- `JSON.parse()`
- `jQuery.parseJSON()`
- `$.parseJSON()`

### Tác động

JSON bị tiêm có thể làm hỏng cấu trúc đối tượng kỳ vọng và kích hoạt nhánh logic không an toàn.

## Mô hình giảm thiểu dùng chung

1. Luôn coi dữ liệu đầu vào là không đáng tin cậy trước khi vào API phân tích cú pháp/truy vấn.
2. Dùng lược đồ chặt và kiểm tra kiểu dữ liệu.
3. Tránh dựng parser/query động từ input thô.
4. Áp hành vi tối thiểu quyền cho các thao tác dữ liệu cục bộ.

## Tệp liên quan

- [Taint flow, nguồn và điểm nhận](02-taint-flow-sources-sinks.md)
- [Nguyên nhân gốc rễ và API không an toàn](03-root-causes-and-insecure-apis.md)
- [Phòng thủ và giảm thiểu](14-defense-mitigation.md)
