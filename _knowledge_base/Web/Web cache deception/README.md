# Bộ kiến thức Web Cache Deception

## Mục tiêu

Bộ tài liệu này tổng hợp và chuẩn hóa kiến thức về **Web Cache Deception (WCD)** để phục vụ:

- Học tập theo lộ trình có cấu trúc.
- Pentest và phân tích hệ thống có sử dụng CDN/reverse proxy/cache layer.
- Xây dựng lab thực hành và huấn luyện agent bảo mật.

Nội dung được tái cấu trúc từ các tài liệu tham khảo trong thư mục `reference`, theo phong cách module hóa tương tự bộ SQLi.

## Cấu trúc tài liệu

- [00-overview.md](00-overview.md): Tổng quan WCD, mô hình đe dọa, tác động và điều kiện hình thành.
- [01-cache-fundamentals.md](01-cache-fundamentals.md): Cơ chế web caching, cache key, quy tắc cache và sự khác nhau giữa nội dung động và nội dung đã cache.
- [02-root-causes.md](02-root-causes.md): Nguyên nhân gốc rễ, các sai lệch parser và điều kiện khai thác.
- [03-attack-surface-and-detection.md](03-attack-surface-and-detection.md): Cách tìm endpoint mục tiêu, phát hiện cache, thử nghiệm có hệ thống.
- [04-path-mapping-attacks.md](04-path-mapping-attacks.md): Kỹ thuật khai thác sai lệch URL path mapping.
- [05-delimiter-attacks.md](05-delimiter-attacks.md): Kỹ thuật delimiter discrepancy và delimiter decoding discrepancy.
- [06-normalization-attacks.md](06-normalization-attacks.md): Kỹ thuật khai thác normalization discrepancy (origin/cache).
- [07-cache-rules-key-and-oracles.md](07-cache-rules-key-and-oracles.md): Phân tích quy tắc cache, cache key, cache oracle và sai số đo lường.
- [08-exploitation-workflows.md](08-exploitation-workflows.md): Quy trình tổng quát và các mẫu tấn công có thể tái sử dụng.
- [09-lab-playbooks.md](09-lab-playbooks.md): Kịch bản thực hành theo kiểu lab để tái hiện và kiểm chứng.
- [10-defense-mitigation.md](10-defense-mitigation.md): Chiến lược phòng thủ, gia cố CDN/reverse proxy/origin.
- [11-payloads-cheatsheet.md](11-payloads-cheatsheet.md): Mẫu payload, bộ delimiter, checklist thử nghiệm nhanh.
- [12-agent-training-blueprint.md](12-agent-training-blueprint.md): Khung dữ liệu và quy trình huấn luyện agent.

## Lộ trình học khuyến nghị

1. Đọc [00-overview.md](00-overview.md) và [01-cache-fundamentals.md](01-cache-fundamentals.md) để nắm bản chất.
2. Chuyển sang [02-root-causes.md](02-root-causes.md) và [03-attack-surface-and-detection.md](03-attack-surface-and-detection.md) để hình thành tư duy phát hiện.
3. Đi sâu vào các module kỹ thuật từ [04-path-mapping-attacks.md](04-path-mapping-attacks.md) đến [07-cache-rules-key-and-oracles.md](07-cache-rules-key-and-oracles.md).
4. Vận dụng qua [08-exploitation-workflows.md](08-exploitation-workflows.md) và [09-lab-playbooks.md](09-lab-playbooks.md).
5. Kết thúc với [10-defense-mitigation.md](10-defense-mitigation.md), [11-payloads-cheatsheet.md](11-payloads-cheatsheet.md), [12-agent-training-blueprint.md](12-agent-training-blueprint.md).

## Lưu ý phạm vi

- WCD khác Web Cache Poisoning: WCD tập trung vào **rò rỉ dữ liệu nhạy cảm do cache nhầm**, không phải tiêm nội dung độc hại vào cache để phát tán.
- Khi thử nghiệm, chỉ thực hiện trong môi trường hợp pháp (lab, staging, CTF, pentest được ủy quyền).
