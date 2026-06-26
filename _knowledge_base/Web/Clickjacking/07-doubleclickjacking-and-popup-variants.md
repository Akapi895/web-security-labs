# DoubleClickjacking và biến thể Popup

## Tại sao nội dung này quan trọng

Nghiên cứu clickjacking gần đây cho thấy các hướng tấn công dựa trên timing và quản lý cửa sổ có thể vượt qua giả định phòng thủ chỉ tập trung vào iframe trong suốt tĩnh.

## DoubleClickjacking (dựa trên thời điểm)

Về mặt khái niệm, attacker điều khiển nhịp `mousedown` / `click` / nhấp đúp để cú nhấp thứ hai của nạn nhân rơi đúng vào control nhạy cảm ở bối cảnh mục tiêu.

### Hồ sơ rủi ro

1. Có thể vượt qua các lớp bảo vệ chỉ nhắm vào overlay iframe trong suốt tĩnh.
2. Đặc biệt nguy hiểm với hành động nhạy cảm chỉ cần một cú nhấp xác nhận.
3. Phụ thuộc mạnh vào choreography tương tác chính xác.

## Biến thể dựa trên popup (không dùng iframe làm đường chính)

Một số PoC dùng kỹ thuật định vị cửa sổ/popup thay cho bề mặt khung nhúng hiển thị.

Ý tưởng mức cao:

1. Mở và đặt popup theo quỹ đạo con trỏ.
2. Điều phối focus/foreground của cửa sổ.
3. Canh thời điểm nhấp để thao tác rơi vào UI mục tiêu trong popup.

Nhóm kỹ thuật này phụ thuộc nặng vào trình duyệt và chính sách môi trường.

## Điều kiện cần

| Điều kiện | Lý do cần có |
| --- | --- |
| Nạn nhân làm đúng chuỗi tương tác | Tấn công phụ thuộc nhịp nhấp cụ thể |
| Hình học control mục tiêu ổn định | Lệch tọa độ sẽ làm tấn công thất bại |
| Hành vi trình duyệt tương thích | Cơ chế focus/cửa sổ bị giới hạn khác nhau |
| Mục tiêu giá trị cao kiểu một cú nhấp | Tối đa hóa tác động thực tế |

## Hướng dẫn kiểm thử (có ủy quyền)

1. Đánh giá xem mục tiêu có hành động tác động cao kiểu một cú nhấp hay không.
2. Kiểm tra liệu đội sản phẩm có đang coi header cổ điển là đủ hay chưa.
3. Bổ sung biến thể tương tác hiện đại vào threat model và regression test.

## Kết luận phòng thủ

1. Hạn chế framing là cần thiết nhưng chưa chắc đủ cho mọi biến thể UI redress.
2. Cần thêm ma sát ở tầng UX cho thao tác quan trọng.
3. Nên giám sát pattern hoàn tất consent/hành động bất thường.

## Tệp liên quan

- [Frame Buster và bypass phía client](08-frame-buster-and-client-side-bypass.md)
- [Chuỗi tấn công và mô hình hóa tác động](10-attack-chains-and-impact-modeling.md)
- [Phòng thủ và giảm thiểu](13-defense-mitigation.md)
