# Chuyển hướng mở và thao túng liên kết dựa trên DOM

## Chuyển hướng mở dựa trên DOM

### Định nghĩa

Chuyển hướng mở dựa trên DOM xảy ra khi dữ liệu phía client do attacker kiểm soát bị ghi vào điểm nhận điều hướng, khiến trình duyệt chuyển hướng sang domain không tin cậy.

### Logic dễ lỗi điển hình

```javascript
const url = /https?:\/\/.+/.exec(location.hash);
if (url) {
  location = url[0];
}
```

### Tác động

1. Chiến dịch phishing tăng độ tin cậy vì bắt đầu từ domain hợp lệ.
2. Người dùng có thể bị chuyển hướng âm thầm sang hạ tầng của attacker.
3. Trong một số tình huống, có thể leo thang thành thực thi script qua vector kiểu `javascript:`.

### Các điểm nhận chính

- `location`
- `location.assign()`
- `location.replace()`
- `open()`
- `location.href`, `location.protocol` và các trường location liên quan
- `element.srcdoc`
- `XMLHttpRequest.open()` / `send()`
- `jQuery.ajax()` / `$.ajax()`

## Thao túng liên kết dựa trên DOM

### Định nghĩa

Thao túng liên kết xuất hiện khi dữ liệu đầu vào do attacker kiểm soát ghi đè đích điều hướng trong trang, form action hoặc URL tài nguyên.

### Các điểm nhận chính

- `element.href`
- `element.src`
- `element.action`

### Mẫu tác động

1. Người dùng bấm vào link trông hợp lệ nhưng bị chuyển tới đích do attacker kiểm soát.
2. Dữ liệu form nhạy cảm bị gửi sang endpoint của attacker.
3. Link nội bộ bị sửa để kích hoạt hành động ngoài ý muốn trong ứng dụng.

## Chuỗi khai thác

```text
1. Xác định nguồn dữ liệu điều khiển giá trị URL đích
2. Xác nhận dữ liệu được ghi vào điểm nhận điều hướng/liên kết
3. Tạo payload với đích do attacker kiểm soát
4. Kích hoạt tương tác người dùng hoặc điều hướng tự động
5. Xác minh tác động chuyển hướng hoặc rò rỉ dữ liệu
```

## Trọng tâm giảm thiểu

1. Không đặt đích redirect/link trực tiếp từ dữ liệu không đáng tin cậy.
2. Áp danh sách cho phép chặt cho protocol, host và mẫu đường dẫn.
3. Chặn các scheme rủi ro (`javascript:`, `data:` nếu không thực sự cần).
4. Tách giá trị hiển thị khỏi giá trị đích điều hướng trong logic UI.

## Tệp liên quan

- [Taint flow, nguồn và điểm nhận](02-taint-flow-sources-sinks.md)
- [Phát hiện và phân tích luồng dữ liệu](04-detection-and-dataflow-analysis.md)
- [Quy trình khai thác](13-exploitation-workflows.md)
- [Phòng thủ và giảm thiểu](14-defense-mitigation.md)
