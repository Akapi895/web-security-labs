# Multi-endpoint Race Conditions

## Core Idea

Multi-endpoint race xuất hiện khi hai hoặc nhiều endpoint khác nhau cùng thao tác lên một shared resource trong cùng khoảng thời gian, tạo ra trạng thái lệch logic.

## Common Pattern

Một endpoint xác nhận điều kiện, endpoint còn lại thay đổi dữ liệu nền ngay trước khi bước commit diễn ra.

Ví dụ điển hình:

- `POST /cart/checkout` kiểm tra đủ tiền.
- `POST /cart` thêm hàng vào giỏ gần đồng thời.

Nếu thứ tự nội bộ rơi vào race window, hệ thống có thể xác nhận đơn với giá trị không hợp lệ.

## Why This Class Is Harder

1. Mỗi endpoint có độ trễ xử lý khác nhau.
2. Có thể đi qua các pipeline backend khác nhau.
3. Thời gian mở kết nối backend có thể làm lệch cửa sổ race.

## Alignment Challenges

### Network and Architecture Delay

- Khác biệt do thiết lập kết nối backend mới.
- Khác biệt giao thức hoặc đường đi nội bộ.

### Endpoint-specific Processing Delay

- Endpoint A chạy logic nặng hơn endpoint B.
- Cùng gửi song song nhưng không cùng chạm critical section.

## Connection Warming Strategy

Trước khi gửi request chính, gửi một số request "vô hại" để ổn định kết nối backend. Mục tiêu là giảm độ lệch do khởi tạo connection, giúp timing phản ánh đúng logic ứng dụng hơn.

## Exploitation Workflow

1. Chọn hai endpoint có khả năng chạm cùng resource.
2. Benchmark gửi tuần tự để xem endpoint nào chậm/nhanh.
3. Thử warm connection, benchmark lại.
4. Gửi song song cặp endpoint mục tiêu.
5. Quan sát response + state cuối.
6. Tối ưu thứ tự và số lượng request để tăng xác suất.

## Realistic Lab-style Scenario

- Thêm gift card vào giỏ để duy trì credit.
- Chuẩn bị hai request: add jacket và checkout.
- Gửi song song nhiều vòng.
- Khi checkout thành công trong điều kiện bình thường phải thất bại, đã có bằng chứng race.

## Evidence Quality

Bằng chứng mạnh gồm:

- Request/response pair ở cùng phiên thử.
- Trạng thái đơn hàng cuối cùng vi phạm rule (ví dụ insufficient funds nhưng vẫn purchase thành công).
- Khả năng tái lập sau nhiều lần chạy.

## Related Files

- [03-detection-and-scoping](03-detection-and-scoping.md)
- [09-exploitation-workflows](09-exploitation-workflows.md)
- [10-tooling-burp-and-turbo-intruder](10-tooling-burp-and-turbo-intruder.md)
