# Reference Mapping and Coverage

## Purpose

File này ánh xạ nội dung đã chuẩn hóa trong knowledge base với các tài liệu gốc trong thư mục `reference/`, giúp truy vết nguồn và kiểm tra phạm vi bao phủ.

## Source Files

- `reference/portswigger.txt`
- `reference/hacktricks.txt`
- `reference/PayloadsAllTheThings.md`
- `reference/lab1.txt`
- `reference/lab2.txt`
- `reference/lab3.txt`
- `reference/lab4.txt`
- `reference/lab5.txt`
- `reference/lab6.txt`

## Coverage Map

| KB Module                             | Main Source Inputs                       | Coverage Focus                                       |
| ------------------------------------- | ---------------------------------------- | ---------------------------------------------------- |
| 00-overview                           | portswigger, hacktricks, payloads        | Khái niệm, taxonomy, lifecycle                       |
| 01-concurrency-and-timing-foundations | portswigger                              | Shared resource, critical section, sub-state         |
| 02-root-causes                        | portswigger, hacktricks                  | Nguyên nhân thiết kế, lock, transaction, distributed |
| 03-detection-and-scoping              | portswigger (predict/probe/prove), labs  | Phương pháp nhận diện và chứng minh                  |
| 04-limit-overrun-toctou               | portswigger, lab1, lab2                  | TOCTOU, coupon/rate-limit bypass                     |
| 05-multi-endpoint-race                | portswigger, lab3                        | Căn chỉnh race window đa endpoint                    |
| 06-single-endpoint-race               | portswigger, lab4                        | Trộn state trong cùng endpoint                       |
| 07-partial-construction-race          | portswigger, lab6, hacktricks            | Trạng thái chưa hoàn thiện và null-equivalent input  |
| 08-time-sensitive-attacks             | portswigger, lab5, hacktricks            | Token collision theo timing                          |
| 09-exploitation-workflows             | portswigger whitepaper methodology, labs | Pattern hóa quy trình khai thác                      |
| 10-tooling-burp-and-turbo-intruder    | portswigger, hacktricks, payloads        | Kỹ thuật gửi song song và tuning                     |
| 11-lab-design-and-training            | labs 1-6 + methodology                   | Xây lab và dataset huấn luyện agent                  |
| 12-defense-mitigation                 | portswigger prevention guidance          | Atomicity, locking, integrity, token hygiene         |
| 13-testing-and-review-checklists      | toàn bộ nguồn                            | Checklist pentest/dev/agent                          |

## Notes on Interpretation

1. Nội dung được tái cấu trúc và chuẩn hóa theo mô hình module như SQLi knowledge base.
2. Payload cụ thể trong nguồn được diễn giải ở mức pattern để tăng tính tái sử dụng.
3. Trọng tâm đặt vào nguyên lý concurrency/timing và bất biến trạng thái (state invariants).

## Related Files

- [00-overview](00-overview.md)
- [09-exploitation-workflows](09-exploitation-workflows.md)
- [12-defense-mitigation](12-defense-mitigation.md)
