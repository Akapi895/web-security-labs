# JWT Lab Design and Agent Training Blueprint

## Mục tiêu

Xây khung chuẩn để:

1. Thiết kế lab JWT có kiểm soát và đo lường được.
2. Huấn luyện agent/pentester theo workflow nhất quán.
3. Mở rộng sang nhiều biến thể lỗ hổng mà vẫn giữ cấu trúc chuẩn hóa.

## 1) Mô hình lab chuẩn

Mỗi lab nên có 5 thành phần:

1. **Threat model**: mục tiêu tấn công và phạm vi quyền.
2. **Vulnerability seed**: lỗi cụ thể cài vào verifier/key resolver/claim logic.
3. **Observable signals**: status code, redirect, marker nội dung.
4. **Success criteria**: hành động đặc quyền để chứng minh impact.
5. **Defense objective**: control cần bật để vá lỗi.

## 2) Taxonomy kịch bản lab JWT

| Nhóm lab         | Seed lỗi chính                  | Ví dụ bài tập    |
| ---------------- | ------------------------------- | ---------------- |
| Verify flaws     | Bỏ verify hoặc chấp nhận `none` | Lab 1, 2         |
| Weak key         | HS secret yếu/default           | Lab 3            |
| Header key abuse | Trust `jwk`/`jku`/`kid`         | Lab 4, 5, 6      |
| Confusion        | RS/ES <-> HS mismatch           | Lab 7, 8         |
| Claim logic      | Bỏ kiểm `exp`/`aud`/tenant      | Scenario mở rộng |

## 3) Template mô tả một lab

```markdown
# <Lab Name>

## Objective

## Baseline Behavior

## Detection Hypothesis

## Exploitation Steps

## Impact Proof

## Root Cause

## Mitigation

## Regression Tests
```

## 4) Thiết kế scoring/evaluation cho agent

Nên chấm điểm theo evidence-based milestones:

1. Agent xác định đúng token location và `alg`.
2. Agent tạo baseline chuẩn.
3. Agent chọn đúng pattern khai thác.
4. Agent chứng minh impact bằng hành động đặc quyền.
5. Agent đề xuất mitigation khớp root cause.

## 5) Bộ dữ liệu huấn luyện gợi ý

### Input cho agent

1. HTTP request/response mẫu.
2. JWT token snapshots (nhiều phiên bản).
3. Hints có kiểm soát (có/không có JWKS, key leak, ...).

### Output kỳ vọng

1. Chuỗi lập luận detect -> exploit.
2. Payload/token mutation có thể tái hiện.
3. Bằng chứng impact.
4. Đề xuất hardening có thể implement.

## 6) Rubric chất lượng writeup/lời giải

| Tiêu chí           | Mức đạt                          |
| ------------------ | -------------------------------- |
| Technical accuracy | Không sai cơ chế ký/xác minh     |
| Reproducibility    | Bước làm tái hiện được           |
| Evidence quality   | Có baseline + bypass + impact    |
| Root cause clarity | Chỉ ra đúng điểm gãy trust model |
| Mitigation quality | Khớp lỗi, có tính triển khai     |

## 7) Kịch bản mở rộng nên bổ sung sau

1. Multi-tenant JWT claim confusion (`tenant_id` misuse).
2. Refresh token abuse và replay.
3. JWKS caching race/poisoning.
4. JWE + inner JWT handling flaws.
5. Microservice audience confusion.

## 8) Checklist khi tạo lab mới

1. Có endpoint user thường và endpoint đặc quyền tách biệt rõ.
2. Có marker rõ để xác nhận bypass (không mơ hồ).
3. Có đường vá rõ ràng và test regression đi kèm.
4. Không phụ thuộc quá nhiều vào UI, có thể giải bằng HTTP-level.
5. Có ghi chú đạo đức và giới hạn thực hành trong môi trường lab.

## Related Files

- [Attack Workflows and Patterns](11-attack-workflows-patterns.md)
- [PortSwigger Labs Playbook](12-labs-portswigger-playbook.md)
- [Defense and Mitigation](13-defense-mitigation.md)
