# CSRF Discovery and Detection

## Mục tiêu của giai đoạn detection

Xác định:

1. Endpoint nào đáng tấn công (state-changing, impact cao).
2. Endpoint nào thực sự khả thi CSRF theo mô hình browser + auth + validation.
3. Lớp bảo vệ nào đang có và điểm yếu cụ thể nằm ở đâu.

## Quy trình mapping bề mặt tấn công

## Bước 1: Lập danh sách chức năng nhạy cảm

Ưu tiên theo mức rủi ro:

- Quản lý tài khoản: đổi email, mật khẩu, số điện thoại, MFA.
- Thanh toán/tài chính: chuyển tiền, đổi tài khoản nhận tiền.
- Quản trị: tạo user, đổi role, xoá dữ liệu.
- Tích hợp: API key, webhook, OAuth connections.

## Bước 2: Thu thập request chuẩn

Dùng proxy/intercept (ví dụ Burp) để lưu request gốc khi thao tác hợp pháp.

Thu thập tối thiểu:

- Method và endpoint.
- Required params/body format.
- Header liên quan auth/CSRF.
- Cookie set và thuộc tính SameSite/Secure/HttpOnly.

## Bước 3: Xác định cơ chế xác thực request

| Tín hiệu                  | Ý nghĩa                            |
| ------------------------- | ---------------------------------- |
| Chỉ có session cookie     | CSRF risk cao hơn                  |
| Có hidden csrf token      | Cần test token validation flaws    |
| Có custom header bắt buộc | Đánh giá khả năng forge cross-site |
| Kiểm tra Origin/Referer   | Đánh giá fail-open và bypass logic |

## Bước 4: Kiểm thử biến thể request

Test matrix thực hành:

| Biến thể               | Mục đích                                    |
| ---------------------- | ------------------------------------------- |
| Bỏ token hoàn toàn     | Kiểm tra validate phụ thuộc token hiện diện |
| Token rỗng/sai độ dài  | Kiểm tra validate lỏng                      |
| Đổi method POST -> GET | Kiểm tra method-conditioned validation      |
| Thêm \_method override | Kiểm tra routing override bypass            |
| Đổi content-type       | Kiểm tra parser leniency                    |
| Loại bỏ Origin/Referer | Kiểm tra fail-open                          |
| Referer lookalike      | Kiểm tra regex/domain match sai             |

## Bước 5: Dựng PoC và xác nhận thực thi

Kịch bản xác nhận điển hình:

1. Tạo PoC HTML từ request mục tiêu.
2. Mở PoC trên browser đang đăng nhập victim account.
3. Kiểm tra trạng thái sau request (email đổi chưa, role đổi chưa, v.v.).

## Chỉ báo xác nhận lỗ hổng

- Action thành công dù request xuất phát cross-site.
- Action thành công khi thiếu hoặc sai token.
- Action thành công khi Origin/Referer vắng mặt hoặc giả mạo dễ dàng.
- Action thành công qua phương thức thay thế (GET, HEAD, override method).

## False positive thường gặp

- Request trả 200 nhưng server không commit thay đổi.
- Endpoint yêu cầu xác nhận bổ sung (OTP/re-auth) sau request đầu tiên.
- Session victim hết hạn nên PoC không phản ánh đúng khả năng khai thác.

## Ước lượng mức độ nghiêm trọng

| Yếu tố             | Câu hỏi                                                           |
| ------------------ | ----------------------------------------------------------------- |
| Impact của action  | Action có thể dẫn đến takeover hay admin compromise không?        |
| Friction khai thác | Cần bao nhiêu tương tác người dùng?                               |
| Quy mô ảnh hưởng   | Chỉ user thường hay cả admin/ops?                                 |
| Khả năng chain     | Có thể nối với XSS, OAuth, open redirect, cookie injection không? |

## Checklist detection nhanh

- [ ] Endpoint có state-changing.
- [ ] Browser tự gửi credential cho endpoint.
- [ ] Có thể tạo request hợp lệ từ bối cảnh cross-site.
- [ ] Anti-CSRF check thiếu hoặc bypass được bằng biến thể thực tế.
- [ ] Có bằng chứng thay đổi trạng thái sau PoC.

## Output mong muốn của giai đoạn detection

- Danh sách endpoint vulnerable có mức độ ưu tiên.
- Bản mô tả điều kiện khai thác (preconditions).
- PoC tái lập được.
- Mapping rõ root cause để team fix đúng chỗ.

## Related Files

- [Root Causes and Conditions](02-root-causes-and-conditions.md)
- [Exploitation Workflow](04-exploitation-workflow.md)
- [Token Validation Bypasses](05-token-validation-bypasses.md)
- [Testing Checklist and Playbook](12-testing-checklist-and-playbook.md)
