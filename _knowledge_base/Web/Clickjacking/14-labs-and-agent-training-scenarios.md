# Kịch bản lab và huấn luyện agent

## Mục tiêu

Cung cấp bộ kịch bản thực hành clickjacking theo mức độ từ cơ bản đến nâng cao, phục vụ đào tạo pentester và AI agent bảo mật.

## Kịch bản 1. Nhúng khung cơ bản

Mục tiêu học tập:

1. Xác định endpoint thiếu policy chống framing.
2. Dựng PoC iframe + mồi nhấp cơ bản.
3. Chứng minh sự khác biệt giữa “nhúng được” và “khai thác được”.

## Kịch bản 2. Căn chỉnh một cú nhấp nhạy cảm

Mục tiêu học tập:

1. Căn tọa độ control mục tiêu theo viewport cố định.
2. Tái hiện side effect ngoài ý muốn.
3. Ghi nhận bằng chứng tái hiện ở mức báo cáo.

## Kịch bản 3. Prefill + submit

Mục tiêu học tập:

1. Nhận diện endpoint nhận dữ liệu từ URL.
2. Kết hợp payload điền sẵn với clickjacking.
3. Đánh giá tác động khi dữ liệu do attacker áp đặt.

## Kịch bản 4. Luồng nhiều bước

Mục tiêu học tập:

1. Mô hình hóa chuỗi nhiều tương tác người dùng.
2. Điều phối lớp mồi theo chuyển trạng thái UI.
3. Đo độ ổn định theo thời gian và lỗi lệch căn chỉnh.

## Kịch bản 5. Đánh giá bypass frame-buster

Mục tiêu học tập:

1. So sánh phòng thủ phía client và phía máy chủ.
2. Thực nghiệm bypass trong môi trường sandbox kiểm soát.
3. Rút ra giới hạn của phòng thủ chỉ dựa vào JavaScript.

## Kịch bản 6. Chuỗi tấn công đa lỗ hổng

Mục tiêu học tập:

1. Kết hợp clickjacking với lỗ hổng kế tiếp (ví dụ lỗi tiêm script).
2. Mô tả tác động dây chuyền theo ngôn ngữ kinh doanh.
3. Viết khuyến nghị phòng thủ đa lớp theo nguyên nhân gốc.

## Rubric đánh giá

| Tiêu chí | Mô tả |
| --- | --- |
| Độ đúng kỹ thuật | Chuỗi tấn công và precondition được mô tả chính xác |
| Tính tái hiện | Người khác có thể lặp lại PoC theo tài liệu |
| Chất lượng bằng chứng | Có header, PoC, side effect rõ ràng |
| Chất lượng giảm thiểu | Khuyến nghị bám nguyên nhân và khả thi triển khai |
| An toàn vận hành | Tuân thủ phạm vi được ủy quyền |

## Prompt gợi ý cho agent huấn luyện

1. “Hãy xác định endpoint có nguy cơ clickjacking cao nhất và giải thích vì sao.”
2. “Từ endpoint đã chọn, dựng workflow kiểm thử có thể lặp lại.”
3. “Đề xuất kế hoạch giảm thiểu theo thứ tự ưu tiên và effort triển khai.”

## Lưu ý triển khai lab

1. Tách biệt hoàn toàn với hệ thống production.
2. Dùng dữ liệu mô phỏng, không dùng tài khoản thật.
3. Ghi rõ luật phạm vi và điều kiện cấp quyền trước khi thực hành.

## Tệp liên quan

- [Workflow khai thác](11-exploitation-workflows.md)
- [Phòng thủ và giảm thiểu](13-defense-mitigation.md)
- [Ánh xạ tài liệu tham chiếu](15-reference-mapping.md)
