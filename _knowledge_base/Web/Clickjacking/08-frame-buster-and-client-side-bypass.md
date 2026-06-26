# Frame Buster và bypass phía client

## Bối cảnh

Nhiều ứng dụng vẫn dựa vào JavaScript frame-busting phía client. Cơ chế này hữu ích như tín hiệu bổ sung, nhưng không nên xem là lớp bảo vệ chính.

## Logic frame-busting điển hình

```javascript
if (top !== self) {
  top.location = self.location;
}
```

Mục tiêu của đoạn này là ép nội dung đang bị nhúng thoát ra top-level context.

## Vì sao phòng thủ phía client mong manh

1. JavaScript có thể bị chặn/tắt/hạn chế.
2. Hành vi trình duyệt khác nhau theo phiên bản và nền tảng.
3. Frame-busting có thể bị vượt qua bằng sandbox và các kỹ thuật liên quan.

## Pattern vô hiệu hóa bằng sandbox

Iframe do attacker kiểm soát có thể khai báo `sandbox` theo cách vẫn cho phép hành vi cần thiết, nhưng làm hỏng giả định kiểm tra top-navigation của frame-busting.

Mẫu đại diện trong nghiên cứu công khai:

```html
<iframe src="https://target.example" sandbox="allow-forms allow-scripts">
</iframe>
```

Tùy hành vi ứng dụng, các flag bổ sung như `allow-same-origin` hoặc `allow-modals` có thể làm thay đổi kết quả.

## Nhóm bypass mang tính lịch sử

1. Lạm dụng `onbeforeunload` để can thiệp chuyển hướng phá khung.
2. Tương tác với bộ lọc XSS của trình duyệt làm tắt script inline (hành vi cũ).
3. Ràng buộc thực thi script theo môi trường cụ thể.

Những hướng này quan trọng ở góc nhìn lịch sử để hiểu vì sao phòng thủ phía máy chủ trở thành tiêu chuẩn.

## Định vị phòng thủ

1. Giữ frame-busting như defense-in-depth.
2. Dùng chính sách framing phía máy chủ làm kiểm soát có thẩm quyền.
3. Kiểm thử liên tục trên ma trận trình duyệt được hỗ trợ.

## Checklist kiểm thử

1. Endpoint còn được bảo vệ nếu JavaScript bị tắt không?
2. Cơ chế bảo vệ có sống sót trước thử nghiệm sandbox framing không?
3. Mọi route nhạy cảm đã được bảo vệ phía máy chủ một cách nhất quán chưa?

## Tệp liên quan

- [Điều kiện và nguyên nhân gốc rễ](03-conditions-and-root-causes.md)
- [Phòng thủ và giảm thiểu](13-defense-mitigation.md)
- [Kịch bản lab và huấn luyện agent](14-labs-and-agent-training-scenarios.md)
