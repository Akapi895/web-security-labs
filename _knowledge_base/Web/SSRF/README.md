# SSRF Knowledge Base

Bộ tài liệu này chuẩn hóa và tái cấu trúc kiến thức SSRF từ các nguồn tham chiếu trong thư mục `reference`:

- HackTricks (`hacktricks.txt`)
- OWASP SSRF Cheat Sheet (`owasp.txt`)
- PayloadsAllTheThings (`payloadsallthethings.txt`)
- Advanced PayloadsAllTheThings (`advanced_payloadsallthethings.txt`)
- PortSwigger Web Security Academy (`portswigger.txt`)

## Mục tiêu

- Làm rõ bản chất kỹ thuật SSRF trong kiến trúc web hiện đại.
- Chuẩn hóa workflow khai thác từ cơ bản đến nâng cao.
- Tạo nền tảng có thể dùng cho pentest thực chiến hoặc thiết kế lab.

## Cấu trúc tài liệu

1. `overview.md` - Tổng quan, định nghĩa, vai trò SSRF, mô hình tấn công.
2. `architecture-and-root-causes.md` - Trust boundary, root cause, anti-pattern.
3. `detection-and-injection-points.md` - Cách tìm injection point và xác minh SSRF.
4. `exploitation-workflow.md` - Quy trình khai thác theo giai đoạn.
5. `filter-bypass-techniques.md` - Kỹ thuật bypass blacklist/whitelist/filter.
6. `protocol-abuse-and-gopher.md` - SSRF qua scheme/protocol và gopher payload model.
7. `payload-patterns.md` - Mẫu payload theo nhóm kỹ thuật và bối cảnh.
8. `blind-ssrf-and-oast.md` - Blind SSRF, OAST, time-based, inference.
9. `chaining-and-impact.md` - Chaining SSRF và đánh giá tác động.
10. `prevention-and-hardening.md` - Phòng thủ theo OWASP + hardening thực tiễn.
11. `lab-construction-guide.md` - Blueprint xây lab SSRF theo cấp độ.

## Cách đọc đề xuất

1. Đọc `overview.md` và `architecture-and-root-causes.md` để nắm khung tư duy.
2. Đọc `detection-and-injection-points.md` và `exploitation-workflow.md` để áp dụng pentest.
3. Dùng `filter-bypass-techniques.md`, `protocol-abuse-and-gopher.md`, `blind-ssrf-and-oast.md` khi gặp case khó.
4. Kết thúc bằng `chaining-and-impact.md` và `prevention-and-hardening.md` để hoàn chỉnh góc nhìn offensive + defensive.
5. Dùng `lab-construction-guide.md` để chuyển hóa thành bài tập/lab.
