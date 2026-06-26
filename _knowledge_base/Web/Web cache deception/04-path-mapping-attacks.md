# Tấn công sai lệch Path Mapping

## Mục tiêu module

Phần này mô tả cách khai thác WCD khi cache và origin map URL path theo hai logic khác nhau.

## 1) Bản chất discrepancy

Path mapping discrepancy xuất hiện khi:

- Origin route theo kiểu REST, có thể bỏ qua một số segment.
- Cache map theo kiểu file path đầy đủ và match static extension.

Ví dụ payload:

`/user/123/profile/wcd.css`

Có thể được hiểu như sau:

- Origin: `/user/123/profile`.
- Cache: request tới file `.css` trong path đầy đủ.

Nếu cache có rule cho `.css`, response dynamic có thể bị lưu.

## 2) Điều kiện thành công

1. Endpoint dynamic phải trả về data nhạy cảm.
2. Origin phải có xu hướng abstraction/bỏ qua segment cuối.
3. Cache phải có rule extension cho static file.

## 3) Quy trình khai thác

1. **Chọn endpoint**: ví dụ `/my-account`.
2. **Test segment thêm**: `/my-account/abc` và `/my-accountabc`.
3. **Thêm extension static**: `/my-account/abc.js` hoặc `/my-account;wcd.js`.
4. **Xác nhận cache oracle**: `miss -> hit`.
5. **Victim priming**: buộc victim truy cập URL độc hại.
6. **Harvest**: attacker truy cập lại cùng URL để lấy dữ liệu đã cache.

## 4) Payload templates

## Pattern A: extra path segment

- `/api/orders/123/foo.js`
- `/profile/wcd.css`

## Pattern B: fake static file in route tail

- `/my-account/non-existent.css`
- `/session/current/wcd.ico`

## Pattern C: kết hợp với delimiter

- `/my-account;wcd.js`

Pattern C thực chất giao nhau với delimiter discrepancy, nhưng thường được dùng để khởi động exploit nhanh.

## 5) Dấu hiệu exploit đã thành công

- Payload trả về nội dung dynamic của victim.
- Header/behavior cache cho thấy object được lưu.
- Request tiếp theo của attacker trả về cùng dữ liệu, không cần session victim.

## 6) Hạn chế và rủi ro đánh giá

1. Parser behavior có thể khác giữa endpoint trong cùng app.
2. Một số route framework reject extension là không hợp lệ.
3. Nếu CDN không cache HTML/dynamic hoặc có armor, exploit có thể thất bại.

## 7) Mapping với lab thực chiến

Kịch bản lab tương ứng thường theo logic:

1. Đăng nhập để xem endpoint trả API key.
2. Fuzz delimiter/segment tìm payload trả body đúng.
3. Kiểm tra `X-Cache` và transition `miss -> hit`.
4. Gửi exploit buộc victim truy cập URL mới (cache buster).
5. Truy cập lại URL để lấy API key của victim.

## 8) Kỹ thuật mở rộng

- Thử nhiều extension (`.css`, `.js`, `.ico`, `.exe`) vì rule có thể đặc thù theo CDN.
- Kết hợp cache buster để tránh contaminate object cũ.
- Nếu browser can thiệp ký tự đặc biệt, thử encoded variant.

## Liên kết đọc tiếp

- [05-delimiter-attacks.md](05-delimiter-attacks.md)
- [06-normalization-attacks.md](06-normalization-attacks.md)
- [09-lab-playbooks.md](09-lab-playbooks.md)
