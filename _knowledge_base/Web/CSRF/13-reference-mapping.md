# CSRF Reference Mapping and Traceability

## Mục đích

File này ánh xạ nội dung knowledge base với các nguồn trong thư mục `reference/` để đảm bảo:

- Tính truy vết nguồn kiến thức.
- Dễ cập nhật khi reference thay đổi.
- Rõ ràng phạm vi diễn giải và tái cấu trúc.

## Nguồn sử dụng

- `reference/owasp.txt`
- `reference/portswigger.txt`
- `reference/hacktricks.txt`
- `reference/PayloadsAllTheThings.md`

## Mapping theo chủ đề

| Chủ đề                                 | Nguồn chính                                   | File KB tương ứng                             |
| -------------------------------------- | --------------------------------------------- | --------------------------------------------- |
| Định nghĩa CSRF và tác động            | OWASP, PortSwigger                            | 00-overview.md                                |
| Mô hình cookie/session và user intent  | OWASP, PortSwigger, HackTricks                | 01-browser-auth-and-trust-model.md            |
| Điều kiện tấn công thành công          | PortSwigger, HackTricks                       | 02-root-causes-and-conditions.md              |
| Quy trình nhận diện và kiểm thử        | PortSwigger, HackTricks                       | 03-discovery-and-detection.md                 |
| Workflow khai thác chuẩn hóa           | PortSwigger, PayloadsAllTheThings, HackTricks | 04-exploitation-workflow.md                   |
| Lỗi validate token và bypass           | PortSwigger, HackTricks                       | 05-token-validation-bypasses.md               |
| SameSite và bypass pattern             | PortSwigger, HackTricks                       | 06-samesite-and-browser-behavior.md           |
| Referer/Origin và request-shape bypass | PortSwigger, HackTricks                       | 07-origin-referer-and-request-shape-bypass.md |
| Pattern nâng cao (login/stored/chains) | OWASP, HackTricks, PortSwigger                | 08-advanced-csrf-patterns.md                  |
| Payload thực hành                      | PayloadsAllTheThings, HackTricks, PortSwigger | 09-payloads-cheatsheet.md                     |
| Phòng thủ nhiều lớp                    | OWASP, PortSwigger                            | 10-defense-mitigation.md                      |
| Thiết kế lab/huấn luyện agent          | Tổng hợp từ toàn bộ nguồn                     | 11-lab-design-and-agent-training.md           |
| Checklist pentest và regression        | PortSwigger, HackTricks, OWASP                | 12-testing-checklist-and-playbook.md          |

## Ghi chú tái cấu trúc

1. Nội dung đã được chuẩn hóa theo taxonomy giống SQLi KB (`00-...` đến `13-...`).
2. Ví dụ payload dùng domain placeholder để phục vụ học tập/lab.
3. Các bypass techniques được nhóm lại theo root cause thay vì liệt kê rời rạc.
4. Bổ sung workflow hóa để phù hợp huấn luyện agent.

## Hướng cập nhật trong tương lai

- Nếu reference bổ sung case mới (browser behavior mới, framework mới), ưu tiên cập nhật các file:
  - `06-samesite-and-browser-behavior.md`
  - `07-origin-referer-and-request-shape-bypass.md`
  - `12-testing-checklist-and-playbook.md`

- Nếu bổ sung module lab mới, cập nhật:
  - `11-lab-design-and-agent-training.md`

## Related Files

- [CSRF Overview](00-overview.md)
- [Defense and Mitigation](10-defense-mitigation.md)
- [Testing Checklist and Playbook](12-testing-checklist-and-playbook.md)
