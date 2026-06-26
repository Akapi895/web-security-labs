# Detection and Scoping Methodology

## Goal

Phát hiện race condition hiệu quả không phải là spam mọi endpoint, mà là xác định đúng điểm có collision potential và chứng minh sai lệch trạng thái có ý nghĩa bảo mật.

## Predict, Probe, Prove

### 1. Predict Potential Collisions

Ưu tiên endpoint thỏa 3 điều kiện:

1. Security-critical: ảnh hưởng auth, quyền, tiền, token, hạn mức.
2. Shared key: nhiều request có thể chạm cùng bản ghi (username, account, order, session).
3. Multi-step processing: check và update tách rời.

Ví dụ chức năng ưu tiên kiểm tra:

- Chuyển tiền, nạp/rút, ví điện tử.
- Reset mật khẩu, đổi email, xác minh tài khoản.
- Checkout, coupon, gift card, loyalty points.
- Bộ đếm chống brute-force, CAPTCHA one-time.

### 2. Probe for Clues

Quy trình probe chuẩn:

1. Benchmark tuần tự (sequential) để lấy hành vi bình thường.
2. Gửi song song (parallel) để ép collision.
3. So sánh response + side effects bậc hai.

Clue cần theo dõi:

- Nhiều response thành công vượt giới hạn mong đợi.
- Trạng thái sau cùng bất nhất với business rule.
- Email gửi sai người nhận hoặc chứa dữ liệu sai user.
- Số dư, quota, role, trạng thái đơn không hợp lệ.

### 3. Prove the Concept

Sau khi có dấu hiệu:

1. Loại request dư thừa.
2. Giảm số request về mức tối thiểu để tái lập.
3. Đo tỷ lệ thành công qua nhiều lần chạy.
4. Chứng minh impact nghiệp vụ (không chỉ response anomaly).

## Scoping Matrix

| Question                                         | If Yes                           | If No                  |
| ------------------------------------------------ | -------------------------------- | ---------------------- |
| Endpoint có tác động bảo mật/tài chính?          | Đưa vào scope ưu tiên cao        | Giảm ưu tiên           |
| Nhiều request cùng chạm một key dữ liệu?         | Có collision potential           | Khả năng race thấp     |
| Có trạng thái trung gian hoặc async side effect? | Tập trung tìm hidden sub-state   | Chỉ test TOCTOU cơ bản |
| Có cơ chế lock theo session?                     | Dùng nhiều session để kiểm chứng | Test bình thường       |

## Identifying Race Window

Race window thường nằm giữa:

- Check limit -> Increment counter.
- Validate payment -> Confirm order.
- Store pending email -> Render/send confirmation.
- Create user record -> Store verification token.

## Session Locking Considerations

Một số framework xử lý tuần tự request trong cùng session. Điều này có thể che khuất lỗ hổng.

Cách kiểm tra:

1. Gửi song song cùng session, quan sát response time gần như nối đuôi.
2. Lặp lại với hai session khác nhau.
3. Nếu song song tốt hơn rõ rệt, lock theo session đang che race.

## False Positives and Noise Control

Nhiễu thường gặp:

- Network jitter.
- Backend connection setup delay.
- Cache warm-up effects.

Cách giảm nhiễu:

- Chạy baseline đủ số mẫu.
- Dùng kỹ thuật đồng bộ request chuyên dụng.
- Thêm bước connection warming nếu cần.

## Minimal Evidence for a Valid Finding

Một finding race condition nên có:

1. Điều kiện tái lập rõ ràng.
2. Cặp request/song song minh họa collision.
3. Bằng chứng state vi phạm business invariant.
4. Mức impact nghiệp vụ và bảo mật cụ thể.

## Related Files

- [04-limit-overrun-toctou](04-limit-overrun-toctou.md)
- [05-multi-endpoint-race](05-multi-endpoint-race.md)
- [06-single-endpoint-race](06-single-endpoint-race.md)
- [10-tooling-burp-and-turbo-intruder](10-tooling-burp-and-turbo-intruder.md)
