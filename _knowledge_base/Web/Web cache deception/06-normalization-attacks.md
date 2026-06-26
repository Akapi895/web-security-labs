# Tấn công Normalization

## Mục tiêu module

Trình bày hai hướng khai thác chính khi cache và origin normalize URL khác nhau:

1. Origin normalize, cache không normalize (hoặc normalize khác).
2. Cache normalize, origin không normalize (hoặc normalize khác).

## 1) URL normalization là gì

Normalization thường bao gồm:

- Decode ký tự encoded trong path (`%2f`, `%2e`, ...).
- Resolve dot-segment (`.` và `..`).
- Chuẩn hóa path về dạng canonical.

Vấn đề là mỗi parser có thể normalize khác nhau.

## 2) Exploit hướng A: origin normalize mạnh hơn cache

## Ý tưởng

Dùng static directory prefix để cache áp rule, nhưng origin resolve traversal về dynamic endpoint.

## Payload mẫu

`/<static-prefix>/..%2f<dynamic-path>`

Ví dụ:

`/resources/..%2fmy-account`

## Diễn giải

- Cache thấy prefix `/resources` nên có thể cache.
- Origin decode + resolve thành `/my-account` và trả response dynamic.

## 3) Exploit hướng B: cache normalize mạnh hơn origin

## Ý tưởng

Cache resolve traversal để match static rule, origin không resolve nên cần kết hợp delimiter để origin truncate về dynamic path.

## Payload mẫu

`/<dynamic-path><delimiter>%2f%2e%2e%2f<static-prefix>`

Ví dụ:

- `/my-account%23%2f%2e%2e%2fresources`
- `/my-account;%2f%2e%2e%2fresources`

## Diễn giải

- Cache normalize path traversal về `/resources` và cache.
- Origin xử lý delimiter và cắt path về `/my-account`.

## 4) Kiểm tra normalization của origin

1. Chọn endpoint dynamic `/my-account`.
2. Thử `/aaa/..%2fmy-account`.
3. Nếu vẫn trả body của `/my-account`, origin đang decode + resolve.

## 5) Kiểm tra normalization của cache

1. Chọn static resource có bằng chứng được cache (`/resources/js/app.js`).
2. Thử payload trước prefix: `/aaa/..%2fresources/js/app.js`.
3. Thử payload sau prefix: `/resources/..%2fjs/app.js`.
4. So sánh oracle cache để suy luận cache có resolve dot-segment hay không.

## 6) Static directory vs exact file name rules

## Static directory rule

- Match theo prefix (`/static`, `/assets`, `/resources`).
- Dễ khai thác hơn vì có nhiều đường dẫn con.

## Exact file name rule

- Match đúng tên file (`/index.html`, `/favicon.ico`, `/robots.txt`).
- Thường cần cache normalize traversal rất cụ thể mới exploit được.

## 7) Decision tree nhanh

1. Nếu origin normalize, cache không normalize: thử hướng A (`/static/..%2fprofile`).
2. Nếu cache normalize, origin không normalize: thử hướng B + delimiter.
3. Nếu cả hai normalize giống nhau: đổi vector (delimiter/path mapping) hoặc endpoint khác.

## 8) Chỉ báo thành công

- Payload trả body dynamic nhưng đồng thời có dấu hiệu cache.
- Request lại cùng payload cho `hit`.
- Victim priming thành công dẫn đến leak data victim.

## 9) Sai lầm thường gặp

1. Encode sai chuỗi traversal (thiếu `%2f` hoặc `%2e`).
2. Quên rằng browser có thể xử lý một phần path trước khi gửi request.
3. Không xác nhận static directory rule nên hiểu sai lý do cache hit.

## Liên kết đọc tiếp

- [07-cache-rules-key-and-oracles.md](07-cache-rules-key-and-oracles.md)
- [08-exploitation-workflows.md](08-exploitation-workflows.md)
- [09-lab-playbooks.md](09-lab-playbooks.md)
