# Kịch bản lab và huấn luyện agent (WebSocket)

## Mục tiêu

Cung cấp bộ kịch bản thực hành từ cơ bản đến nâng cao để đào tạo pentester và agent bảo mật cho hệ thống real-time.

## Kịch bản 1. Nhận diện handshake và endpoint

Mục tiêu học tập:

1. Phát hiện endpoint WebSocket trong một ứng dụng web hoàn chỉnh.
2. Thu thập đầy đủ thông tin handshake quan trọng.
3. Phân biệt auth ở HTTP và auth ở WebSocket.

## Kịch bản 2. Kiểm thử origin policy và CSWSH

Mục tiêu học tập:

1. Xác định origin policy thực tế của server.
2. Kiểm thử khả năng mở socket từ origin không tin cậy trong lab.
3. Đánh giá impact khi session cookie bị tái sử dụng.

## Kịch bản 3. Message schema tampering

Mục tiêu học tập:

1. Mô hình hóa message contract.
2. Thử type/structure mutation để tìm validate bypass.
3. Ghi nhận rõ phản hồi và side effect.

## Kịch bản 4. Authorization theo action

Mục tiêu học tập:

1. So sánh quyền UI với quyền thực thi message-level.
2. Kiểm thử horizontal/vertical authorization bypass.
3. Viết báo cáo dựa trên impact nghiệp vụ.

## Kịch bản 5. Race condition trong luồng real-time

Mục tiêu học tập:

1. Xác định hành động có nguy cơ race cao.
2. Dùng nhiều kết nối song song để kiểm thử.
3. Chứng minh vi phạm invariant nghiệp vụ.

## Kịch bản 6. DoS có kiểm soát

Mục tiêu học tập:

1. Thiết kế bài test tải tăng dần an toàn.
2. Xác định ngưỡng fail của hệ thống.
3. Đề xuất ngưỡng quota/rate-limit thực tế.

## Rubric đánh giá

| Tiêu chí               | Mô tả                                              |
| ---------------------- | -------------------------------------------------- |
| Độ đúng kỹ thuật       | Mô tả đúng protocol, state, điều kiện khai thác    |
| Tính tái hiện          | Người khác tái lập được theo tài liệu              |
| Chất lượng bằng chứng  | Có transcript, trạng thái trước/sau, log tương ứng |
| Chất lượng khuyến nghị | Bám nguyên nhân gốc và khả thi triển khai          |
| An toàn vận hành       | Không vượt phạm vi, có kiểm soát rủi ro test       |

## Prompt mẫu cho huấn luyện agent

1. "Từ transcript handshake và message, hãy lập bản đồ action và quyền theo vai trò."
2. "Đề xuất workflow kiểm thử CSWSH cho môi trường lab, nêu rõ precondition và expected evidence."
3. "Với một action tài chính real-time, hãy xây test plan phát hiện race condition và cách xác nhận impact."
4. "Từ các phát hiện đã có, tạo kế hoạch hardening ưu tiên theo mức rủi ro và effort."

## Lưu ý triển khai lab

1. Tách biệt hoàn toàn với production.
2. Dữ liệu thử nghiệm không chứa thông tin thật.
3. Có cơ chế reset trạng thái nhanh giữa các vòng test.
4. Định nghĩa rõ phạm vi và quyền kiểm thử trước khi chạy.

## Tệp liên quan

- [Workflow khai thác](11-exploitation-workflows.md)
- [Cheatsheet payload và kiểm thử](12-payloads-and-testing-cheatsheet.md)
- [Phòng thủ và giảm thiểu](13-defense-mitigation.md)
- [Ánh xạ nguồn tham chiếu](15-reference-mapping.md)
