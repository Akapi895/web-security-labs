# Tổng quan Clickjacking

## Định nghĩa

Clickjacking (còn gọi là UI redressing) là kỹ thuật tấn công ở lớp giao diện, trong đó attacker lừa người dùng nhấp vào một thành phần có thể thao tác nhưng đang bị ẩn hoặc ngụy trang từ một origin khác.

Thay vì nhấp vào nội dung họ nhìn thấy trên trang mồi, người dùng thực tế lại tương tác với nội dung mục tiêu bị che giấu, thường được tải thông qua iframe.

## Ý tưởng cốt lõi

Clickjacking khai thác cách trình duyệt render và xử lý tương tác:

1. Trình duyệt render nhiều lớp giao diện.
2. Một trang mục tiêu nhạy cảm được nhúng và làm mờ/ẩn về mặt thị giác.
3. UI mồi được đặt để thu hút thao tác nhấp.
4. Input của người dùng được chuyển tới lớp ẩn theo tọa độ do attacker chọn.

## Tại sao quan trọng

| Thuộc tính an ninh | Tác động điển hình |
| --- | --- |
| Toàn vẹn | Thực hiện nhấp trái phép lên hành động thay đổi trạng thái |
| Bảo mật thông tin | Có thể kết hợp mẹo UI để làm lộ hoặc tái ngữ cảnh dữ liệu nhạy cảm |
| Xác thực / Phiên | Tái sử dụng phiên đăng nhập của nạn nhân để thực hiện hành động ngoài ý muốn |
| Rủi ro kinh doanh | Duyệt hành động gian lận, đổi thông tin tài khoản, thao túng hành vi xã hội, lạm dụng consent |

## Clickjacking và CSRF

| Khía cạnh | Clickjacking | CSRF |
| --- | --- | --- |
| Tương tác người dùng | Thường cần (nhấp/cử chỉ) | Thường không cần |
| Cơ chế chính | Lừa giao diện + bề mặt thao tác bị ẩn | Giả mạo yêu cầu liên trang |
| Hiệu quả của CSRF token | Thường không đủ nếu đứng một mình | Thường là lớp giảm thiểu cốt lõi |
| Bối cảnh trình duyệt | Tương tác hợp lệ trong phiên thật nhưng nằm trong khung ẩn | Yêu cầu cross-origin bị giả mạo |

## Các họ kỹ thuật chính

1. Clickjacking cơ bản với iframe ẩn.
2. Clickjacking form điền sẵn (attacker kiểm soát input qua URL).
3. Clickjacking nhiều bước (chuỗi các cú nhấp được căn chỉnh).
4. Biến thể có cử chỉ hỗ trợ (ví dụ kéo-thả + nhấp).
5. Biến thể dựa trên thời điểm (double-clickjacking).
6. Biến đổi hình ảnh nâng cao (ví dụ filter-based UI distortion).

## Vòng đời tấn công (mức cao)

```text
1. MAP       -> Xác định endpoint có thể bị nhúng và hành động UI nhạy cảm
2. ALIGN     -> Chồng lớp điều khiển mục tiêu ẩn với phần tử mồi
3. BAIT      -> Điều hướng tương tác người dùng (nhấp/kéo-thả/nhấp đúp)
4. TRIGGER   -> Hành động của nạn nhân được thực thi trên origin mục tiêu
5. CHAIN     -> Kết hợp với XSS/OAuth/lỗi UX để tăng tác động
```

## Phòng thủ trong một cái nhìn

1. Chặn nhúng khung trái phép từ phía máy chủ (`CSP frame-ancestors`, kèm `X-Frame-Options` để tương thích).
2. Giảm các hành động nhạy cảm kiểu một cú nhấp bằng bước xác nhận/reauth.
3. Dùng cookie `SameSite` khi phù hợp để giảm khả năng lạm dụng phiên liên trang.
4. Giữ frame-busting phía client như lớp bổ trợ, không phải lớp chính.

## Lưu ý phạm vi

Bộ kiến thức này phục vụ nghiên cứu phòng thủ, pentest có ủy quyền và xây dựng lab huấn luyện.

## Tệp liên quan

- [Nền tảng UI Redressing trên Trình duyệt](01-browser-ui-redressing-fundamentals.md)
- [Primitives tấn công: iframe, Layering, Opacity](02-attack-primitives-iframe-layering-opacity.md)
- [Điều kiện và nguyên nhân gốc rễ](03-conditions-and-root-causes.md)
- [Phát hiện và lập bản đồ mục tiêu](04-detection-and-target-mapping.md)
- [Khai thác cơ bản](05-basic-exploitation.md)
- [Prefill, Kéo-thả, Nhiều bước](06-prefill-dragdrop-multistep.md)
- [DoubleClickjacking và biến thể Popup](07-doubleclickjacking-and-popup-variants.md)
- [Frame Buster và bypass phía client](08-frame-buster-and-client-side-bypass.md)
- [UI redressing nâng cao bằng SVG filter](09-advanced-svg-filter-ui-redressing.md)
- [Chuỗi tấn công và mô hình hóa tác động](10-attack-chains-and-impact-modeling.md)
- [Workflow khai thác](11-exploitation-workflows.md)
- [Cheatsheet payload và snippet](12-payloads-cheatsheet.md)
- [Phòng thủ và giảm thiểu](13-defense-mitigation.md)
- [Kịch bản lab và huấn luyện agent](14-labs-and-agent-training-scenarios.md)
- [Ánh xạ nguồn tham chiếu](15-reference-mapping.md)
