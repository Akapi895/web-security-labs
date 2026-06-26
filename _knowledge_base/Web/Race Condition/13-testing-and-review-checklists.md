# Testing and Review Checklists

## A. Pentest Execution Checklist

1. Đã xác định endpoint nhạy cảm theo business impact chưa?
2. Đã chứng minh collision potential trên cùng resource key chưa?
3. Đã benchmark sequential làm baseline chưa?
4. Đã chạy parallel với chiến lược đồng bộ phù hợp giao thức chưa?
5. Đã quan sát side effects ngoài response (email, state, logs) chưa?
6. Đã thu hẹp PoC tối thiểu và tái lập nhiều lần chưa?
7. Đã mô tả invariant bị phá bằng ngôn ngữ nghiệp vụ chưa?

## B. Code Review Checklist (Developer/Security Reviewer)

1. Có đoạn check-then-update nào không nằm trong transaction không?
2. Có shared state nào được ghi bởi nhiều endpoint mà không có lock/version control không?
3. Session có đang giữ logic bảo mật thay cho datastore không?
4. Async worker có đọc mutable state thay vì snapshot đã commit không?
5. Token reset/verify có CSPRNG và one-time atomic consume không?
6. Có ràng buộc DB hỗ trợ invariant chính không?

## C. Validation Checklist for Report Quality

1. Có request/response mẫu cho baseline và exploit run.
2. Có mô tả điều kiện race window rõ ràng.
3. Có bằng chứng state trước/sau.
4. Có ước lượng tỷ lệ thành công theo số vòng thử.
5. Có khuyến nghị fix cụ thể ở mức thiết kế và triển khai.

## D. Lab QA Checklist

1. Lab reset được về trạng thái sạch.
2. Có ít nhất một chiến lược khả thi để khai thác.
3. Không phụ thuộc quá mức vào may mắn ngẫu nhiên.
4. Có quan sát được vì sao thất bại khi timing sai.
5. Flag thành công phản ánh đúng business impact.

## E. Agent Evaluation Checklist

1. Agent có phân loại đúng pattern race không?
2. Agent có nhận diện đúng shared resource key không?
3. Agent có chọn công cụ/kỹ thuật gửi song song phù hợp không?
4. Agent có tách được tín hiệu thật và nhiễu timing không?
5. Agent có đề xuất mitigation đúng gốc nguyên nhân không?

## Risk Rating Hints

| Indicator                                 | Suggested Severity Direction |
| ----------------------------------------- | ---------------------------- |
| Ảnh hưởng trực tiếp tiền/quyền admin      | High/Critical                |
| Chỉ gây bất nhất nhẹ, khó tái lập         | Medium                       |
| Chỉ là timing anomaly, chưa phá invariant | Low/Informational            |

## Related Files

- [03-detection-and-scoping](03-detection-and-scoping.md)
- [10-tooling-burp-and-turbo-intruder](10-tooling-burp-and-turbo-intruder.md)
- [12-defense-mitigation](12-defense-mitigation.md)
