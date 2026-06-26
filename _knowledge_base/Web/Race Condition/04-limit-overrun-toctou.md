# Limit Overrun and TOCTOU Race Conditions

## Core Idea

Limit overrun là dạng race condition cổ điển: hệ thống kiểm tra giới hạn ở đầu luồng, nhưng việc cập nhật trạng thái giới hạn xảy ra trễ hơn. Kẻ tấn công gửi nhiều request trong race window để vượt giới hạn.

Đây là một biến thể của TOCTOU (time-of-check to time-of-use).

## Typical Targets

- Coupon/gift card chỉ dùng một lần.
- Số lần thử đăng nhập sai tối đa.
- CAPTCHA one-time.
- Vote/rating một lần mỗi user.
- Số dư tài khoản khi chuyển/rút tiền.

## Canonical State Transition

1. Check: `can_perform_action == true`
2. Apply action.
3. Update: `can_perform_action = false` hoặc `counter += 1`

Race window nằm giữa bước 1 và bước 3.

## Exploitation Sequence

1. Xác nhận endpoint có giới hạn và ảnh hưởng bảo mật/tài chính.
2. Benchmark gửi tuần tự để xác lập phản hồi chuẩn.
3. Gửi song song N request cùng payload.
4. Quan sát số response thành công vượt mức cho phép.
5. Kiểm tra trạng thái cuối cùng để chứng minh impact.

## Practical Indicators

- Response tuần tự: 1 thành công, còn lại bị từ chối.
- Response song song: nhiều request cùng báo thành công.
- State cuối cùng phản ánh nhiều lần áp dụng action.

## Stabilization Tips

1. Tăng số request song song để bù server-side jitter.
2. Lặp nhiều đợt tấn công nếu race window ngắn.
3. Giữ request tối giản để giảm sai số timing.
4. Cô lập yếu tố thay đổi (session, CSRF token, cache state).

## Example Scenario: Coupon Reuse

- Hệ thống cho mã giảm giá 20% một lần.
- Gửi đồng thời nhiều request apply coupon.
- Nhiều request vượt qua check trước khi DB ghi nhận mã đã dùng.
- Tổng tiền giảm nhiều lần ngoài thiết kế.

## Risk and Business Impact

| Domain         | Impact                                  |
| -------------- | --------------------------------------- |
| E-commerce     | Mua hàng dưới giá, thất thoát doanh thu |
| Finance        | Over-withdraw/over-transfer             |
| Authentication | Brute-force bypass do vượt ngưỡng khóa  |
| Anti-abuse     | Vượt quota và spam hành động            |

## Defensive Direction

Fix đúng bản chất là đảm bảo check + update diễn ra atomically trên cùng resource key, không tách rời theo nhiều thao tác độc lập.

## Related Files

- [03-detection-and-scoping](03-detection-and-scoping.md)
- [10-tooling-burp-and-turbo-intruder](10-tooling-burp-and-turbo-intruder.md)
- [12-defense-mitigation](12-defense-mitigation.md)
