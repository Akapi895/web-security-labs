# Bề mặt tấn công và phát hiện

## Mục tiêu module

Module này trả lời ba câu hỏi:

1. Endpoint nào có khả năng trở thành điểm WCD?
2. Làm sao xác định cache có đang lưu response hay không?
3. Làm sao phân biệt discrepancy thật với false positive?

## 1) Khoanh vùng endpoint mục tiêu

Ưu tiên endpoint có đặc điểm:

- Trả về dữ liệu cá nhân: `/my-account`, `/profile`, `/orders`, `/api/auth/session`.
- Sử dụng method idempotent (GET/HEAD/OPTIONS).
- Có response phụ thuộc session đăng nhập.

Không nên bắt đầu từ endpoint thay đổi state (POST đặt hàng, PUT update profile) vì thường không bị cache.

## 2) Thiết lập baseline trước khi fuzz

Với mỗi endpoint, cần lưu 3 mốc:

1. Response gốc (`/target`).
2. Response path sai có ý (`/targetabc` hoặc `/target/abc`).
3. Header/timing làm oracle cache (`X-Cache`, `Age`, `CF-Cache-Status`, thời gian đáp ứng).

Baseline giúp phân biệt:

- Origin đang route thế nào.
- Cache đang lưu hay không.

## 3) Luôn dùng cache buster khi thử nghiệm

Nếu không đổi cache key mỗi lần test, bạn có thể đọc phải object đã cache trước đó và kết luận sai.

Mẫu thực hành:

- `GET /target;abc.js?wcd=1711223344`
- Tăng `wcd` mỗi request.

## 4) Phát hiện cached response

## Oracle header phổ biến

- `X-Cache: miss -> hit`
- `CF-Cache-Status: MISS -> HIT`
- `Age` tăng dần

## Oracle timing

Request thứ hai nhanh hơn đáng kể request đầu trong điều kiện giống nhau.

Lưu ý: timing chỉ là tín hiệu bổ trợ, không dùng một mình để kết luận.

## 5) Quy trình detection đề xuất

1. Xác nhận endpoint dynamic có dữ liệu nhạy cảm.
2. Test path mapping cơ bản (`/target/abc`, `/targetabc`).
3. Fuzz delimiter sau path gốc (`;`, `?`, `%23`, `%3f`, ...).
4. Test static extension (`.css`, `.js`, `.ico`, `.exe`) để kích hoạt rule.
5. Test normalization (`..%2f`) với static directory.
6. Kiểm tra `miss -> hit` trên cùng payload.
7. Thử exploit với victim simulation + cache buster.

## 6) Matrix quick triage

| Hiện tượng                                       | Diễn giải khả năng cao                        | Hành động tiếp                                |
| ------------------------------------------------ | --------------------------------------------- | --------------------------------------------- |
| `/target/abc` vẫn trả data gốc                   | Origin abstraction hoặc route permissive      | Thử thêm `.js` và kiểm tra cache              |
| `;` cho body giống base, `.js` có `X-Cache: hit` | Delimiter discrepancy có thể khai thác        | Chuyển qua xây payload exploit                |
| `%23` có tác dụng, `#` không                     | Browser xử lý `#` trước, encoded mới hữu dụng | Ưu tiên encoded delimiter                     |
| `..%2f` thay đổi hành vi cache/origin            | Normalization discrepancy                     | Thử payload theo hướng origin/cache normalize |

## 7) Tránh false positive

1. Response redirect tới login do hết session.
2. 404 vẫn bị cache theo rule khác, không liên quan endpoint nhạy cảm.
3. CDN có behavior khác theo region/POP.
4. Browser có thể tự encode delimiter, làm payload không tới được cache.

## 8) Tiêu chí xác nhận vulnerability

Chỉ nên kết luận WCD khi đạt đủ các điều kiện:

1. Có payload tạo ra sự sai lệch parser rõ ràng.
2. Response dynamic có dấu hiệu được cache.
3. Kẻ tấn công gọi lại cùng URL/KEY và nhận được dữ liệu nhạy cảm của victim.

## Liên kết đọc tiếp

- [04-path-mapping-attacks.md](04-path-mapping-attacks.md)
- [05-delimiter-attacks.md](05-delimiter-attacks.md)
- [06-normalization-attacks.md](06-normalization-attacks.md)
- [11-payloads-cheatsheet.md](11-payloads-cheatsheet.md)
