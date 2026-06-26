# Race Condition Overview

## Definition

Race Condition là lỗi xuất hiện khi kết quả của hệ thống phụ thuộc vào thứ tự hoặc thời điểm thực thi của nhiều tác vụ đồng thời, nhưng ứng dụng lại không đảm bảo đồng bộ đúng cách. Khi đó, các request hoặc tiến trình có thể va chạm trên cùng dữ liệu và tạo ra trạng thái ngoài ý muốn.

Trong web app, lỗi này thường nằm trong nhóm business logic flaws vì không phải lỗi cú pháp, mà là lỗi mô hình trạng thái và điều phối xử lý.

## Core Concepts

| Concept          | Meaning                                                                         | Security Impact                                               |
| ---------------- | ------------------------------------------------------------------------------- | ------------------------------------------------------------- |
| Shared Resource  | Tài nguyên dùng chung: số dư, giỏ hàng, token reset, trạng thái đơn hàng, quota | Nhiều request cùng đọc/ghi gây xung đột                       |
| Critical Section | Đoạn logic phải được thực thi nguyên tử (atomic)                                | Nếu không khóa hoặc transaction tốt, dữ liệu dễ lệch          |
| Race Window      | Khoảng thời gian ngắn có thể xảy ra va chạm                                     | Đây là điểm tấn công chính                                    |
| Order Dependency | Kết quả phụ thuộc request nào chạy trước/sau                                    | Có thể bypass validation nếu đảo thứ tự                       |
| Hidden Sub-state | Trạng thái trung gian tạm thời trong một request                                | Mở ra primitive khai thác mới, không chỉ limit overrun        |
| TOCTOU           | Time-of-check to time-of-use                                                    | Check hợp lệ ở bước đầu nhưng trạng thái đổi trước khi commit |

## Why Web Systems Are Vulnerable

1. Ứng dụng xử lý request song song (multi-thread, async worker, multi-process).
2. Một request thường gồm nhiều bước đọc/kiểm tra/cập nhật nhưng không gói trong transaction nguyên tử.
3. Session, database, cache, queue, email worker có thể cập nhật không đồng bộ theo từng lớp.
4. Cơ chế rate-limit hoặc one-time action chỉ kiểm tra ở đầu luồng, commit ở cuối luồng.

## Classification

| Class                  | Core Idea                                                      | Typical Example                             |
| ---------------------- | -------------------------------------------------------------- | ------------------------------------------- |
| Limit Overrun (TOCTOU) | Gửi nhiều request trước khi counter/trạng thái được cập nhật   | Dùng coupon/gift card nhiều lần             |
| Multi-endpoint Race    | Hai endpoint khác nhau va chạm trên cùng bản ghi               | Vừa checkout vừa sửa cart                   |
| Single-endpoint Race   | Cùng endpoint, tham số khác nhau, ghi đè trạng thái            | Đổi email song song để chiếm email mục tiêu |
| Partial Construction   | Object được tạo theo nhiều bước, có trạng thái chưa hoàn thiện | Confirm account khi token chưa được ghi     |
| Time-sensitive Exploit | Không hẳn race, nhưng khai thác timing chính xác               | Token reset trùng do timestamp yếu          |

## Exploitation Lifecycle

1. Identify chức năng nhạy cảm với timing: chuyển tiền, reset mật khẩu, đổi email, cập nhật trạng thái đơn.
2. Model state machine: xác định bước check, bước update, bước side effect (email, queue, callback).
3. Find race window: điểm giữa kiểm tra và commit hoặc giữa hai lần ghi.
4. Align requests: gửi song song để chồng lên race window.
5. Observe deviation: phản hồi bất thường hoặc hiệu ứng bậc hai (email sai người nhận, trạng thái lệch).
6. Prove and stabilize: giảm request dư thừa, chứng minh tái lập, đo tỷ lệ thành công.

## Recommended Reading Order

1. [01-concurrency-and-timing-foundations](01-concurrency-and-timing-foundations.md)
2. [02-root-causes](02-root-causes.md)
3. [03-detection-and-scoping](03-detection-and-scoping.md)
4. [04-limit-overrun-toctou](04-limit-overrun-toctou.md)
5. [05-multi-endpoint-race](05-multi-endpoint-race.md)
6. [06-single-endpoint-race](06-single-endpoint-race.md)
7. [07-partial-construction-race](07-partial-construction-race.md)
8. [08-time-sensitive-attacks](08-time-sensitive-attacks.md)
9. [09-exploitation-workflows](09-exploitation-workflows.md)
10. [10-tooling-burp-and-turbo-intruder](10-tooling-burp-and-turbo-intruder.md)
11. [11-lab-design-and-training](11-lab-design-and-training.md)
12. [12-defense-mitigation](12-defense-mitigation.md)
13. [13-testing-and-review-checklists](13-testing-and-review-checklists.md)
14. [14-reference-mapping](14-reference-mapping.md)
