# Playbook Thiết Kế Lab và Huấn Luyện Agent Cho XXE

## Mục Tiêu

File này hướng dẫn dùng knowledge base XXE để:

- Xây dựng chuỗi lab từ cơ bản đến nâng cao
- Chuẩn hóa tiêu chí đánh giá kết quả khai thác
- Tạo dữ liệu huấn luyện cho security agent

## Lộ Trình Học Tập

| Cấp độ                | Mục tiêu học tập                         | Kỹ năng                     |
| --------------------- | ---------------------------------------- | --------------------------- |
| Cấp 1 - Cơ bản        | Hiểu XML/DTD/entity và detect XXE cơ bản | Đọc file in-band            |
| Cấp 2 - Pivot SSRF    | Kết nối XXE với SSRF nội bộ              | Trinh sát nội bộ            |
| Cấp 3 - Blind OOB     | Exfiltration không cần in-band response  | Quy trình OAST              |
| Cấp 4 - Lỗi/Local DTD | Khai thác khi outbound bị hạn chế        | Logic parser nâng cao       |
| Cấp 5 - Bề mặt ẩn     | XXE qua upload/transform pipelines       | Săn bề mặt tấn công thực tế |

## Các Module Lab Khuyến Nghị

## Mô-đun A: In-Band XXE Cơ Bản

- Endpoint nhận XML rõ ràng
- Parser resolve external entity
- Mục tiêu: đọc `/etc/hostname`, mở rộng sang config file

## Mô-đun B: XXE -> SSRF

- Parser cho phép HTTP entity
- Mục tiêu: truy cập internal endpoint hoặc metadata mock service

## Mô-đun C: OOB Mù

- Endpoint không reflect entity value
- Mục tiêu: xác nhận OOB hit và exfil file ngắn qua external DTD

## Mô-đun D: Trích Xuất Dựa Trên Lỗi

- Ứng dụng trả parser errors
- Mục tiêu: leak file content qua nonexistent-path technique

## Mô-đun E: Tái Mục Đích Local DTD

- Outbound bị chặn
- Mục tiêu: tìm local DTD + redefine entity để lấy data qua lỗi

## Mô-đun F: Bề Mặt Ẩn

- Upload SVG/DOCX/XLSX/XLIFF
- Mục tiêu: tìm XML parser ẩn và exploit thành công

## Kiến Trúc Hạ Tầng Lab

```text
Attacker VM
  - Burp Suite / proxy
  - OAST endpoint (DNS/HTTP)
  - Simple DTD server

Vulnerable App
  - Multiple XML parsing endpoints
  - Configurable parser modes (safe/unsafe)
  - Structured logging

Internal Mock Services
  - Metadata mock
  - Internal admin/health endpoints
```

## Bộ Dữ Liệu và Telemetry Cho Huấn Luyện Agent

## Dữ Liệu Đầu Vào

- Requests: XML payloads hợp lệ và độc hại
- Metadata: endpoint type, content-type, parser mode
- Labels: vulnerable/not vulnerable, exploit type, impact level

## Nhãn Đầu Ra

- Detection result (true/false)
- Exploit path (file-read, SSRF, OOB, error-based)
- Evidence quality score
- Recommended mitigation set

## Thang Đánh Giá

| Tiêu chí               | Mô tả                                             |
| ---------------------- | ------------------------------------------------- |
| Độ chính xác phát hiện | Agent tìm đúng endpoint/parser vulnerable         |
| Chọn kỹ thuật phù hợp  | Chọn đúng pattern theo signal (in-band vs blind)  |
| Chất lượng payload     | Payload phù hợp context XML và parser constraints |
| Độ đầy đủ bằng chứng   | Có request/response/OOB log + impact statement    |
| Độ đúng của giảm thiểu | Đề xuất parser hardening đúng trọng tâm           |

## Biến Thể Kịch Bản Để Tăng Độ Bền Mô Hình

1. Parser chặn general entity nhưng cho parameter entity.
2. Outbound HTTP bị chặn, DNS vẫn mở.
3. Error message bị ẩn một phần.
4. Chỉ có hidden XML surface qua file upload.
5. Có WAF keyword filter cần bypass encoding.

## Vận Hành An Toàn Cho Lab Huấn Luyện

- Tách môi trường lab với hệ thống production.
- Giới hạn network route và credential scope.
- Có cơ chế reset state sau mỗi bài.
- Log và đánh dấu rõ payload nguy cơ DoS.

## Mẫu Prompt Đề Xuất Cho Agent

```text
Đầu vào: HTTP traffic + endpoint description + parser hints
Nhiệm vụ:
1) Xác định khả năng XXE
2) Chọn workflow khai thác tối ưu
3) Tạo payload và expected signal
4) Mô tả impact chain
5) Đề xuất remediation theo mức ưu tiên
Đầu ra: Structured report + các bước tái hiện
```

## Tệp Liên Quan

- [03-detection.md](03-detection.md)
- [04-exploitation-workflow.md](04-exploitation-workflow.md)
- [10-payloads-cheatsheet.md](10-payloads-cheatsheet.md)
- [11-defense-mitigation.md](11-defense-mitigation.md)
