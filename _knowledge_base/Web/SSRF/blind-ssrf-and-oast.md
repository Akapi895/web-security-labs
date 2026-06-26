# Blind SSRF And OAST

## 1. Blind SSRF là gì

Blind SSRF xảy ra khi attacker khiến server gửi request thành công, nhưng không đọc trực tiếp response trong giao diện ứng dụng.

## 2. Vì sao blind SSRF vẫn nguy hiểm

Dù không có in-band data leak, blind SSRF vẫn cho phép:

1. nội suy mạng nội bộ,
2. dò service,
3. kích hoạt chain known-vulnerabilities,
4. trong một số case đạt RCE gián tiếp.

## 3. OAST là kỹ thuật cốt lõi

Out-of-band Application Security Testing (OAST) dùng endpoint kiểm soát bởi tester để ghi nhận:

1. DNS query,
2. HTTP request,
3. đôi khi các giao thức khác.

Công cụ thường dùng theo tài liệu:

- Burp Collaborator,
- Interactsh,
- webhook/request bin tương đương.

## 4. Cách đọc tín hiệu callback

1. DNS-only callback:
   - có thể do HTTP egress bị chặn sau bước resolve.
   - vẫn là bằng chứng SSRF.
2. DNS + HTTP callback:
   - chứng minh outbound HTTP hoàn chỉnh.
3. Không callback:
   - chưa đủ kết luận, cần thử thêm variant payload.

## 5. Time-based blind SSRF

Khi không có callback rõ ràng, có thể dùng chênh lệch thời gian để suy luận:

1. target tồn tại/không tồn tại,
2. port mở/đóng,
3. endpoint xử lý chậm/nhanh.

Giới hạn:

- dễ nhiễu bởi retry, queue, network jitter.

## 6. Blind-to-informative transitions

Một số tình huống từ tài liệu cho thấy có thể nâng từ blind sang lộ dữ liệu:

1. Lợi dụng handling bất thường của redirect status code.
2. Đẩy ứng dụng vào error mode làm lộ redirect chain/body.
3. Kết hợp chain với service có side effect quan sát được.

## 7. Hidden attack surface cho blind SSRF

1. Referer processing của analytics.
2. Parser dữ liệu có URL embedded (XML/HTML/CSS/PDF).
3. Background workers tự fetch resource.

Đây là các bề mặt khó thấy trong luồng request chính nhưng rất giá trị khi săn blind SSRF.

## 8. Workflow thực chiến cho blind SSRF

1. Xác nhận callback OAST cơ bản.
2. Fingerprint phương thức fetch:
   - user-agent,
   - timeout behavior,
   - redirect behavior.
3. Tạo probe map theo subnet/port có kiểm soát.
4. Ưu tiên chain deterministic có callback để xác minh impact.

## 9. Ghi nhận bằng chứng trong báo cáo

1. Payload gốc gửi vào injection point.
2. Log callback OAST có timestamp.
3. Correlation giữa request ứng dụng và callback.
4. Mức độ reachability và kịch bản leo thang khả thi.
