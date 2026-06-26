# Tổng quan Web Cache Deception

## Định nghĩa

**Web Cache Deception (WCD)** là lỗ hổng trong đó cache layer (CDN, reverse proxy, edge cache) bị đánh lừa để lưu một response động (dynamic, nhạy cảm) như thể đó là tài nguyên tĩnh (static).

Hệ quả là kẻ tấn công có thể truy cập lại URL đã bị cache để lấy dữ liệu của nạn nhân.

## Bản chất kỹ thuật

WCD xuất hiện khi có **sai lệch cách diễn giải request** giữa:

- Cache layer (thường quyết định cache theo extension/prefix/key).
- Origin stack (web server + framework route/parser).

Nói cách khác, cache và origin nhìn cùng một URL nhưng hiểu theo hai nghĩa khác nhau:

- Cache: đây là static object có thể lưu.
- Origin: đây là dynamic endpoint trả về dữ liệu tài khoản.

## WCD khác gì với Web Cache Poisoning

| Chủ đề         | Web Cache Deception                           | Web Cache Poisoning                      |
| -------------- | --------------------------------------------- | ---------------------------------------- |
| Mục tiêu chính | Lấy dữ liệu nhạy cảm của nạn nhân từ cache    | Tiêm nội dung độc hại vào response cache |
| Cơ chế lỗi     | Sai lệch cache rule + URL parsing             | Sai lệch cache key + unkeyed input       |
| Kết quả        | Lộ dữ liệu riêng tư (token, API key, profile) | Phát tán payload đến nhiều người dùng    |

## Điều kiện hình thành

WCD thường cần đồng thời các điều kiện sau:

1. Có endpoint dynamic trả về dữ liệu nhạy cảm qua GET/HEAD/OPTIONS.
2. Có cache rule có thể bị kích hoạt bởi extension/prefix/file name.
3. Có discrepancy trong path parsing, delimiter hoặc normalization.
4. Có khả năng dẫn được nạn nhân truy cập URL độc hại.

## Mô hình tấn công tổng quát

1. Chọn endpoint nhạy cảm (ví dụ: `/my-account`, `/api/auth/session`).
2. Tạo URL mơ hồ để cache coi là static, origin coi là dynamic.
3. Nạn nhân truy cập URL, response của nạn nhân bị cache.
4. Kẻ tấn công gọi lại cùng cache key để đọc dữ liệu đã lưu.

## Tác động bảo mật

| Nhóm tác động   | Mô tả                                                  |
| --------------- | ------------------------------------------------------ |
| Confidentiality | Lộ API key, JWT/session data, thông tin tài khoản, PII |
| Privacy         | Lộ thông tin cá nhân trong endpoint “my-account”       |
| Business risk   | Mất uy tín, vi phạm compliance, hỗ trợ takeover chain  |

## Chỉ báo thông dụng khi pentest

- Header như `X-Cache`, `CF-Cache-Status`, `Age` thay đổi theo mẫu `miss -> hit`.
- Cùng một URL, request thứ 2 nhanh hơn rõ rệt so với request thứ 1.
- Đường dẫn có extension static (`.css`, `.js`, `.ico`) vẫn trả về nội dung dynamic.

## Khung tài liệu liên quan

- [01-cache-fundamentals.md](01-cache-fundamentals.md)
- [02-root-causes.md](02-root-causes.md)
- [03-attack-surface-and-detection.md](03-attack-surface-and-detection.md)
- [08-exploitation-workflows.md](08-exploitation-workflows.md)
- [10-defense-mitigation.md](10-defense-mitigation.md)

## Kết luận nhanh

WCD không đơn thuần là lỗi “thêm `.css` vào URL”. Bản chất của nó là **lỗi thiết kế và đồng bộ parser/rule** trong kiến trúc nhiều lớp (browser -> CDN/proxy -> origin). Khi các lớp không thống nhất cách hiểu URL, dữ liệu động có thể bị lưu và phát lại như tài nguyên tĩnh.
