# Quy tắc cache, cache key và oracle

## Vì sao module này quan trọng

Nhiều trường hợp WCD thất bại không phải vì không có sai lệch, mà vì tester không nắm được:

- Quy tắc nào đang kích hoạt cache.
- Key nào đang xác định object cache.
- Oracle nào đang cho tín hiệu chính xác.

## 1) Các quy tắc cache thường gặp trong WCD

## Quy tắc dựa trên extension

- Cache nếu URL kết thúc `.css`, `.js`, `.ico`, `.exe`, ...

## Quy tắc dựa trên thư mục

- Cache nếu path có prefix `/static`, `/assets`, `/resources`, `/images`.

## Quy tắc dựa trên tên tệp

- Cache nếu path khớp tên file cụ thể (`/favicon.ico`, `/robots.txt`).

WCD dùng sai lệch parser để đưa dynamic response vào URL thỏa các quy tắc trên.

## 2) Cache key và ý nghĩa trong khai thác

Cache key là định danh object lưu trong cache. Thường bao gồm:

- Path.
- Query string (toàn bộ hoặc một phần).
- Host/scheme.
- Một số header được include theo cấu hình.

Trong pentest WCD, key giúp bạn:

1. Tránh đọc object cũ (dùng cache buster).
2. Kiểm soát victim priming và attacker harvesting cùng một key.

## 3) Chiến lược cache buster

Mẫu đơn giản:

- `?cb=<timestamp-or-random>`

Nguyên tắc:

- Mỗi lần test parser discrepancy: đổi `cb`.
- Mỗi lần victim priming: dùng key mới so với key của tester.

## 4) Oracle để xác định hành vi cache

## Oracle dựa trên header

| Header              | Giải thích                                            |
| ------------------- | ----------------------------------------------------- |
| `X-Cache: miss/hit` | Tín hiệu phổ biến để kiểm tra object đã được lưu chưa |
| `CF-Cache-Status`   | Oracle đặc thù Cloudflare                             |
| `Age`               | Tuổi object trong cache                               |
| `Via`               | Có thể cho thấy request qua cache hop nào             |

## Oracle dựa trên timing

Request thứ 2 nhanh hơn request thứ 1 là dấu hiệu bổ trợ cho cache hit.

## 5) Giá trị tham chiếu của một số trạng thái

Theo tài liệu tham khảo:

- `hit`: trả từ cache.
- `miss`: cache chưa có object, vừa forward tới origin.
- `dynamic`: nội dung động, thường không phù hợp để cache.
- `refresh`: object hết hạn, vừa được revalidate/làm mới.

## 6) Tình huống dễ gây nhầm lẫn

1. 404 cũng có thể bị cache (không đồng nghĩa exploit thành công).
2. `Cache-Control` có thể nói `no-store`, nhưng edge có cấu hình override.
3. Nhiều POP edge cho kết quả khác nhau ở từng thời điểm.

## 7) Cloudflare ghi chú thực chiến

Tài liệu tham khảo cho thấy:

- Cloudflare thường cache dựa trên extension mặc định.
- Có cơ chế Cache Deception Armor (nếu bật) để đối chiếu extension và `Content-Type`.

Ý nghĩa pentest:

- Nếu armor bật, payload extension mismatch có thể bị chặn cache.
- Nếu armor tắt, rủi ro WCD tăng rõ ràng.

## 8) Quy trình xác nhận chất lượng kết quả

1. Xác nhận discrepancy parser độc lập (không cần cache).
2. Xác nhận cache rule được kích hoạt độc lập (trên static resource).
3. Kết hợp hai điều kiện trên cùng một payload WCD.
4. Xác nhận `miss -> hit` và leak dữ liệu victim.

## 9) Điểm kiểm tra cho báo cáo pentest

- Quy tắc bị lỗi: extension/prefix/file-name.
- Sai lệch loại nào: mapping/delimiter/decoding/normalization.
- Oracle nào được dùng để xác nhận.
- Điều kiện để tái hiện (payload + key + victim flow).
- Mức độ rủi ro business.

## Liên kết đọc tiếp

- [08-exploitation-workflows.md](08-exploitation-workflows.md)
- [10-defense-mitigation.md](10-defense-mitigation.md)
- [11-payloads-cheatsheet.md](11-payloads-cheatsheet.md)
