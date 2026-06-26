# Tấn công Delimiter

## Phạm vi module

Module này bao gồm hai nhóm kỹ thuật:

1. **Delimiter discrepancy**: cache và origin khác nhau về ký tự phân tách.
2. **Delimiter decoding discrepancy**: khác nhau ở bước decode ký tự đã URL-encode.

## 1) Delimiter discrepancy

Ví dụ payload:

`/my-account;abc.js`

Kịch bản thường gặp:

- Origin coi `;` là delimiter, cắt path về `/my-account`.
- Cache không coi `;` là delimiter, thấy đường dẫn kết thúc `.js` và cache response.

## 2) Delimiter decoding discrepancy

Ví dụ payload:

`/my-account%23wcd.css`

Kịch bản thường gặp:

- Origin decode `%23` thành `#`, sau đó dùng `#` làm delimiter.
- Cache không decode trước khi áp rule, nên thấy path `%23wcd.css` và cache.

## 3) Quy trình fuzz delimiter

1. Tạo baseline `GET /targetabc` (thường 404).
2. Chèn delimiter candidate: `/target<delim>abc`.
3. So sánh body/status với baseline và base endpoint.
4. Delimiter nào trả về body giống base endpoint thì đánh dấu là delimiter của origin.
5. Thêm extension static: `/target<delim>abc.js`.
6. Kiểm tra cache oracle (`miss -> hit`).

## 4) Bộ ký tự khởi đầu để test

Theo tài liệu tham chiếu, nên test đầy đủ ASCII printable và encoded variants. Các nhóm ưu tiên:

- Plain: `;`, `?`, `#`, `.`, `/`, `:`.
- Encoded: `%23`, `%3f`, `%2f`, `%2e`, `%00`, `%09`, `%0a`.

Chi tiết tập ký tự tham khảo: `reference/delimiter_list.txt`.

## 5) Browser-side caveats

Không phải delimiter nào cũng được gửi nguyên về server:

- `#` thường bị browser dùng làm fragment delimiter ở client-side.
- `{`, `}`, `<`, `>` thường bị encode tự động.

Do đó trong exploit thực tế, encoded variant (`%23`) thường hữu dụng hơn raw `#`.

## 6) Mẫu payload theo nhóm

## Pattern D1: plain delimiter + extension

- `/settings/profile;wcd.js`
- `/my-account;cache.ico`

## Pattern D2: encoded delimiter + extension

- `/my-account%23wcd.css`
- `/my-account%3fwcd.js`

## Pattern D3: delimiter kết hợp traversal

- `/my-account;%2f%2e%2e%2fresources`
- `/my-account%23%2f%2e%2e%2fresources`

Pattern D3 thường dùng trong cache-normalization exploit.

## 7) Định hướng phân tích kết quả

| Kết quả                                         | Diễn giải                                                     |
| ----------------------------------------------- | ------------------------------------------------------------- |
| Delimiter cho body 200 giống base endpoint      | Có khả năng origin đang truncate path                         |
| Thêm `.js` mà không cache                       | Cache có thể cũng dùng delimiter hoặc không có extension rule |
| Encoded variant cache được, plain variant không | Có decoding discrepancy hoặc browser preprocessing            |

## 8) Lỗi thường gặp khi khai thác

1. Quên tắt auto encoding trong công cụ fuzz.
2. Không đổi cache buster mỗi request.
3. Dùng payload có `#` raw trong exploit URL trình duyệt.
4. Kết luận dựa trên một POP của CDN (khi hệ thống có nhiều edge).

## 9) Kết nối với module khác

- [06-normalization-attacks.md](06-normalization-attacks.md): Kết hợp delimiter + traversal.
- [11-payloads-cheatsheet.md](11-payloads-cheatsheet.md): Tập payload nhanh.
- [09-lab-playbooks.md](09-lab-playbooks.md): Kịch bản thực hành theo lab.
