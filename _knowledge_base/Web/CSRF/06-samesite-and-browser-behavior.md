# SameSite and Browser Behavior in CSRF

## Vì sao SameSite quan trọng

SameSite quyết định khi nào browser gửi cookie trong ngữ cảnh cross-site. Vì CSRF phụ thuộc vào việc cookie được tự động gửi, SameSite ảnh hưởng trực tiếp đến khả năng khai thác.

Tuy nhiên SameSite chỉ là lớp giảm thiểu, không phải miễn nhiễm CSRF.

## Site vs Origin (điểm dễ nhầm)

| Khái niệm | Thành phần           | Hệ quả bảo mật                     |
| --------- | -------------------- | ---------------------------------- |
| Origin    | scheme + host + port | Dùng cho SOP/CORS đọc dữ liệu      |
| Site      | scheme + eTLD+1      | Dùng để quyết định cookie SameSite |

Cross-origin có thể vẫn same-site (ví dụ subdomain khác nhau trong cùng eTLD+1).

## Ba chế độ SameSite

| Chế độ | Hành vi tổng quát                                           | Ý nghĩa CSRF                                         |
| ------ | ----------------------------------------------------------- | ---------------------------------------------------- |
| Strict | Không gửi cookie trong cross-site request                   | Giảm mạnh CSRF cổ điển                               |
| Lax    | Gửi cookie trong một số top-level cross-site GET navigation | Vẫn có bề mặt khai thác nếu action reachable qua GET |
| None   | Gửi cookie mọi ngữ cảnh (kèm Secure)                        | CSRF risk cao nếu thiếu lớp khác                     |

## Lax-by-default và rủi ro thực tế

Nhiều browser áp Lax mặc định cho cookie không khai báo SameSite. Điều này giúp giảm một phần CSRF nhưng dễ tạo cảm giác an toàn giả nếu:

- Endpoint state-changing vẫn dùng GET.
- Có gadget điều hướng phù hợp.
- Có method override hoặc route xử lý linh hoạt.

## Các pattern bypass SameSite điển hình

## 1. Lax bypass qua top-level GET navigation

Nếu endpoint nhạy cảm xử lý GET, attacker có thể dùng:

- link dụ click,
- `document.location`,
- hoặc trigger điều hướng tương đương.

## 2. Bypass qua method override

Ngay cả khi logic nghiệp vụ kỳ vọng POST, một số framework cho `_method=GET/DELETE/PUT` hoặc header override làm thay đổi effective method.

## 3. Strict bypass qua on-site gadget

Nếu có client-side redirect/open redirect gadget trong cùng site:

- Request đầu cross-site kích hoạt gadget.
- Gadget tạo request thứ cấp same-site.
- Cookie được gửi trong request thứ cấp.

## 4. Bypass qua sibling domain

Lỗ hổng trên domain cùng site (ví dụ XSS ở subdomain khác) có thể được dùng để phát sinh request same-site tới domain mục tiêu.

## 5. Cửa sổ cookie mới cấp (browser behavior edge cases)

Một số trường hợp browser có ngoại lệ ngắn hạn cho cookie mới cấp trong top-level POST. Nếu attacker ép refresh session cookie đúng thời điểm, có thể tăng khả năng khai thác.

## Checklist kiểm thử SameSite trong pentest

- [ ] Session cookie có SameSite không?
- [ ] Giá trị là Strict, Lax, hay None?
- [ ] Endpoint nhạy cảm có xử lý GET không?
- [ ] Có cơ chế method override không?
- [ ] Có gadget redirect/client-side navigation trong cùng site không?
- [ ] Có sibling domain dễ bị tấn công không?

## Hướng phòng thủ đúng

1. Không để state-changing action chạy bằng GET.
2. Dùng SameSite như lớp bổ trợ, không thay CSRF token.
3. Chặn method override cho action nhạy cảm nếu không thật sự cần.
4. Giảm attack surface ở sibling domains và client-side redirect.

## Related Files

- [Browser Auth and Trust Model](01-browser-auth-and-trust-model.md)
- [Exploitation Workflow](04-exploitation-workflow.md)
- [Origin Referer and Request Shape Bypass](07-origin-referer-and-request-shape-bypass.md)
- [Defense and Mitigation](10-defense-mitigation.md)
