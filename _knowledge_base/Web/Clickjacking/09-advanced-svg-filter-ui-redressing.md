# UI redressing nâng cao bằng SVG filter

## Mục tiêu

Tài liệu hóa các kỹ thuật thao túng hình ảnh hiện đại liên quan clickjacking để phục vụ phòng thủ, threat modeling và thiết kế lab.

## Ý tưởng mức cao

Một số phiên bản trình duyệt hiện đại cho phép pipeline filter hình ảnh (ví dụ SVG `filter:url(#id)`) tác động lên pixel đã render của iframe cross-origin mà không cần truy cập DOM.

Điều này mở rộng clickjacking cổ điển “nút ẩn” sang dạng UI redressing phong phú hơn.

## Khác biệt so với clickjacking cơ bản

Clickjacking cơ bản:

1. Ẩn khung mục tiêu và căn tọa độ nhấp.

UI redressing điều khiển bằng filter:

1. Bóp méo, tạo mask hoặc biến đổi pixel người dùng nhìn thấy.
2. Đặt lại ngữ cảnh để người dùng hiểu sai giao diện thật.
3. Dẫn hướng tương tác theo tín hiệu trạng thái thị giác.

## Các họ primitive thường gặp (theo nghiên cứu công khai)

1. Bóp méo pixel (`feDisplacementMap`, pipeline nhiễu/turbulence).
2. Toán tử tương phản/ngưỡng (`feComposite operator="arithmetic"`, color transform).
3. Cắt-và-khuếch đại vùng (`feTile`) để phóng đại vùng pixel chọn lọc.
4. Biến đổi hình thái (`feMorphology`) để nở/co nét.

## Hàm ý bảo mật

1. Nạn nhân có thể bị dẫn qua workflow nhạy cảm trong khi giao diện nhìn thấy đã bị thao túng.
2. Dò trạng thái theo pixel giúp attacker đồng bộ tốt hơn với chuyển trạng thái UI mục tiêu.
3. Giả định “chỉ iframe vô hình” là quá hẹp trước kỹ thuật mới.

## Ràng buộc thực tế

| Ràng buộc | Tác động |
| --- | --- |
| Khác biệt trình duyệt/phiên bản | Độ ổn định kỹ thuật thay đổi đáng kể |
| Khác biệt pipeline render | Kết quả filter và căn chỉnh có thể lệch |
| Chi phí hiệu năng | Pipeline phức tạp dễ để lộ bất thường |
| Header phòng thủ + kiểm soát UX | Vẫn giúp giảm tác động kinh doanh trong thực tế |

## Khuyến nghị phòng thủ

1. Xem UI redressing là lớp rủi ro rộng, không chỉ overlay opacity.
2. Ưu tiên chặn framing mạnh cho luồng nhạy cảm.
3. Thêm transaction binding và re-auth cho thao tác rủi ro cao.
4. Kiểm thử theo ma trận trình duyệt thực tế và điều kiện UI đối kháng.

## Gợi ý thiết kế lab

Chỉ mô phỏng các tình huống nâng cao này trong môi trường kiểm soát, có cấp quyền rõ ràng và cách ly đầy đủ.

## Tệp liên quan

- [DoubleClickjacking và biến thể Popup](07-doubleclickjacking-and-popup-variants.md)
- [Chuỗi tấn công và mô hình hóa tác động](10-attack-chains-and-impact-modeling.md)
- [Phòng thủ và giảm thiểu](13-defense-mitigation.md)
