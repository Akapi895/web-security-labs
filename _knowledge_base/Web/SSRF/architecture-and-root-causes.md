# Architecture And Root Causes

## 1. Trust boundary sai là nguyên nhân trung tâm

Root cause lớn nhất của SSRF là thiết kế trust boundary sai:

- Ứng dụng coi URL do user cung cấp là dữ liệu vô hại.
- Trong khi thực tế URL này điều khiển đích mạng mà server sẽ truy cập.

Hậu quả là quyền mạng của server bị "mượn" bởi attacker.

## 2. Các request sink dễ phát sinh SSRF

1. Avatar/image fetch từ URL.
2. Webhook/callback URL.
3. Import dữ liệu từ URL.
4. URL preview, crawler, analytics (đặc biệt qua Referer).
5. PDF/HTML renderer tự động tải ảnh/CSS.
6. API gateway/proxy chuyển tiếp URL đích theo input.

## 3. Lỗi kiểm soát URL đầu vào

1. Chỉ dùng blacklist (`localhost`, `127.0.0.1`) dễ bypass.
2. Không canonicalize trước khi validate.
3. Validate ở parser A, nhưng request thực thi bởi parser B.
4. Cho phép redirect follow không giới hạn.
5. Chấp nhận nhiều scheme ngoài ý định.

## 4. URL parsing discrepancy

Nhiều bypass xảy ra do parser mismatch giữa:

- framework web,
- thư viện validate URL,
- HTTP client runtime,
- reverse proxy/load balancer.

Các thành phần xử lý khác nhau với ký tự như `@`, `#`, `%`, backslash, encoded byte, dẫn đến host thực bị thay đổi sau khi đã qua filter.

## 5. Lỗi kiến trúc mạng

1. App server có egress quá rộng.
2. Internal services tin tưởng request nội mạng, thiếu auth mạnh.
3. Không tách network zone cho service phụ trợ.
4. Metadata endpoint cloud chưa harden (không bắt buộc IMDSv2, không chặn route).

## 6. Lỗi ở hệ thống phụ trợ (auxiliary systems)

Từ tài liệu tham chiếu, SSRF có thể đến từ thành phần không phải business API chính:

1. Analytics xử lý Referer.
2. TLS stack auto-fetch AIA CA Issuers.
3. Nginx stream `proxy_pass $ssl_preread_server_name`.
4. PDF/CSS preprocessors tải URL trong nội dung user-controlled.
5. Reverse proxy chấp nhận absolute-form request line.

## 7. Anti-pattern cần tránh

1. "Chỉ cho phép domain whitelist" nhưng vẫn follow redirect tùy ý.
2. Chỉ kiểm tra string URL, không kiểm tra IP sau DNS resolution.
3. Chấp nhận full URL khi thực tế chỉ cần ID tài nguyên.
4. Cho phép nhiều protocol mà không có lý do nghiệp vụ.
5. Dựa vào client-side validation hoặc regex đơn giản.

## 8. Triệu chứng kiến trúc rủi ro cao

1. Endpoint nhận URL và trả dữ liệu fetch thẳng cho user.
2. Chức năng callback chạy trong worker có quyền mạng rộng.
3. Không có outbound firewall policy theo đích.
4. Ứng dụng vừa có SSRF vừa có open redirect nội bộ.

Khi các dấu hiệu này xuất hiện cùng nhau, SSRF thường mang mức rủi ro cao hoặc critical.
