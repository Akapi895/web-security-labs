# Lab Design and Agent Training Guide

## Goal

Chuẩn hóa cách xây lab Race Condition để:

1. Dạy người học theo lộ trình từ cơ bản đến nâng cao.
2. Tạo dữ liệu huấn luyện cho agent phân tích bảo mật.
3. Đảm bảo lab đo được đúng năng lực nhận diện và khai thác.

## Lab Design Principles

1. Một invariant rõ ràng cho mỗi lab (ví dụ one-time coupon, one-time token).
2. Có race window thật sự và có thể điều khiển xác suất.
3. Có tín hiệu thành công đo được từ state cuối cùng, không chỉ response.
4. Có cơ chế reset trạng thái để thử lặp lại.

## Difficulty Tiers

| Level        | Focus                               | Suggested Scenario                           |
| ------------ | ----------------------------------- | -------------------------------------------- |
| Apprentice   | Limit overrun cơ bản                | Coupon/gift card reuse                       |
| Practitioner | Multi-endpoint hoặc single-endpoint | Checkout+cart, change-email                  |
| Expert       | Hidden sub-state phức tạp           | Partial construction + null-equivalent token |

## Canonical Scenario Set

1. Limit overrun: áp coupon nhiều lần.
2. Rate-limit bypass: brute-force vượt ngưỡng khóa.
3. Multi-endpoint: checkout đồng thời add item.
4. Single-endpoint: đổi email song song để chiếm email mời admin.
5. Time-sensitive: token trùng do timestamp.
6. Partial construction: confirm user khi token chưa khởi tạo.

## Required Lab Components

### Application Layer

- Endpoint nhạy cảm.
- Shared resource theo key rõ ràng.
- State transition có thể mô hình hóa.

### Observability Layer

- Log request ID, user key, timestamp.
- Log bước check, update, side effect.
- Snapshot state trước/sau mỗi attempt.

### Control Layer

- Script reset state lab.
- Seed dữ liệu mặc định.
- Flag thành công rõ ràng.

## Agent Training Artifacts

Để huấn luyện agent, nên xuất mỗi attempt thành bản ghi có cấu trúc:

```json
{
  "scenario": "single-endpoint-email-claim",
  "attempt_id": "a-1042",
  "requests": ["r1", "r2"],
  "dispatch_mode": "parallel",
  "observed_responses": [200, 200],
  "state_before": "pending_email=attacker",
  "state_after": "account_email=target",
  "invariant_broken": true,
  "success": true
}
```

## Evaluation Rubric

| Capability | What to Evaluate                              |
| ---------- | --------------------------------------------- |
| Detection  | Tìm đúng endpoint có collision potential      |
| Reasoning  | Mô hình hóa được race window và sub-state     |
| Execution  | Chọn đúng chiến lược gửi song song            |
| Validation | Chứng minh được invariant bị phá              |
| Mitigation | Đề xuất fix atomic/transaction đúng trọng tâm |

## Lab Author Checklist

1. Invariant đã mô tả rõ chưa?
2. Có bằng chứng race tái lập được ở ít nhất một cấu hình công cụ chưa?
3. Side effects đã được ghi log đủ để debug chưa?
4. Có kịch bản thất bại giả (false positive) để người học phân biệt chưa?

## Related Files

- [09-exploitation-workflows](09-exploitation-workflows.md)
- [12-defense-mitigation](12-defense-mitigation.md)
- [13-testing-and-review-checklists](13-testing-and-review-checklists.md)
