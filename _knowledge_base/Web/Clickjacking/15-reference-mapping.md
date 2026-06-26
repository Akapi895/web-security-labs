# Ánh xạ tài liệu tham chiếu

## Mục tiêu

Liên kết nguồn tài liệu gốc trong thư mục reference với từng chương trong bộ kiến thức Clickjacking để hỗ trợ truy xuất nguồn và kiểm chứng nội dung.

## Bản đồ theo chương

| Chương | Trọng tâm | Nguồn tham chiếu chính |
| --- | --- | --- |
| 00-overview | Khái niệm tổng quan, phạm vi, mô hình đe dọa | OWASP, PortSwigger, HackTricks |
| 01-browser-ui-redressing-fundamentals | Cơ chế render, xếp lớp, tương tác | OWASP, PortSwigger |
| 02-attack-primitives-iframe-layering-opacity | Primitive iframe, layering, opacity, căn tọa độ | PortSwigger, PayloadsAllTheThings |
| 03-conditions-and-root-causes | Điều kiện khai thác và nguyên nhân gốc | OWASP, HackTricks |
| 04-detection-and-target-mapping | Quy trình phát hiện và lập bản đồ mục tiêu | OWASP WSTG, PortSwigger |
| 05-basic-exploitation | Chuỗi khai thác cơ bản có thể tái hiện | PortSwigger labs, PayloadsAllTheThings |
| 06-prefill-dragdrop-multistep | Biến thể prefill, kéo-thả, nhiều bước | PortSwigger (advanced), HackTricks |
| 07-doubleclickjacking-and-popup-variants | Biến thể timing/cửa sổ hiện đại | Nghiên cứu thực chiến, HackTricks |
| 08-frame-buster-and-client-side-bypass | Giới hạn frame-buster và bypass phía client | OWASP, PortSwigger legacy notes |
| 09-advanced-svg-filter-ui-redressing | Kỹ thuật redressing nâng cao theo browser behavior | Nghiên cứu công khai hiện đại |
| 10-attack-chains-and-impact-modeling | Chuỗi tấn công đa lỗ hổng và phân tích tác động | OWASP risk framing, case studies |
| 11-exploitation-workflows | Quy trình khai thác chuẩn hóa | Tổng hợp từ toàn bộ nguồn |
| 12-payloads-cheatsheet | Snippet, checklist, mẫu báo cáo | PayloadsAllTheThings, lab notes |
| 13-defense-mitigation | CSP/XFO, UX hardening, vận hành phòng thủ | OWASP Cheat Sheet, PortSwigger defense |
| 14-labs-and-agent-training-scenarios | Kịch bản đào tạo và rubric đánh giá | Tổng hợp huấn luyện nội bộ + nguồn mở |

## Danh mục nguồn chính trong thư mục reference

1. HackTricks - các mục Clickjacking và UI Redressing.
2. OWASP - Cheat Sheet, Testing Guide, nguyên tắc phòng thủ.
3. PayloadsAllTheThings - snippet, ý tưởng payload phục vụ lab.
4. PortSwigger Web Security Academy - bài học và lab clickjacking.

## Hướng dẫn bảo trì mapping

1. Khi thêm chương mới, bổ sung ngay dòng mapping tương ứng.
2. Nếu chỉnh sửa nội dung trọng yếu, cập nhật lại cột “Nguồn tham chiếu chính”.
3. Ưu tiên nguồn có mô tả kỹ thuật rõ ràng và kiểm chứng được.

## Tệp liên quan

- [Tổng quan](00-overview.md)
- [Workflow khai thác](11-exploitation-workflows.md)
- [Phòng thủ và giảm thiểu](13-defense-mitigation.md)
