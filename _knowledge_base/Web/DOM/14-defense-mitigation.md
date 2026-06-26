# Phòng thủ và giảm thiểu lỗ hổng dựa trên DOM

## Nguyên tắc cốt lõi

Không cho dữ liệu không đáng tin cậy đi động tới các sink nguy hiểm.

Không có một biện pháp duy nhất áp dụng cho mọi tình huống. Kiểm soát phải được triển khai theo từng loại sink và từng ngữ cảnh thực thi.

## Các lớp phòng thủ

| Lớp                     | Mục tiêu                      | Kiểm soát điển hình                                                        |
| ----------------------- | ----------------------------- | -------------------------------------------------------------------------- |
| Kiểm soát nguồn dữ liệu | Giảm rủi ro dữ liệu nhiễm bẩn | Kiểm tra danh sách cho phép chặt, ràng buộc lược đồ                        |
| Kiểm soát luồng         | Ngăn lan truyền không an toàn | Tách ranh giới tin cậy/không tin cậy rõ ràng                               |
| Gia cố điểm nhận        | Chặn đường khai thác          | API an toàn hơn, cơ chế bảo vệ theo từng điểm nhận, chặn protocol rủi ro   |
| Xác minh thời gian chạy | Bắt lỗi hồi quy               | Kiểm thử bảo mật, rà soát luồng dữ liệu, kiểm thử theo ma trận trình duyệt |

## Hướng dẫn gia cố ở mức API

1. Ưu tiên API DOM an toàn dạng text thay cho API tiêm HTML.
2. Cấm API thực thi mã từ chuỗi khi dữ liệu đầu vào không đáng tin cậy.
3. Bắt buộc kiểm tra origin nghiêm ngặt cho kênh messaging.
4. Bắt buộc danh sách cho phép đích điều hướng cho chuyển hướng và liên kết.
5. Không cho ghi cookie/storage từ dữ liệu không đáng tin cậy trong các luồng quan trọng.

## Biến đổi dữ liệu theo đúng ngữ cảnh

Khi nghiệp vụ bắt buộc render động, phải áp đúng thứ tự biến đổi theo ngữ cảnh điểm nhận. Tùy ngữ cảnh có thể cần kết hợp:

1. URL encoding
2. HTML encoding/sanitization
3. JavaScript escaping

Thứ tự chính xác phụ thuộc ngữ cảnh và phải được kiểm thử trong thời gian chạy thực tế.

## Kiểm soát riêng cho DOM clobbering

1. Tránh mẫu fallback global tin trực tiếp giá trị trong `window` namespace.
2. Kiểm tra kiểu đối tượng/hàm mong đợi trước khi truy cập thuộc tính.
3. Dùng thư viện sanitize đã tính tới kịch bản DOM clobbering.

## Gia cố parser/query phía client

1. Dùng truy vấn tham số hóa cho SQL API phía client khi có thể.
2. Áp kiểm tra lược đồ nghiêm ngặt trước khi phân tích JSON.
3. Tránh nối giá trị không đáng tin cậy vào biểu thức XPath.

## Kiểm soát vận hành

1. Bổ sung kiểm tra source-to-sink pattern trong code review.
2. Thêm regression test cho các nhóm sink quan trọng.
3. Audit sink usage của thư viện bên thứ ba sau mỗi lần nâng phiên bản.
4. Duy trì playbook lỗ hổng và chương trình huấn luyện qua lab.

## Checklist phòng thủ

1. Mọi source đã được coi mặc định là không đáng tin cậy chưa?
2. Các sink nguy hiểm đã được liệt kê và bảo vệ chưa?
3. Đích redirect/message đã bị giới hạn bằng allowlist rõ ràng chưa?
4. Việc ghi cookie/storage đã được kiểm soát và kiểm tra chưa?
5. Bộ kiểm thử hiện tại có xác minh hành vi thời gian chạy, không chỉ mã tĩnh không?

## Tệp liên quan

- [Nguyên nhân gốc rễ và API không an toàn](03-root-causes-and-insecure-apis.md)
- [Quy trình khai thác](13-exploitation-workflows.md)
- [Kịch bản lab và huấn luyện agent](15-labs-and-agent-training-scenarios.md)
