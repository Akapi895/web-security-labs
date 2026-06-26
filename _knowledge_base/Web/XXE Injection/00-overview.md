# Tổng Quan Về Lỗ Hổng XXE

## Định Nghĩa

XML External Entity (XXE) Injection là lỗ hổng xảy ra khi ứng dụng phân tích XML với parser cho phép xử lý external entity hoặc tài nguyên bên ngoài (external DTD, schema, stylesheet, XInclude) từ dữ liệu do người dùng kiểm soát.

- CWE mapping: `CWE-611`
- Bản chất: mất ranh giới giữa dữ liệu XML hợp lệ và khả năng parser truy cập tài nguyên hệ thống/remote
- Hệ quả: đọc file local, SSRF, exfiltration, DoS, và trong một số trường hợp có thể leo thang thành RCE

## Vì Sao XXE Quan Trọng

XML không còn phổ biến như JSON trong API mới, nhưng vẫn tồn tại rộng rãi trong:

- SOAP services
- SAML / XML-based SSO flows
- SVG, DOCX, XLSX, XLIFF, RSS
- Legacy integration giữa hệ thống nội bộ
- Parsers trong backend import/export pipeline

Vì vậy, XXE thường nằm ở hidden attack surface thay vì endpoint API rõ ràng.

## Các Nhóm Tấn Công Cốt Lõi

| Nhóm                         | Cơ chế                                          | Dấu hiệu khai thác                               |
| ---------------------------- | ----------------------------------------------- | ------------------------------------------------ |
| Đọc file trực tiếp (in-band) | Entity trả về nội dung file ngay trong response | Thấy dữ liệu hệ thống trong response             |
| XXE sang SSRF                | Entity trỏ đến URL nội bộ/bên ngoài             | Server gửi request đến host do attacker chỉ định |
| Blind XXE (OOB)              | Không có data in-band, exfil qua DNS/HTTP/FTP   | Log Collaborator hoặc listener có interaction    |
| XXE dựa trên lỗi             | Gây lỗi parser để lộ data trong error message   | Error message chứa dữ liệu nhạy cảm              |
| DoS qua mở rộng thực thể     | Mở rộng entity để exhaust tài nguyên            | CPU/memory tăng đột biến, service chậm/treo      |

## Mô Hình Tác Động

| Mục tiêu                      | Ví dụ                                                  |
| ----------------------------- | ------------------------------------------------------ |
| Bảo mật thông tin             | Đọc `/etc/passwd`, `web.config`, secrets, key material |
| Lộ bề mặt mạng nội bộ         | Query metadata service, call internal admin endpoints  |
| Toàn vẹn/điểm pivot kiểm soát | Dùng SSRF để trigger hành vi bên trong hệ thống        |
| Tính sẵn sàng                 | Billion Laughs, parser lock với stream không kết thúc  |

## Điều Kiện Tiên Quyết

XXE thường cần đồng thời các điều kiện sau:

1. Ứng dụng nhận dữ liệu XML (trực tiếp hoặc gián tiếp qua file format XML-based).
2. Parser cho phép DTD/external entity hoặc có một cơ chế include external resource.
3. Input người dùng đi vào phần parser có thể giải quyết entity.
4. Có kênh quan sát kết quả (response, timing, error, hoặc OOB interaction).

## Quy Trình Tấn Công Chuẩn Hóa

```text
1. KHẢO SÁT        -> Tìm endpoint/chức năng có XML parser
2. THĂM DÒ         -> Kiểm tra parser behavior với payload entity an toàn
3. XÁC NHẬN        -> Xác nhận external entity có được resolve hay không
4. KHAI THÁC       -> Chọn mục tiêu: đọc file, SSRF, exfil OOB, dựa trên lỗi
5. MỞ RỘNG TÁC ĐỘNG -> Mở rộng sang tài nguyên nội bộ và data giá trị cao
6. GHI NHẬN        -> Lưu evidence, impact và điều kiện tái hiện
```

## Phạm Vi Bộ Kiến Thức

Bộ tài liệu này được tổ chức từ nền tảng kỹ thuật đến khai thác và phòng thủ:

- Nền tảng XML/DTD/parser
- Nguyên nhân gốc rễ và điều kiện hình thành XXE
- Detection và exploitation workflow theo pattern
- Blind/OOB, bề mặt ẩn và kỹ thuật bypass
- Defense/mitigation và hướng dẫn xây dựng lab + huấn luyện agent

## Tệp Liên Quan

- [01-xml-dtd-parser-fundamentals.md](01-xml-dtd-parser-fundamentals.md)
- [02-root-causes-and-attack-conditions.md](02-root-causes-and-attack-conditions.md)
- [03-detection.md](03-detection.md)
- [04-exploitation-workflow.md](04-exploitation-workflow.md)
- [11-defense-mitigation.md](11-defense-mitigation.md)
