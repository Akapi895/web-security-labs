# CSRF Overview

## Definition

Cross-Site Request Forgery (CSRF, còn gọi là XSRF) là lỗ hổng cho phép attacker ép trình duyệt của nạn nhân gửi request ngoài ý muốn tới ứng dụng mà nạn nhân đang đăng nhập.

Điểm cốt lõi của CSRF không nằm ở việc "đọc được phản hồi", mà nằm ở việc "thực thi được hành động" bằng danh tính của nạn nhân.

## Bản chất kỹ thuật

CSRF tồn tại khi ba yếu tố giao nhau:

1. Trình duyệt tự động gắn credential (cookie session, Basic Auth, client certificate) vào request.
2. Server tin rằng request có credential hợp lệ đồng nghĩa với request có chủ đích của user.
3. Attacker có thể tạo request hợp lệ về mặt cú pháp tới chức năng nhạy cảm.

Nói ngắn gọn: CSRF là lỗi kiểm soát "ý định người dùng" trong các request state-changing.

## Vì sao cơ chế xác thực dựa trên cookie là trọng tâm

Trong mô hình cookie-based session:

- User đăng nhập một lần, browser lưu session cookie.
- Từ đó về sau, browser tự động gửi cookie cho mọi request phù hợp domain/path/scheme.
- Nếu endpoint thay đổi trạng thái chỉ kiểm tra session cookie mà không kiểm tra anti-CSRF signal, request giả mạo sẽ được xử lý như request thật.

Điều này tạo trust relationship bị lạm dụng:

- User tin browser.
- Browser tự động gửi credential.
- Server tin credential.
- Attacker lợi dụng chuỗi tin cậy đó để thực thi hành động trái phép.

## Tác động điển hình

| Nhóm tác động              | Ví dụ                                      |
| -------------------------- | ------------------------------------------ |
| Account takeover gián tiếp | Đổi email rồi reset mật khẩu               |
| Thay đổi cấu hình bảo mật  | Tắt MFA, thay số điện thoại khôi phục      |
| Tác động tài chính         | Chuyển tiền, đổi tài khoản nhận thanh toán |
| Tác động quản trị          | Tạo user admin, đổi quyền, xoá dữ liệu     |
| Chuỗi tấn công             | Login CSRF + Stored XSS + session hijack   |

## Điều kiện để CSRF xảy ra

| Điều kiện                               | Mô tả                                                  |
| --------------------------------------- | ------------------------------------------------------ |
| Có hành động đáng khai thác             | Ví dụ: đổi email, đổi mật khẩu, chuyển tiền, cấp quyền |
| Request dựa vào credential tự gửi       | Cookie session là phổ biến nhất                        |
| Thiếu yếu tố bất ngờ ngoài tầm attacker | Không có token mạnh/nonce ràng buộc đúng               |

## Mô hình hoá vòng đời tấn công

```text
1. Recon chức năng nhạy cảm
   ->
2. Phân tích request thật (method, params, token, headers)
   ->
3. Đánh giá lớp phòng vệ (token / SameSite / Origin-Referer)
   ->
4. Chọn pattern bypass phù hợp
   ->
5. Dựng payload (link, img, form, auto-submit, iframe, JS)
   ->
6. Lừa nạn nhân thực thi trong trạng thái đăng nhập
   ->
7. Xác nhận thay đổi trạng thái và mở rộng tác động
```

## Phân loại CSRF theo góc nhìn khai thác

| Loại                     | Mô tả                                                  |
| ------------------------ | ------------------------------------------------------ |
| No-defense CSRF          | Không có kiểm tra anti-CSRF đáng kể                    |
| Token-bypass CSRF        | Có token nhưng validate sai                            |
| SameSite-bypass CSRF     | Dựa vào hành vi trình duyệt / site gadget              |
| Header-check bypass CSRF | Check Origin/Referer yếu hoặc fail-open                |
| Login CSRF               | Ép nạn nhân đăng nhập vào tài khoản attacker           |
| Stored CSRF              | Payload tồn tại trong nội dung lưu trữ và tự kích hoạt |

## CSRF và mối quan hệ với XSS

- CSRF thường là one-way: attacker kích hoạt được request nhưng không đọc response.
- XSS là two-way: script có thể gửi request, đọc response, exfiltrate dữ liệu.
- Khi có XSS, nhiều lớp chống CSRF có thể bị vô hiệu hóa (đọc token, gửi request hợp lệ, vượt header checks).

## Related Files

- [Browser Auth and Trust Model](01-browser-auth-and-trust-model.md)
- [Root Causes and Conditions](02-root-causes-and-conditions.md)
- [Discovery and Detection](03-discovery-and-detection.md)
- [Exploitation Workflow](04-exploitation-workflow.md)
- [Token Validation Bypasses](05-token-validation-bypasses.md)
- [SameSite and Browser Behavior](06-samesite-and-browser-behavior.md)
- [Origin Referer and Request Shape Bypass](07-origin-referer-and-request-shape-bypass.md)
- [Advanced CSRF Patterns](08-advanced-csrf-patterns.md)
- [Payloads Cheatsheet](09-payloads-cheatsheet.md)
- [Defense and Mitigation](10-defense-mitigation.md)
- [Lab Design and Agent Training](11-lab-design-and-agent-training.md)
- [Testing Checklist and Playbook](12-testing-checklist-and-playbook.md)
- [Reference Mapping](13-reference-mapping.md)
