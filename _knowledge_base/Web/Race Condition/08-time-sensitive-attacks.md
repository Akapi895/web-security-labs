# Time-sensitive Attacks (Related to Race Techniques)

## Positioning

Không phải lúc nào timing exploit cũng là race condition thuần. Có trường hợp hệ thống không có va chạm ghi/đọc dữ liệu, nhưng token hoặc state phụ thuộc thời gian quá chặt và có thể đoán/đồng bộ.

Vì vậy, đây là nhóm "timing-sensitive" liên quan chặt với kỹ thuật race delivery.

## Typical Vulnerability Pattern

Token bảo mật được tạo từ thành phần có entropy thấp, ví dụ timestamp độ phân giải cao nhưng không đủ ngẫu nhiên. Khi hai request đến gần như đồng thời, hai user có thể nhận token trùng.

## Distinguish from Classical Race

| Aspect     | Classical Race                 | Time-sensitive Weakness        |
| ---------- | ------------------------------ | ------------------------------ |
| Root cause | Đồng bộ trạng thái sai         | Thiết kế token/entropy yếu     |
| Trigger    | Collision trên shared resource | Đồng bộ thời điểm sinh token   |
| Effect     | Bypass limit, state corruption | Token collision/predictability |

## Exploitation Workflow

1. Quan sát token reset có format ổn định.
2. Gửi nhiều yêu cầu để đánh giá tính biến thiên token.
3. Thử gửi song song hai yêu cầu từ hai session khác nhau để tránh session lock.
4. Tìm lần hai request có thời gian xử lý trùng/khít.
5. Kiểm tra token nhận được có trùng nhau không.
6. Dùng token của account attacker áp cho user mục tiêu nếu thiết kế token không bind chặt theo user.

## Practical Signals

- Cặp email reset chứa cùng token khi request được xử lý gần đồng thời.
- Đổi username trong query nhưng token vẫn hợp lệ.
- Khả năng reset mật khẩu user khác với token của user hiện tại.

## Testing Notes

1. Nếu cùng session bị xử lý tuần tự, tạo session riêng cho mỗi request.
2. Chạy nhiều vòng vì collision theo timestamp có xác suất.
3. Log thời gian response và token để tìm tương quan.

## Defensive Direction

- Token phải được sinh bằng CSPRNG.
- Token cần bind chặt vào user + ngữ cảnh + TTL.
- Mỗi token chỉ dùng một lần và revoke atomically khi consume.

## Related Files

- [06-single-endpoint-race](06-single-endpoint-race.md)
- [10-tooling-burp-and-turbo-intruder](10-tooling-burp-and-turbo-intruder.md)
- [12-defense-mitigation](12-defense-mitigation.md)
