# Khung huấn luyện agent

## Mục tiêu

Tài liệu này định nghĩa cách sử dụng bộ kiến thức WCD để huấn luyện và đánh giá agent bảo mật theo hướng:

- Hiểu đúng bản chất discrepancy giữa cache và origin.
- Sinh payload phù hợp theo context endpoint.
- Xác minh vulnerability bằng bằng chứng có cấu trúc.

## 1) Năng lực agent cần đạt

1. Phân loại endpoint dynamic/có khả năng nhạy cảm.
2. Nhận diện parser discrepancy (mapping, delimiter, decoding, normalization).
3. Chọn pattern payload tối ưu từ [08-exploitation-workflows.md](08-exploitation-workflows.md).
4. Kiểm chứng cache oracle (`miss -> hit`) và victim-flow.
5. Sinh báo cáo root cause -> impact -> mitigation.

## 2) Bộ dữ liệu huấn luyện đề xuất

Mỗi mẫu gồm:

1. **Input context**: baseline request/response + cache headers + route info.
2. **Expected reasoning**: discrepancy type, cache rule type.
3. **Expected action**: payload candidates + key control strategy.
4. **Expected output**: exploit chain, evidence, mitigation.

## 3) Cam kết đầu ra cho agent

Mỗi lần đánh giá, agent phải xuất:

1. Endpoint mục tiêu.
2. Discrepancy đã xác định.
3. Cache rule bị kích hoạt.
4. Payload exploit cuối cùng.
5. Oracle và bằng chứng (`miss -> hit`, data leak).
6. Khuyến nghị fix theo nguyên nhân gốc.

## 4) Thang điểm đánh giá

| Tiêu chí           | Mô tả                                   | Trọng số |
| ------------------ | --------------------------------------- | -------- |
| Accuracy           | Nhận diện đúng discrepancy/rule         | 30%      |
| Reproducibility    | Payload tái hiện được vulnerability     | 25%      |
| Evidence quality   | Bằng chứng đầy đủ, không false positive | 20%      |
| Mitigation quality | Đề xuất fix đúng nguyên nhân gốc        | 15%      |
| Clarity            | Trình bày logic, có cấu trúc            | 10%      |

## 5) Lộ trình đề xuất theo cấp độ

## Cấp 1 - Nền tảng

- Mục tiêu: phân biệt dynamic vs cached, đọc oracle.
- Tài liệu: [00-overview.md](00-overview.md), [01-cache-fundamentals.md](01-cache-fundamentals.md).

## Cấp 2 - Phân tích sai khác

- Mục tiêu: nhận diện mapping/delimiter discrepancy.
- Tài liệu: [02-root-causes.md](02-root-causes.md), [03-attack-surface-and-detection.md](03-attack-surface-and-detection.md), [05-delimiter-attacks.md](05-delimiter-attacks.md).

## Cấp 3 - Khai thác nâng cao

- Mục tiêu: xử lý normalization discrepancy và kết hợp pattern.
- Tài liệu: [06-normalization-attacks.md](06-normalization-attacks.md), [08-exploitation-workflows.md](08-exploitation-workflows.md), [09-lab-playbooks.md](09-lab-playbooks.md).

## Cấp 4 - Tư duy phòng thủ

- Mục tiêu: mapping root cause -> hardening controls.
- Tài liệu: [10-defense-mitigation.md](10-defense-mitigation.md).

## 6) Mẫu prompt cho huấn luyện

## Mẫu A - Phát hiện

"Cho baseline request/response và cache headers, hãy xác định endpoint có nguy cơ WCD không, discrepancy nào khả năng cao nhất, và 5 payload test ưu tiên."

## Mẫu B - Khai thác

"Từ kết quả fuzz delimiter và normalization, hãy đề xuất payload exploit cuối cùng, cách victim priming, cách harvest và bằng chứng cần thu thập."

## Mẫu C - Giảm thiểu

"Với discrepancy đã xác nhận, hãy đề xuất bộ fix theo 3 lớp: origin, CDN/proxy, regression testing."

## 7) Loại bài test để đánh giá bền vững

1. Case có cache hit nhưng không leak data (agent phải tránh false positive).
2. Case cần encoded delimiter, plain delimiter thất bại.
3. Case parser behavior khác nhau theo endpoint.
4. Case defense đã bật (armor), payload cũ không còn hiệu lực.

## 8) Bộ bằng chứng nên lưu

- Baseline traces.
- Fuzz matrix.
- Exploit requests.
- Victim/attacker timeline.
- Ground-truth label (vulnerable/not vulnerable + root cause).

## 9) Liên kết module

- [08-exploitation-workflows.md](08-exploitation-workflows.md)
- [09-lab-playbooks.md](09-lab-playbooks.md)
- [11-payloads-cheatsheet.md](11-payloads-cheatsheet.md)
