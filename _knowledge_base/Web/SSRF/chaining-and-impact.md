# Chaining And Impact

## 1. SSRF như một primitive để chain

SSRF thường là điểm khởi đầu cho chuỗi tấn công lớn hơn, đặc biệt trong hệ thống phân tầng và microservice.

## 2. Các hướng chain phổ biến

### 2.1 SSRF -> Internal admin/API abuse

1. Truy cập endpoint nội bộ không public.
2. Bypass auth dựa trên trust source nội mạng.
3. Thực hiện thao tác quản trị trái phép.

### 2.2 SSRF -> Cloud credential exposure

1. Truy cập metadata endpoint.
2. Lấy token/credential tạm thời.
3. Dùng token pivot sang cloud control plane.

### 2.3 SSRF -> Protocol abuse

1. Dùng gopher/dict gửi payload đến TCP service nội bộ.
2. Thay đổi trạng thái service hoặc thực thi command tùy cấu hình.
3. Kết hợp với lỗi khác để đạt RCE.

### 2.4 SSRF -> Open redirect chain

1. Vượt whitelist bằng URL hợp lệ ban đầu.
2. Redirect sang đích nội bộ/nhạy cảm.

### 2.5 SSRF -> Auxiliary system compromise

1. Referer-driven analytics.
2. PDF renderer/CSS preprocessor.
3. TLS AIA fetch hoặc SNI-based routing misconfig.

## 3. Blind SSRF chaining

Ngay cả khi blind, attacker vẫn có thể:

1. nội suy service nội bộ,
2. kích hoạt known exploit chain có OAST signal,
3. mở rộng footprint tấn công trong mạng.

## 4. Tác động theo CIA

### 4.1 Confidentiality

1. Lộ metadata, secret, config, credential.
2. Lộ dữ liệu từ internal API.

### 4.2 Integrity

1. Thay đổi dữ liệu/thiết lập nội bộ thông qua API hoặc protocol abuse.
2. Tiêm payload vào service nội mạng có cấu hình yếu.

### 4.3 Availability

1. SSRF flood vào endpoint nặng gây resource exhaustion.
2. Abuse vòng lặp redirect hoặc fetch file lớn để DoS.

## 5. Yếu tố làm tăng mức độ nghiêm trọng

1. Server có quyền mạng rộng.
2. Có đường tới metadata hoặc control plane.
3. Nội bộ thiếu authentication/authorization.
4. SSRF sink cho phép scheme ngoài HTTP.
5. Ứng dụng follow redirect tự động.

## 6. Cách lượng hóa impact trong báo cáo

1. Xác định rõ asset đã chạm tới.
2. Chứng minh hành động trái phép thực tế.
3. Trình bày chain từ SSRF primitive -> business impact.
4. Phân biệt impact hiện hữu và impact tiềm năng có điều kiện.

## 7. Mẫu kết luận kỹ thuật

1. SSRF không chỉ là "server gọi URL tùy ý".
2. Đây là lỗi phá vỡ trust boundary giữa web layer và internal network.
3. Khi kết hợp với misconfiguration nội bộ, SSRF có thể đạt mức critical.
