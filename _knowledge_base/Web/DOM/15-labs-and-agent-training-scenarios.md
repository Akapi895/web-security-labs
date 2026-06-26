# Kịch bản lab và huấn luyện agent

## Mục tiêu

Cung cấp các kịch bản tăng dần độ khó, có thể tái hiện, để học phân tích và khai thác lỗ hổng DOM-based trong môi trường được ủy quyền.

## Kịch bản 1: Cơ bản về lập bản đồ nguồn-điểm nhận

Mục tiêu học:

1. Liệt kê nguồn dữ liệu phía trình duyệt trên một trang mục tiêu.
2. Nhận diện điểm nhận nguy hiểm bằng cả phân tích tĩnh và thời gian chạy.
3. Viết báo cáo dấu vết nguồn-điểm nhận đầu tiên.

## Kịch bản 2: DOM XSS trong HTML sink

Mục tiêu học:

1. Xác minh marker được phản chiếu trong DOM thời gian chạy.
2. Xác định đúng ngữ cảnh điểm nhận (`innerHTML` hoặc `document.write`).
3. Xây payload đúng ngữ cảnh và xác minh thực thi.

## Kịch bản 3: DOM clobbering dưới bộ lọc HTML

Mục tiêu học:

1. Khai thác va chạm `id`/`name` để ghi đè thuộc tính đối tượng.
2. Chứng minh thay đổi hành vi mà không cần script-tag injection cổ điển.
3. Giải thích vì sao mẫu fallback object là không an toàn.

## Kịch bản 4: Redirect và link manipulation

Mục tiêu học:

1. Theo dõi luồng gán đích điều hướng do nguồn dữ liệu điều khiển.
2. Tái hiện open redirect và sửa link ngay trong trang.
3. Mô hình hóa tác động phishing/chuyển hướng dữ liệu.

## Kịch bản 5: Cookie/storage chaining

Mục tiêu học:

1. Đầu độc cookie hoặc storage qua sink ghi phía DOM.
2. Tìm điểm vỡ ranh giới tin cậy ở luồng đọc về sau.
3. Chứng minh tác động chain tới hành vi mức nghiêm trọng hơn.

## Kịch bản 6: Parser/query injection và lạm dụng logic client

Mục tiêu học:

1. Kiểm thử các điểm nhận parser/truy vấn (`executeSql`, `evaluate`, `JSON.parse`).
2. Chứng minh thao túng logic bằng dữ liệu attacker bị định dạng sai.
3. Đề xuất biện pháp giảm thiểu theo đúng ngữ cảnh.

## Rubric đánh giá

| Tiêu chí                | Mô tả                                                     |
| ----------------------- | --------------------------------------------------------- |
| Độ đúng kỹ thuật        | Nguồn dữ liệu, điểm nhận và luồng được xác định chính xác |
| Tính tái hiện           | Người kiểm thử khác có thể tái hiện từ hướng dẫn          |
| Chất lượng tác động     | Chứng minh hệ quả bảo mật thực, không chỉ dấu hiệu mùi mã |
| Chất lượng giảm thiểu   | Khuyến nghị khớp nguyên nhân gốc và ngữ cảnh sink         |
| Kỷ luật an toàn/phạm vi | Kiểm thử luôn nằm trong phạm vi được ủy quyền             |

## Prompt huấn luyện agent

1. "Hãy lập bản đồ toàn bộ nguồn dữ liệu không đáng tin cậy và điểm nhận rủi ro của trang này."
2. "Hãy tạo dấu vết nguồn-điểm nhận theo từng bước kèm điểm bằng chứng."
3. "Hãy đề xuất kế hoạch giảm thiểu theo thứ tự ưu tiên khả năng khai thác và mức độ tác động."

## Lưu ý vận hành lab

1. Dùng môi trường cô lập và dữ liệu mô phỏng.
2. Luôn ghi chú phiên bản trình duyệt vì hành vi có thể khác nhau theo engine.
3. Thu thập bằng chứng thời gian chạy (dấu vết debugger, trạng thái DOM, hiệu ứng phụ request/response).

## Tệp liên quan

- [Phát hiện và phân tích luồng dữ liệu](04-detection-and-dataflow-analysis.md)
- [Quy trình khai thác](13-exploitation-workflows.md)
- [Phòng thủ và giảm thiểu](14-defense-mitigation.md)
