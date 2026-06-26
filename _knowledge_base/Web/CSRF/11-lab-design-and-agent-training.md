# CSRF Lab Design and Agent Training Blueprint

## Mục tiêu

Chuẩn hóa cách dựng lab CSRF để:

- Người học đi từ căn bản đến bypass nâng cao.
- Đội pentest có bộ scenario tái lập.
- Agent có bộ bài tập huấn luyện suy luận theo workflow.

## Kiến trúc module gợi ý

```text
CSRF Lab Track
  Module 01 - No defenses
  Module 02 - Token check by method
  Module 03 - Token optional/present-only
  Module 04 - Token not bound to session
  Module 05 - Token tied to non-session cookie
  Module 06 - Weak Referer/Origin checks
  Module 07 - SameSite bypass scenarios
  Module 08 - Login CSRF + stored chain
  Module 09 - Defense validation and regression
```

## Thiết kế từng module

Mỗi module nên có 5 phần cố định:

1. Learning objective.
2. Vulnerable logic (mô tả rõ root cause).
3. Exploit goal (điều kiện pass).
4. Hints có kiểm soát (không lộ đáp án ngay).
5. Remediation objective (fix rồi retest).

## Ví dụ rubric cho một lab

| Thành phần       | Nội dung                                                  |
| ---------------- | --------------------------------------------------------- |
| Scenario         | Đổi email account qua endpoint `/my-account/change-email` |
| Vulnerability    | Token chỉ kiểm tra khi method = POST                      |
| Student task     | Xây dựng PoC bypass bằng GET hoặc method override         |
| Success criteria | Email đổi thành công trong phiên victim                   |
| Defense task     | Áp token validation theo effective method + fail-closed   |

## Chuẩn dữ liệu cho huấn luyện agent

## Input artifacts cho agent

- HTTP request/response mẫu.
- Cookie attributes và session behavior.
- Mô tả endpoint/business action.
- Constraints (không có XSS, có/không có method override, v.v.).

## Output mong đợi từ agent

- Nhận diện điều kiện CSRF khả thi/không khả thi.
- Chọn bypass pattern tương ứng.
- Đề xuất PoC dạng chuẩn hóa.
- Đề xuất fix tương ứng root cause.

## Evaluation criteria cho agent

| Tiêu chí            | Mô tả                                   |
| ------------------- | --------------------------------------- |
| Accuracy            | Xác định đúng root cause                |
| Completeness        | Bao phủ đủ điều kiện và bước kiểm thử   |
| Explainability      | Giải thích vì sao payload hoạt động     |
| Defensive alignment | Đề xuất fix đúng bản chất, không vá tạm |

## Mẫu task cards cho chương trình huấn luyện

## Card A - Detection

- Input: Request đổi mật khẩu có cookie session, không token.
- Goal: Kết luận có CSRF hay không, nêu điều kiện.

## Card B - Token bypass

- Input: Request có `csrf` nhưng endpoint vẫn chạy khi thiếu `csrf`.
- Goal: Mô tả kỹ thuật bypass và bằng chứng cần thu thập.

## Card C - SameSite reasoning

- Input: Session cookie `SameSite=Lax`, endpoint nhạy cảm dùng GET.
- Goal: Mô hình hóa đường khai thác khả thi.

## Card D - Remediation

- Input: Hệ thống check Referer bằng substring.
- Goal: Đề xuất chiến lược fix đầy đủ nhiều lớp.

## Gợi ý tích hợp vào pipeline lab

1. Mỗi module có test script kiểm tra pass/fail tự động.
2. Có mode "vulnerable" và "patched" để so sánh.
3. Lưu exploit evidence (request, PoC, ảnh trạng thái trước/sau).
4. Chạy regression khi cập nhật framework/session middleware.

## Related Files

- [Exploitation Workflow](04-exploitation-workflow.md)
- [Advanced CSRF Patterns](08-advanced-csrf-patterns.md)
- [Defense and Mitigation](10-defense-mitigation.md)
- [Testing Checklist and Playbook](12-testing-checklist-and-playbook.md)
