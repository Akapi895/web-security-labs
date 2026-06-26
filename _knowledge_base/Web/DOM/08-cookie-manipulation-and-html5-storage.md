# Thao túng cookie và lưu trữ HTML5 dựa trên DOM

## Thao túng cookie dựa trên DOM

### Định nghĩa

Thao túng cookie xảy ra khi script phía client ghi dữ liệu do attacker kiểm soát vào `document.cookie`.

Mẫu dễ lỗi điển hình:

```javascript
document.cookie = "cookieName=" + location.hash.slice(1);
```

### Vì sao nguy hiểm

Riêng thao tác ghi cookie có thể trông như mức thấp. Nhưng trong hệ thống thực tế, nó có thể trở thành chuỗi tác động cao:

1. Đầu độc cookie điều khiển hành vi nghiệp vụ.
2. Ép session fixation khi session token bị xử lý sai.
3. Cấp dữ liệu đầu vào cho các luồng phản chiếu server/client không an toàn đang tin nội dung cookie.

### Điểm nhận

- `document.cookie`

## Thao túng lưu trữ HTML5 dựa trên DOM

### Định nghĩa

HTML5 storage manipulation xảy ra khi dữ liệu do attacker kiểm soát được lưu vào `localStorage` hoặc `sessionStorage` bởi script phía client.

### Các điểm nhận

- `sessionStorage.setItem()`
- `localStorage.setItem()`

### Vai trò an ninh

Việc ghi storage thường là vấn đề giai đoạn đầu. Tác động thật xuất hiện khi mã ở bước sau đọc giá trị đã bị đầu độc rồi đưa vào điểm nhận nhạy cảm (ví dụ điểm nhận HTML hoặc điểm nhận thực thi script).

## Góc nhìn chuỗi khai thác

```text
Nguồn dữ liệu -> ghi cookie/storage -> mã tin cậy đọc lại -> điểm nhận nguy hiểm
```

Tính chất trễ của chuỗi này thường che giấu rủi ro khi chỉ kiểm thử bề mặt.

## Trọng tâm giảm thiểu

1. Không ghi dữ liệu không đáng tin cậy vào cookie/storage nếu không thật sự cần.
2. Kiểm tra định dạng và áp danh sách cho phép trước khi lưu.
3. Mọi dữ liệu đọc từ cookie/storage phải coi là không đáng tin cậy nếu chưa được xác thực mật mã.
4. Tách dữ liệu cache không tin cậy khỏi trạng thái thời gian chạy quan trọng về bảo mật.

## Tệp liên quan

- [Taint flow, nguồn và điểm nhận](02-taint-flow-sources-sinks.md)
- [DOM XSS](05-dom-xss.md)
- [Thao túng dữ liệu DOM và DoS dựa trên DOM](12-dom-data-manipulation-and-dos.md)
- [Phòng thủ và giảm thiểu](14-defense-mitigation.md)
