# Race condition trong luồng real-time WebSocket

## Mục tiêu

Mô tả cách race condition xuất hiện trong hệ thống WebSocket và cách kiểm thử có hệ thống.

## Vì sao WebSocket dễ phát sinh race

1. Kết nối dài hạn cho phép gửi nhiều message gần như đồng thời.
2. Ứng dụng real-time thường tối ưu độ trễ, dễ bỏ qua khóa nghiệp vụ.
3. Cùng tài nguyên có thể bị thao tác từ nhiều socket/tab/device.

## Mẫu race phổ biến

| Mẫu race            | Mô tả                                                 | Tác động                                 |
| ------------------- | ----------------------------------------------------- | ---------------------------------------- |
| Double-submit       | Hai message thực thi cùng hành động gần như đồng thời | Trừ tiền/đặt lệnh/đổi trạng thái hai lần |
| Check-then-act race | Kiểm tra điều kiện và cập nhật không atomically       | Vượt hạn mức, bypass kiểm soát           |
| Token/nonce reuse   | Token một lần bị tiêu thụ nhiều lần                   | Lạm dụng tác vụ đặc quyền                |
| Sequence race       | Message đến sai thứ tự nhưng vẫn được chấp nhận       | Desync trạng thái, thực thi trái logic   |

## Điều kiện cần để khai thác race thành công

1. Có thao tác có side effect trên tài nguyên chia sẻ.
2. Thiếu đồng bộ hoặc thiếu idempotency ở backend.
3. Attacker gửi được nhiều message song song hoặc qua nhiều kết nối.

## Quy trình kiểm thử race qua WebSocket

1. Xác định action có nguy cơ cao (thanh toán, redeem, cập nhật quota, phát hành token).
2. Ghi nhận precondition và trạng thái ban đầu.
3. Phát sinh nhiều kết nối/luồng gửi cùng payload trong cửa sổ thời gian hẹp.
4. So sánh kết quả thực tế với invariant nghiệp vụ.
5. Lặp lại với mức concurrency khác nhau để đánh giá độ ổn định của lỗi.

## Chỉ báo xác nhận race

1. Hệ thống ghi nhận nhiều side effect khi chỉ một side effect được phép.
2. Số dư/trạng thái cuối không khớp ràng buộc nghiệp vụ.
3. Log cho thấy cùng user/action được chấp nhận cùng timestamp.

## Giảm thiểu kỹ thuật

1. Dùng thao tác atomically ở DB hoặc lock phù hợp theo tài nguyên.
2. Áp dụng idempotency key cho action có side effect.
3. Áp đặt state machine cứng và từ chối message sai thứ tự.
4. Thiết kế hàng đợi hoặc serial executor cho thao tác nhạy cảm.

## Lưu ý khi xây lab

1. Bảo đảm khả năng reset trạng thái nhanh sau mỗi lượt chạy.
2. Ghi log chi tiết để so sánh expected vs observed.
3. Tách rõ lỗi race thuần logic với lỗi do hạ tầng timeout.

## Tệp liên quan

- [Phiên và authorization trong kênh stateful](08-session-authorization-and-stateful-risks.md)
- [DoS và cạn kiệt tài nguyên](10-denial-of-service-and-resource-exhaustion.md)
- [Workflow khai thác chuẩn hóa](11-exploitation-workflows.md)
- [Kịch bản lab và huấn luyện agent](14-labs-and-agent-training-scenarios.md)
