# Nguyên nhân gốc rễ của Web Cache Deception

## Tổng quan

WCD hiếm khi đến từ một lỗi đơn lẻ. Nó thường là kết quả của **chuỗi sai lệch liên thành phần**:

- Cache layer áp dụng rule nhanh, thường dựa trên string.
- Origin layer route theo framework parser, có delimiter và normalization riêng.
- Cấu hình cache ghi đè (override) policy của origin.

## Nhóm nguyên nhân gốc rễ

## 1) Path parsing và path mapping discrepancy

Hai bên có thể map cùng URL theo hai cách:

- Cache: map theo file-path truyền thống.
- Origin: map theo REST route và bỏ qua một phần segment.

Ví dụ: `/user/123/profile/wcd.css`

- Origin có thể trả profile của user 123.
- Cache có thể coi đây là file `.css` hợp lệ để lưu.

## 2) Delimiter discrepancy

Một ký tự là delimiter ở origin nhưng không phải delimiter ở cache (hoặc ngược lại):

- `;`, `?`, `#`, `%23`, `%3f`, `%00`, ...

Ví dụ `/my-account;foo.js`:

- Origin cắt path tại `;` và trả `/my-account`.
- Cache giữ toàn bộ chuỗi và kích hoạt rule extension `.js`.

## 3) Delimiter decoding discrepancy

Cả hai bên có thể đều biết delimiter, nhưng khác nhau ở việc decode URL:

- Origin decode `%23` thành `#` trước khi parse.
- Cache không decode trước khi áp rule.

Kết quả: cùng request nhưng logic parse khác nhau.

## 4) Normalization discrepancy

Khác biệt trong quá trình normalize path (decode slash, resolve dot-segment):

- Origin normalize mạnh, cache normalize yếu.
- Hoặc cache normalize mạnh, origin normalize yếu.

Đây là nền tảng cho các payload traversal dạng `..%2f`.

## 5) Cache rule thiếu context nội dung

Rule chỉ dựa vào extension/prefix/file name mà không xác nhận:

- Response content-type có phù hợp với extension hay không.
- Endpoint có mang tính private/user-specific hay không.

## 6) Cache key và policy không đủ phân biệt ngữ cảnh

Nếu cache key không đưa vào user/session context cho response động, nguy cơ rò rỉ dữ liệu tăng cao.

Lưu ý: Đây không phải điều kiện bắt buộc duy nhất để tạo WCD, nhưng là yếu tố bổ trợ quan trọng cho impact.

## 7) Không nhất quán giữa web server, CDN, reverse proxy, framework

Mỗi lớp có parser riêng:

- CDN/reverse proxy parse theo implementation riêng.
- Web server parse URI/routing theo bộ quy tắc riêng.
- Framework (Spring, Rails, ...) có delimiter/formatter behavior riêng.

Nếu thiếu một quy ước canonical chung, discrepancy sẽ xuất hiện.

## Mapping nguyên nhân -> biểu hiện -> hướng kiểm chứng

| Nguyên nhân                    | Dấu hiệu                                 | Hướng test                              |
| ------------------------------ | ---------------------------------------- | --------------------------------------- |
| Path mapping mismatch          | Thêm segment vẫn trả dynamic data        | Thử `/endpoint/abc`, `/endpoint/abc.js` |
| Delimiter mismatch             | Một số ký tự giữ nguyên body gốc         | Fuzz ký tự delimiter sau path gốc       |
| Decode mismatch                | Bản mã hóa cho kết quả khác bản thường   | Test `%23`, `%3f`, `%00`, `%0a`, `%09`  |
| Normalize mismatch             | Payload traversal cho kết quả bất thường | Test `..%2f` trước/sau static prefix    |
| Rule extension/prefix quá rộng | URL giống static nhưng trả dynamic       | Thử `.css`, `.js`, `.ico`, static dir   |

## Điều kiện cần và đủ để khai thác

Trong thực tế, thường cần:

1. Dynamic endpoint có thông tin nhạy cảm.
2. Có ít nhất một discrepancy parser/rule.
3. Có cache behavior quan sát được (`miss -> hit`).
4. Có khả năng buộc nạn nhân truy cập payload URL.

## Anti-pattern kiến trúc thường gặp

- Tin rằng chỉ cần set `Cache-Control` là đủ, nhưng CDN đang override.
- Cho phép parser “linh hoạt” quá mức với delimiter/normalized paths.
- Rule cache theo extension mà không đối chiếu `Content-Type`.
- Không có bộ test parser parity giữa edge và origin.

## Hệ quả theo chuỗi

1. Sai lệch parser tạo URL mơ hồ.
2. Rule cache bị kích hoạt nhầm.
3. Response private bị lưu ở key công khai.
4. Kẻ tấn công truy cập lại key đó để thu hồi dữ liệu.

## Liên kết đọc tiếp

- [03-attack-surface-and-detection.md](03-attack-surface-and-detection.md)
- [04-path-mapping-attacks.md](04-path-mapping-attacks.md)
- [05-delimiter-attacks.md](05-delimiter-attacks.md)
- [06-normalization-attacks.md](06-normalization-attacks.md)
