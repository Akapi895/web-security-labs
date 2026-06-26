# Chuỗi tấn công và mô hình hóa tác động

## Mục tiêu

Giải thích cách clickjacking khuếch đại tác động khi kết hợp với điểm yếu khác, đồng thời cung cấp khung đánh giá tác động nhất quán.

## Chuỗi A: Clickjacking + Prefill + luồng tiêm script

Pattern thường gặp trong tài liệu huấn luyện:

1. Mục tiêu chấp nhận giá trị form điền sẵn qua URL.
2. Form ẩn bị nhúng được tải với payload do attacker chọn.
3. Nạn nhân bị lừa nhấp submit.
4. Lỗ hổng kế tiếp (ví dụ đường tiêm script) được kích hoạt.

## Chuỗi B: Clickjacking + lạm dụng consent OAuth

1. Nạn nhân đang xác thực tại identity provider hoặc relying party.
2. Màn hình consent có thể bị nhúng hoặc bị dẫn vào luồng UI đã thao túng.
3. Nạn nhân nhấp chấp thuận quyền ngoài ý muốn.

## Chuỗi C: Clickjacking + điểm yếu frame-buster

1. Ứng dụng chủ yếu dựa vào frame-busting phía client.
2. Attacker dùng hành vi sandbox/cửa sổ để vô hiệu hóa phòng vệ kỳ vọng.
3. Hành động nhạy cảm vẫn có thể bị kích hoạt qua thao tác nhấp.

## Chuỗi D: Clickjacking + UI redress ở browser extension

Các công bố thực tế cho thấy dialog/autofill do extension chèn vào trang có thể trở thành bề mặt tấn công nếu tồn tại script injection hoặc overlay UI ở lớp trang.

## Chuỗi E: Clickjacking + phễu social engineering

1. Nội dung mồi đủ mạnh để dẫn hướng thao tác chính xác.
2. Người dùng hoàn tất hành động tưởng như vô hại.
3. Hệ thống mục tiêu thực thi thao tác không thể hoàn tác.

## Các chiều tác động

| Chiều đánh giá | Câu hỏi |
| --- | --- |
| Độ nhạy hành động | Chính xác thao tác nào đang bị chiếm quyền nhấp? |
| Quyền cần có | Vai trò nạn nhân nào là cần thiết? |
| Gánh nặng tương tác | Nhấp đơn, đa nhấp hay phụ thuộc timing? |
| Khả năng bị phát hiện | Nạn nhân có nhận ra ngay không? |
| Khả năng phục hồi | Có rollback được hay tốn kém? |

## Heuristic xếp mức độ nghiêm trọng

Mức cao thường đi kèm:

1. Hành động giá trị cao kiểu một cú nhấp.
2. Luồng người dùng phổ biến, khả năng gặp nạn cao.
3. Mồi lừa ít ma sát.
4. Kiểm soát framing phía máy chủ yếu.

## Cấu trúc báo cáo khuyến nghị

1. Điểm vào của chuỗi tấn công (endpoint có thể bị nhúng).
2. Điều kiện tiên quyết và trạng thái nạn nhân.
3. Chuỗi tương tác cần thiết.
4. Tác động kinh doanh trái phép.
5. Nguyên nhân gốc và biện pháp khắc phục nhiều lớp.

## Tệp liên quan

- [Workflow khai thác](11-exploitation-workflows.md)
- [Phòng thủ và giảm thiểu](13-defense-mitigation.md)
- [Kịch bản lab và huấn luyện agent](14-labs-and-agent-training-scenarios.md)
