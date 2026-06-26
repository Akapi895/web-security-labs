# Nền tảng UI Redressing trên Trình duyệt

## Mục tiêu

Giải thích vì sao clickjacking khả thi về mặt kỹ thuật bằng cách liên kết cơ chế render, stacking và định tuyến input của trình duyệt.

## Mô hình render liên quan đến clickjacking

1. HTML + CSS được parse thành cấu trúc có thể render.
2. Trình duyệt dựng các lớp hiển thị theo layout và stacking context.
3. Pixel cuối cùng được vẽ theo thứ tự z-order.
4. Sự kiện con trỏ được hit-test theo hình học render và quy tắc hiển thị.

Clickjacking lạm dụng bước cuối: nếu một thành phần có thể thao tác nhưng bị ẩn/độ mờ thấp nằm đúng tọa độ nhấp, thành phần đó sẽ nhận sự kiện.

## Stacking context và layering

Các thuộc tính thường bị attacker lợi dụng:

| Thuộc tính | Ý nghĩa bảo mật |
| --- | --- |
| `position` | Điều khiển vị trí phần tử để chồng lớp chính xác theo pixel |
| `z-index` | Quyết định lớp nào nằm trên hoặc dưới |
| `opacity` | Che giấu lớp mục tiêu nhưng vẫn giữ khả năng nhận nhấp |
| `width` / `height` | Co giãn vùng điều khiển ẩn để khớp nội dung mồi |
| `overflow` / clipping | Cô lập đúng vùng mục tiêu cần khai thác |

## Vì sao iframe là trung tâm

Attacker không thể đọc DOM cross-origin do same-origin policy, nhưng vẫn có thể:

1. Nhúng trang nạn nhân nếu cơ chế framing cho phép.
2. Đặt khung đó dưới lớp mồi.
3. Dựa vào thao tác nhấp của người dùng để kích hoạt hành động trên origin mục tiêu.

Vì vậy, clickjacking thường là mô hình “write-only” từ góc nhìn attacker: không cần đọc dữ liệu, chỉ cần điều hướng tương tác.

## Opacity và đánh lừa thị giác

Opacity thường được đặt ở mức rất thấp (hoặc 0) để ẩn khung mục tiêu nhưng vẫn nhận tương tác. Một số trình duyệt có heuristic chống khung quá trong suốt, nên attacker thường tinh chỉnh opacity và căn chỉnh để tránh bị phát hiện rõ ràng.

## Tâm lý UI mồi

Thiết lập kỹ thuật thôi là chưa đủ. Tỷ lệ thành công còn phụ thuộc vào việc điều hướng ý định người dùng:

1. Lời kêu gọi hành động rõ ràng (phần thưởng, tiện ích, khẩn cấp).
2. Tập trung thị giác mạnh vào phần tử mồi.
3. Giảm nghi ngờ trong chuỗi thao tác.

Đây là lý do clickjacking vừa là vấn đề trình duyệt/UI, vừa là vấn đề yếu tố con người.

## Loại input ngoài “một cú nhấp”

Clickjacking có thể tận dụng:

1. Một cú nhấp đơn.
2. Chuỗi nhấp nhiều bước.
3. Nhấp đúp theo nhịp thời gian.
4. Cử chỉ kéo-thả.
5. Luồng thao tác bàn phím trong một số bối cảnh UI.

## Kết luận chính

1. Clickjacking không phá SOP, mà lạm dụng cơ chế render và phân phối sự kiện hợp lệ.
2. Cô lập cross-origin không ngăn được tương tác bị che giấu.
3. Chặn nhúng khung trái phép là kiểm soát kỹ thuật quan trọng nhất.

## Tệp liên quan

- [Primitives tấn công: iframe, Layering, Opacity](02-attack-primitives-iframe-layering-opacity.md)
- [Điều kiện và nguyên nhân gốc rễ](03-conditions-and-root-causes.md)
- [Phòng thủ và giảm thiểu](13-defense-mitigation.md)
