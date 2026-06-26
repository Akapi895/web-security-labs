# CSRF Root Causes and Conditions

## Tổng quan nguyên nhân gốc

CSRF không phải do một lỗi đơn lẻ, mà là tổ hợp của:

- Thiết kế xác thực request thiếu lớp xác nhận chủ đích.
- Áp dụng anti-CSRF không nhất quán giữa các endpoint.
- Hiểu sai hành vi browser (cookie, SameSite, Referer/Origin, method override).

## Nhóm nguyên nhân chính

## 1. Thiếu cơ chế anti-CSRF token

Đây là nguyên nhân trực tiếp và phổ biến nhất:

- Endpoint state-changing không yêu cầu token.
- Hoặc chỉ bảo vệ một phần route, bỏ sót route API khác.

## 2. Có token nhưng validate không đúng

Các lỗi điển hình:

- Chỉ validate token với POST, bỏ qua GET/HEAD/PUT qua override.
- Chỉ validate khi parameter token xuất hiện, thiếu token thì cho qua.
- Chấp nhận token rỗng hoặc chỉ kiểm tra "token key tồn tại".
- Token không ràng buộc session user.
- Token liên kết với cookie không phải session cookie.
- Mô hình double-submit triển khai sai (chỉ so sánh token param với token cookie do client kiểm soát).

## 3. Kiểm tra Origin/Referer không đầy đủ

Các anti-pattern thường gặp:

- Fail-open khi thiếu Origin/Referer.
- Dùng substring/regex yếu (contains, startsWith) nên bị lookalike domain bypass.
- Chỉ kiểm tra một số route nhạy cảm, bỏ qua route tương đương.

## 4. Cấu hình SameSite không phù hợp

Các cấu hình rủi ro:

- Session cookie không set SameSite (browser fallback không đồng nhất).
- Đặt SameSite=None cho cookie nhạy cảm mà không cần thiết.
- Quá phụ thuộc SameSite=Lax dù endpoint vẫn cho phép state-changing qua GET top-level.

## 5. Xử lý request phía server thiếu chặt chẽ

| Vấn đề                                    | Hệ quả                                            |
| ----------------------------------------- | ------------------------------------------------- |
| Cho phép state-changing bằng GET          | Dễ bị trigger bởi link/img/script navigation      |
| Chấp nhận method override bừa bãi         | Né được rule chống CSRF theo method               |
| Parse linh hoạt quá mức theo content-type | JSON endpoint vẫn nhận dữ liệu từ text/plain/form |
| Không ràng buộc replay/nonce              | Request forged có thể lặp nhiều lần               |

## 6. Thiết kế business flow dễ bị ép thực thi

Ví dụ:

- Action nguy hiểm không yêu cầu re-auth hoặc confirmation step.
- Không có transaction signing cho thao tác tài chính.
- Login flow thiếu CSRF protection, mở đường cho login CSRF.

## Điều kiện cần để tấn công CSRF thành công

## Điều kiện lõi

1. Có endpoint tạo thay đổi trạng thái có giá trị khai thác.
2. Browser của nạn nhân sẽ tự gửi credential hợp lệ khi request được kích hoạt.
3. Attacker tái tạo được request hợp lệ (method, params, encoding, route).
4. Cơ chế anti-CSRF hiện tại thiếu hoặc bypass được.

## Điều kiện tăng tỷ lệ thành công

- Nạn nhân thường xuyên online ở ứng dụng mục tiêu.
- Endpoint phản hồi "silent success" (khó bị người dùng phát hiện).
- Không có thông báo out-of-band (email cảnh báo, push xác nhận).
- Không có bảo vệ theo rủi ro (step-up auth cho thao tác nhạy cảm).

## Ma trận điều kiện nhanh

| Câu hỏi                                  | Yes                     | No                             |
| ---------------------------------------- | ----------------------- | ------------------------------ |
| Endpoint có state-changing?              | Tiếp tục                | Không phải mục tiêu CSRF chính |
| Request dùng cookie session?             | Tiếp tục                | Đánh giá cơ chế auth khác      |
| Có token mạnh, ràng buộc session/action? | Khó khai thác trực tiếp | Tiếp tục đánh giá bypass       |
| Có thể trigger từ context cross-site?    | Có thể khai thác        | Khó khả thi                    |

## Dấu hiệu ứng dụng có rủi ro CSRF cao

- Legacy app với nhiều form cũ.
- API và web UI dùng chung session nhưng bảo vệ không đồng đều.
- Nhiều endpoint admin viết thủ công, thiếu middleware bảo vệ.
- Dùng nhiều framework kết hợp (session framework khác csrf framework).

## Kết luận kỹ thuật

CSRF xuất hiện khi server coi "đã xác thực" là "đã có chủ đích". Chừng nào hai khái niệm này chưa được tách bằng lớp xác thực intent mạnh, ứng dụng vẫn có rủi ro CSRF.

## Related Files

- [CSRF Overview](00-overview.md)
- [Discovery and Detection](03-discovery-and-detection.md)
- [Token Validation Bypasses](05-token-validation-bypasses.md)
- [Origin Referer and Request Shape Bypass](07-origin-referer-and-request-shape-bypass.md)
- [Defense and Mitigation](10-defense-mitigation.md)
