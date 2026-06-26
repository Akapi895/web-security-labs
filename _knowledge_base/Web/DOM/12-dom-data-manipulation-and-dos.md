# Thao túng dữ liệu DOM và từ chối dịch vụ dựa trên DOM

## Thao túng dữ liệu DOM

### Định nghĩa

Dữ liệu do attacker kiểm soát được ghi vào các trường DOM ảnh hưởng trực tiếp đến UI hiển thị hoặc logic phía client.

### Các điểm nhận thường gặp

- `script.src`, `script.text`, `script.textContent`, `script.innerText`
- `element.setAttribute()`, `element.value`, `element.name`, `element.target`, `element.method`, `element.type`
- `element.textContent`, `element.innerText`, `element.outerText`
- `element.search`, `element.backgroundImage`, `element.cssText`, `element.codebase`
- `document.title`
- `document.implementation.createHTMLDocument()`
- `history.pushState()`, `history.replaceState()`

### Tác động

1. Thay đổi giao diện ảo và tạo UI đánh lừa.
2. Tải tài nguyên độc hại qua thuộc tính đã bị ghi đè.
3. Lạm dụng logic bằng cách thao túng trường trạng thái phía client.

## Từ chối dịch vụ dựa trên DOM

### Định nghĩa

Dữ liệu không đáng tin cậy được đưa vào các API nền tảng dễ gây tiêu tốn tài nguyên trình duyệt.

### Các điểm nhận chính

- `requestFileSystem()`
- `RegExp()`

### Tác động

1. Trình duyệt chậm, treo script hoặc tự dừng xử lý.
2. Phát sinh hiệu ứng phụ như chặn thao tác lưu trữ do cạn tài nguyên.

## Hướng dẫn kiểm tra và phân loại

Phân tích tĩnh có thể báo thao túng dữ liệu DOM nhưng chưa chắc khai thác được ngoài thực tế. Luôn xác minh theo đường thực thi thời gian chạy, lớp kiểm soát hiện có và mức kiểm soát thực tế của attacker.

## Trọng tâm giảm thiểu

1. Hạn chế trường DOM có thể ghi từ dữ liệu không đáng tin cậy.
2. Áp schema giá trị chặt cho thuộc tính và cập nhật trạng thái.
3. Chặn gọi API rủi ro khi input bị nhiễm bẩn.
4. Bổ sung cơ chế bảo vệ phía client cho các mẫu input bất thường gây quá tải.

## Tệp liên quan

- [Phát hiện và phân tích luồng dữ liệu](04-detection-and-dataflow-analysis.md)
- [Quy trình khai thác](13-exploitation-workflows.md)
- [Phòng thủ và giảm thiểu](14-defense-mitigation.md)
