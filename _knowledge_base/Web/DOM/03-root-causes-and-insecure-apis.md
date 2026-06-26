# Nguyên nhân gốc rễ và cách dùng API không an toàn

## Vì sao lỗ hổng DOM-based xuất hiện

Lỗi DOM-based thường là lỗi kỹ thuật trong cách xử lý dữ liệu phía client, không phải chỉ là vấn đề payload đơn lẻ.

Mẫu thất bại cốt lõi là: dữ liệu không đáng tin cậy bị coi là an toàn quá sớm.

## Các nguyên nhân chính

1. Dùng API không an toàn với dữ liệu không đáng tin cậy.
2. Thiếu hoặc yếu ở bước kiểm tra/làm sạch phía client.
3. Lỗi logic trong xử lý URL/fragment/referrer/message.
4. Mẫu fallback không an toàn với biến toàn cục và thuộc tính đối tượng.
5. Sink ẩn trong thư viện/framework bên thứ ba.

## API rủi ro và hướng an toàn hơn

| API/mẫu rủi ro                                         | Rủi ro điển hình                               | Hướng an toàn hơn                                                                      |
| ------------------------------------------------------ | ---------------------------------------------- | -------------------------------------------------------------------------------------- |
| `element.innerHTML`, `outerHTML`, `insertAdjacentHTML` | Ngữ cảnh tiêm HTML/script                      | Ưu tiên API dạng text (`textContent`) và sanitize nghiêm ngặt khi bắt buộc render HTML |
| `document.write()`                                     | Ghi trực tiếp vào luồng parser                 | Tránh dùng với dữ liệu động không đáng tin cậy                                         |
| `eval()`, `Function()`, timer dạng chuỗi               | Thực thi JavaScript tùy ý                      | Dùng callback cấu trúc rõ ràng, không thực thi chuỗi                                   |
| `location = value`, `open(value)`                      | Open redirect hoặc lạm dụng `javascript:`      | Áp danh sách cho phép chặt cho đích điều hướng                                         |
| `document.cookie = ...`                                | Đầu độc cookie, session fixation chain         | Tránh ghi cookie từ nguồn dữ liệu không tin cậy; kiểm tra chặt định dạng               |
| `postMessage(data, '*')`                               | Lạm dụng message và nhầm lẫn ranh giới tin cậy | Chỉ định rõ target origin và kiểm tra chặt ở phía nhận                                 |
| `setAttribute()` trên thuộc tính nhạy cảm              | Thao túng trạng thái DOM                       | Hạn chế thuộc tính được phép ghi và kiểm tra theo lược đồ                              |

## Lỗi logic trong xử lý URL

Sai lầm thường gặp:

1. Tin `location.hash` hoặc `location.search` chỉ sau kiểm tra hời hợt.
2. Giả định dữ liệu đã URL-encode thì luôn vô hại trên mọi trình duyệt.
3. Nối trực tiếp dữ liệu URL vào tham số sink.

## Sai lầm ghép nguồn-điểm nhận

Mẫu anti-pattern điển hình:

```javascript
const data = source();
sink(data);
```

Đây là thiếu kiểm soát nếu mã không bắt buộc:

1. Ràng buộc giá trị theo lược đồ danh sách cho phép.
2. Encode/sanitize đúng theo ngữ cảnh.
3. Chốt kiểm tra an toàn riêng cho từng loại điểm nhận.

## Rủi ro từ dependency bên thứ ba

Ngay cả khi mã nội bộ có vẻ an toàn, API của thư viện vẫn có thể là điểm nhận, ví dụ:

- Hàm set thuộc tính của jQuery cho các thuộc tính điều hướng.
- Các helper selector và DOM construction trong mẫu cũ.
- Cơ chế parse expression của framework trong ngữ cảnh template không an toàn.

## Tệp liên quan

- [Taint flow, nguồn và điểm nhận](02-taint-flow-sources-sinks.md)
- [Phát hiện và phân tích luồng dữ liệu](04-detection-and-dataflow-analysis.md)
- [DOM clobbering](06-dom-clobbering.md)
- [Phòng thủ và giảm thiểu](14-defense-mitigation.md)
