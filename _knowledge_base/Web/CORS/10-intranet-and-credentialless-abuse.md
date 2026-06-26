# Intranet Pivot and Credentialless CORS Abuse

## Why This Case Is Special

Nhiều tấn công CORS cần `ACAC: true`. Tuy nhiên, với intranet, ngay cả khi không credentials attacker vẫn có thể dùng browser nạn nhân làm proxy để đọc tài nguyên nội bộ nếu server cho phép `ACAO: *` hoặc trust quá rộng.

## Common Pattern

```http
HTTP/1.1 200 OK
Access-Control-Allow-Origin: *
```

Nếu endpoint intranet không yêu cầu auth cookie (hoặc auth dựa trên network location), trang bên ngoài có thể đọc dữ liệu qua browser của nhân viên trong mạng nội bộ.

## Network-Location-as-Auth Anti-Pattern

Hệ thống nội bộ thường dựa vào IP/private network thay vì auth đúng nghĩa. Đây là điều kiện để CORS pivot trở nên nguy hiểm.

## Attack Flow (Intranet Pivot)

1. Nhân viên mở trang attacker trên Internet.
2. Script attacker gửi request đến host intranet (`http://intranet.local/...`).
3. Intranet trả `ACAO: *` hoặc policy quá lỏng.
4. Browser cho script attacker đọc response nội bộ.

## Practical Notes

- Một số browser/chương trình đang giới hạn local-network request chặt hơn (Private Network Access), nhưng không thể xem là lớp bảo vệ chính.
- Vẫn cần harden service nội bộ như service Internet-facing.

## Detection Checklist

1. Thử CORS request tới endpoint intranet API/no-auth.
2. Kiểm tra `ACAO: *` và khả năng đọc response từ browser.
3. Kiểm tra reliance vào source network thay vì auth token/session.
4. Đánh giá khả năng leak inventory, config, file, metrics nội bộ.

## Remediation

- Không dùng wildcard CORS trên tài nguyên nội bộ nhạy cảm.
- Bắt buộc authN/authZ ở server, không dựa vào network location.
- Áp dụng segmentation và ACL theo identity, không chỉ theo IP zone.

## Related Files

- [CORS Protocol and Headers](02-cors-protocol-and-headers.md)
- [Defense and Mitigation](13-defense-mitigation.md)
