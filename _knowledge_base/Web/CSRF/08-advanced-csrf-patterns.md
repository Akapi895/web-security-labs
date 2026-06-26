# Advanced CSRF Patterns

## Mục tiêu

Phần này tập trung vào các pattern CSRF vượt ngoài PoC cơ bản, bao gồm các chuỗi tấn công có tác động cao và khó phát hiện hơn.

## 1. Login CSRF

## Khái niệm

Attacker ép nạn nhân đăng nhập vào tài khoản do attacker kiểm soát. Nạn nhân tưởng là tài khoản của họ, tiếp tục thao tác và vô tình đẩy dữ liệu vào account attacker.

## Tác động

- Rò rỉ thông tin cá nhân nạn nhân vào account attacker.
- Mở đường cho chain với stored XSS hoặc thao tác hậu kỳ khác.

## Điều kiện

- Login endpoint thiếu CSRF protection.
- Không có cơ chế xác nhận user context rõ ràng sau login.

## 2. Stored CSRF

## Khái niệm

Payload CSRF được lưu vào nội dung hệ thống (comment, profile, rich text HTML). Bất kỳ user phù hợp quyền khi xem nội dung đó đều tự kích hoạt request forged.

## Tại sao nguy hiểm

- Delivery tự động, không cần phishing link riêng cho từng nạn nhân.
- Tỷ lệ kích hoạt cao hơn do payload nằm ngay trong ứng dụng mục tiêu.

## 3. CSRF chain với XSS

## Chiều kết hợp thường gặp

- CSRF -> đổi trạng thái để mở đường XSS.
- XSS -> đọc token rồi thực thi action cần token.

XSS có thể biến CSRF từ one-way thành full two-way attack chain.

## 4. Token exfiltration assisted attacks

Nếu có XSS hoặc lỗi đọc DOM phù hợp, attacker có thể:

1. Lấy token từ form/page protected.
2. Gửi token ra ngoài.
3. Dùng token để thực thi action protected trong phiên nạn nhân.

## 5. WebSocket handshake hijacking (CSWSH-like)

Trong một số hệ thống, handshake WebSocket dựa trên cookie và thiếu CSRF-like origin checks. Đây là biến thể cross-site request abuse cần đánh giá song song khi app dùng WS.

## 6. Business-logic amplified CSRF

CSRF nghiêm trọng hơn khi action có hiệu ứng dây chuyền:

- Đổi email -> reset password -> takeover.
- Bật webhook độc hại -> data exfiltration liên tục.
- Đổi cấu hình thanh toán -> chiếm dòng tiền.

## Ma trận pattern và mức rủi ro

| Pattern                  | Độ khó khai thác   | Tác động tiềm năng |
| ------------------------ | ------------------ | ------------------ |
| Login CSRF               | Trung bình         | Trung bình đến cao |
| Stored CSRF              | Trung bình         | Cao                |
| CSRF + XSS chain         | Cao hơn            | Rất cao            |
| Token exfiltration chain | Cao                | Rất cao            |
| Business-logic amplified | Phụ thuộc hệ thống | Rất cao            |

## Dấu hiệu cần săn trong assessment

- Endpoint login không có anti-CSRF signal.
- Chức năng cho phép HTML/user content render lại cho user khác.
- Workflow thay đổi danh tính không yêu cầu re-auth.
- Các endpoint admin có side effect lớn nhưng bảo vệ không đồng nhất.

## Góc nhìn phòng thủ

1. Bảo vệ CSRF phải bao phủ cả login và workflow thiết lập session.
2. Tách quyền và step-up auth cho action high-impact.
3. Kiểm soát nghiêm render HTML user-generated để giảm stored chains.
4. Kết hợp CSRF controls với XSS hardening (output encoding, CSP, sanitization).

## Related Files

- [Exploitation Workflow](04-exploitation-workflow.md)
- [Payloads Cheatsheet](09-payloads-cheatsheet.md)
- [Defense and Mitigation](10-defense-mitigation.md)
- [Lab Design and Agent Training](11-lab-design-and-agent-training.md)
