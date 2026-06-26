# Browser Auth and Trust Model for CSRF

## Tại sao phải hiểu mô hình trust trước khi khai thác CSRF

CSRF không bắt đầu từ payload, mà bắt đầu từ cách browser và server "tin" nhau. Nếu không nắm mô hình trust này, việc đánh giá khả thi tấn công sẽ thiếu chính xác.

## Trust Relationship trong ứng dụng web

```text
User intention
   |
   v
Browser (auto-attach credential)
   |
   v
Server (accepts credential as authenticated identity)
```

Vấn đề nằm ở khoảng cách giữa:

- User intention: người dùng có thực sự muốn thao tác hay không.
- Authenticated request: request có cookie hợp lệ hay không.

CSRF khai thác khoảng cách này.

## Credential nào có thể bị lạm dụng trong CSRF

| Cơ chế                                  | Có thể bị CSRF? | Ghi chú                                                |
| --------------------------------------- | --------------- | ------------------------------------------------------ |
| Session cookie                          | Có              | Trường hợp phổ biến nhất                               |
| Remember-me cookie                      | Có              | Nếu đủ để thực hiện action                             |
| HTTP Basic Auth                         | Có              | Browser có thể tự gửi thông tin auth                   |
| Client certificate auth                 | Có              | Trình duyệt tự dùng cert đã chọn                       |
| Bearer token trong Authorization header | Thường khó hơn  | Trang ngoài không tự gắn custom header theo ý attacker |

## Browser tự gửi credential như thế nào

Khi một trang attacker ép nạn nhân gửi request sang target, browser vẫn có thể tự thêm:

- Cookie hợp lệ theo domain/path/scheme.
- Một số auth state khác do browser quản lý.

Nếu không có lớp anti-CSRF hiệu quả ở server, request forged được xử lý như request hợp pháp.

## One-way nature của CSRF

Thông thường attacker không đọc được phản hồi do same-origin policy, nhưng vẫn đạt mục tiêu nếu action đã xảy ra.

Ví dụ:

- Không cần đọc response của endpoint đổi email.
- Chỉ cần biết request trả về 200 hoặc trạng thái tài khoản thay đổi là đủ.

## Site vs Origin và ý nghĩa thực chiến

| Khái niệm        | Thành phần           | Ảnh hưởng đến CSRF                |
| ---------------- | -------------------- | --------------------------------- |
| Origin           | scheme + host + port | Quy định đọc dữ liệu qua SOP/CORS |
| Site (schemeful) | scheme + eTLD+1      | Quy định gửi cookie với SameSite  |

Hệ quả quan trọng:

- Cross-origin chưa chắc cross-site.
- Nhiều bypass SameSite khai thác gadget/sibling domain trong cùng site.

## Request classes liên quan CSRF

| Loại request                    | Đặc tính                               | Ý nghĩa tấn công                         |
| ------------------------------- | -------------------------------------- | ---------------------------------------- |
| Top-level GET navigation        | Dễ kích hoạt bằng link/script redirect | Có thể đi qua Lax trong nhiều tình huống |
| Form POST (simple content type) | Không cần JS phức tạp                  | Payload ổn định, dễ social engineering   |
| XHR/fetch with custom headers   | Dễ dính preflight/CORS                 | Khó hơn nếu không có misconfig           |
| Multipart form submit           | Hữu ích cho endpoint upload            |

## Mô hình xác định tính khả thi ban đầu

```text
Nếu action nhạy cảm
  AND request dựa trên cookie/session tự gửi
  AND attacker dựng được request cú pháp hợp lệ
  AND anti-CSRF check thiếu hoặc bypass được
=> CSRF khả thi
```

## Sai lầm tư duy thường gặp

1. "Dùng POST là an toàn".
2. "Có Referer check là đủ".
3. "Có token là xong" (nhưng token validate sai).
4. "HTTPS tự chống CSRF".
5. "Multi-step workflow thì không CSRF được".

## Ứng dụng cho pentest và kiến trúc phòng thủ

Khi review CSRF, luôn tách 2 lớp:

- Lớp xác thực danh tính: request có đúng user không.
- Lớp xác thực chủ đích: request có thực sự do user chủ động khởi tạo không.

CSRF là bài toán của lớp thứ hai.

## Related Files

- [CSRF Overview](00-overview.md)
- [Root Causes and Conditions](02-root-causes-and-conditions.md)
- [SameSite and Browser Behavior](06-samesite-and-browser-behavior.md)
- [Defense and Mitigation](10-defense-mitigation.md)
