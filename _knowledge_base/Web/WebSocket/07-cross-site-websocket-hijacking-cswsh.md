# Cross-Site WebSocket Hijacking (CSWSH)

## Định nghĩa

CSWSH là trường hợp đặc biệt của CSRF trên handshake WebSocket: trang độc hại mở socket tới ứng dụng đích và trình duyệt nạn nhân tự động gửi cookie phiên, khiến server nhầm đó là kết nối hợp lệ của người dùng thật.

## Chuỗi tấn công điển hình

1. Nạn nhân đã đăng nhập vào ứng dụng đích.
2. Nạn nhân truy cập trang do attacker kiểm soát.
3. JavaScript trên trang độc hại mở kết nối WebSocket tới đích.
4. Cookie phiên được gửi kèm theo handshake.
5. Nếu server không kiểm soát origin/chống CSRF đúng cách, kết nối được chấp nhận.
6. Attacker gửi/nhận message trong ngữ cảnh phiên nạn nhân.

## Điều kiện cần để CSWSH khai thác được

| Điều kiện                                                   | Giải thích                                                               |
| ----------------------------------------------------------- | ------------------------------------------------------------------------ |
| Ứng dụng xác thực dựa trên cookie                           | Trình duyệt tự động gửi cookie khi mở WebSocket                          |
| Origin check thiếu hoặc yếu                                 | Không ngăn được kết nối từ site lạ                                       |
| Không có token chống giả mạo handshake                      | Không có bằng chứng phía client hợp lệ ngoài cookie                      |
| Cookie policy cho phép gửi cross-site trong ngữ cảnh cụ thể | Ví dụ cấu hình `SameSite` không phù hợp hoặc bối cảnh localhost/intranet |

## Biến thể thực tế cần chú ý

1. Tấn công từ subdomain bị chiếm quyền script trong cùng hệ sinh thái domain.
2. Lạm dụng WebSocket local/intranet (127.0.0.1 hoặc mạng nội bộ) qua trình duyệt.
3. Endpoint chấp nhận mọi origin (ví dụ cấu hình check origin luôn true).

## Dấu hiệu phát hiện nhanh

1. Handshake thành công khi `Origin` không thuộc danh sách tin cậy.
2. Không có cơ chế ràng buộc anti-CSRF riêng cho WebSocket.
3. Cùng cookie phiên có thể mở socket từ trang ngoài ứng dụng chính.

## Hệ quả bảo mật

1. Đọc dữ liệu real-time của nạn nhân.
2. Thực thi hành động trái phép thay mặt nạn nhân.
3. Kết hợp với lỗi message-level để leo thang impact.

## Kiểm thử CSWSH có kiểm soát

1. Dùng môi trường lab với origin hợp lệ và origin không hợp lệ.
2. So sánh kết quả handshake theo từng trạng thái cookie/session.
3. Xác minh khả năng gửi message thao tác nghiệp vụ sau khi kết nối.
4. Ghi nhận đầy đủ precondition và giới hạn trình duyệt/chính sách cookie.

## Phòng thủ trọng tâm

1. Bắt buộc allowlist `Origin` chính xác theo domain/port/scheme.
2. Không chỉ dựa vào cookie; bổ sung token chống giả mạo cho handshake.
3. Dùng `SameSite` phù hợp và rà soát luồng cần cross-site hợp lệ.
4. Kiểm quyền theo từng message, không xem handshake là đủ.
5. Đóng toàn bộ socket khi logout hoặc session hết hạn.

## Sai lầm triển khai thường gặp

1. Kiểm tra origin bằng `contains("example.com")`.
2. Dùng wildcard origin để "tiện phát triển" rồi quên siết ở production.
3. Áp dụng CSRF cho HTTP form nhưng bỏ qua WebSocket handshake.

## Tệp liên quan

- [Lỗi handshake và auth bypass](06-handshake-manipulation-and-auth-bypass.md)
- [Phiên và authorization trong kênh stateful](08-session-authorization-and-stateful-risks.md)
- [Phòng thủ và giảm thiểu](13-defense-mitigation.md)
- [Kịch bản lab và huấn luyện agent](14-labs-and-agent-training-scenarios.md)
