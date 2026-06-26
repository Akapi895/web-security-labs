# Nền tảng caching cho Web Cache Deception

## Vì sao cần hiểu caching khi nghiên cứu WCD

WCD là lỗi nằm ở giao điểm của networking, HTTP caching và URL parsing. Nếu không nắm rõ cache hoạt động như thế nào, rất dễ nhầm WCD với lỗi route hoặc lỗi auth thông thường.

## Kiến trúc cache web cơ bản

Trong hệ thống hiện đại, cache có thể tồn tại ở nhiều lớp:

1. Browser cache.
2. CDN edge cache.
3. Reverse proxy cache.
4. Application-level cache.

Trong WCD, lớp quan trọng nhất thường là CDN/reverse proxy nằm giữa người dùng và origin.

## Dynamic content và cached content

| Loại nội dung   | Đặc điểm                                                         | Cache policy mong đợi            |
| --------------- | ---------------------------------------------------------------- | -------------------------------- |
| Static content  | Ít thay đổi, dùng chung cho nhiều người dùng (css/js/image/font) | Có thể cache công khai, TTL dài  |
| Dynamic content | Phụ thuộc session/user context (my-account, profile, order)      | Thường `private` hoặc `no-store` |

WCD xảy ra khi dynamic content bị cache layer nhầm là static content.

## Cách cache xác định một response có được tái sử dụng hay không

Cache tính toán **cache key** từ request. Nếu key trùng với object đã lưu, cache trả về bản sao response (cache hit). Nếu không, cache forward tới origin (cache miss).

Thành phần cache key thường gặp:

- URL path.
- Query string (toàn bộ hoặc một phần).
- Một số header được include (tùy cấu hình).
- Content-type, host, scheme hoặc custom dimensions.

## Cache rules phổ biến

Nhiều hệ thống cache dựa trên string matching trong URL:

1. **Static file extension rule**: cache nếu đường dẫn kết thúc `.css`, `.js`, `.ico`, ...
2. **Static directory rule**: cache nếu path có prefix `/static`, `/assets`, `/resources`, ...
3. **Exact file name rule**: cache nếu path khớp `robots.txt`, `favicon.ico`, `index.html`, ...

WCD tấn công trực tiếp vào các rule này bằng cách tạo URL mơ hồ.

## Header quan trọng cần quan sát

| Header                        | Ý nghĩa thực tế trong test                                        |
| ----------------------------- | ----------------------------------------------------------------- |
| `X-Cache` / `CF-Cache-Status` | Oracle nhận biết `miss`, `hit`, `dynamic`, `refresh`              |
| `Age`                         | Tuổi của object trong cache                                       |
| `Cache-Control`               | Chỉ báo cacheability (`public`, `private`, `no-store`, `max-age`) |
| `Vary`                        | Thành phần request được đưa vào key theo header                   |

Lưu ý: Header response có thể không phản ánh chính xác hành vi thực tế nếu CDN override policy.

## Ví dụ sai lệch cơ bản dẫn đến WCD

Giả sử endpoint nhạy cảm là `/my-account`:

- Origin coi `/my-account;abc.js` là `/my-account` do `;` được xử lý như delimiter.
- Cache không coi `;` là delimiter, thấy đường dẫn kết thúc bằng `.js` và cache response.

Kết quả: response dynamic của `/my-account` bị lưu và phát lại qua URL có vẻ ngoài là static.

## Cache buster trong quá trình đánh giá

Trong pentest WCD, mỗi request nên có key khác nhau để tránh đọc nhầm dữ liệu đã cache trước đó.

Kỹ thuật đơn giản:

- Thêm query cache buster, ví dụ `?wcd=1711223344`.
- Đổi giá trị cache buster mỗi lần gửi request.

## Sai lầm thường gặp khi phân tích

1. Chỉ nhìn body mà bỏ qua oracle header/timing.
2. Dùng lại URL cũ làm kết quả bị nhiễm cache từ request trước.
3. Kết luận quá sớm từ 1 endpoint, trong khi parser behavior có thể khác theo route.

## Kết nối với các module tiếp theo

- [02-root-causes.md](02-root-causes.md): Giải thích tại sao parser có thể lệch nhau.
- [03-attack-surface-and-detection.md](03-attack-surface-and-detection.md): Quy trình phát hiện endpoint và cacheability.
- [07-cache-rules-key-and-oracles.md](07-cache-rules-key-and-oracles.md): Đào sâu vào cache key/rule/oracle.
