# SSRF Overview

## 1. SSRF là gì

Server-Side Request Forgery (SSRF) là lỗ hổng cho phép attacker ép ứng dụng phía server gửi request đến đích ngoài ý muốn của hệ thống.

Điểm cốt lõi không nằm ở việc attacker gửi request trực tiếp đến target, mà nằm ở việc:

- server đóng vai trò proxy ngoài dự kiến,
- và request phát sinh từ trust zone của server.

## 2. Vì sao SSRF quan trọng trong kiến trúc web hiện đại

Trong kiến trúc hiện đại, ứng dụng thường phải fetch dữ liệu từ nhiều nơi:

- microservice nội bộ,
- webhook/callback của bên thứ ba,
- dịch vụ cloud metadata,
- image/PDF renderer,
- analytics và preview crawler.

Điều này tạo nhiều "request sink" nơi input người dùng có thể ảnh hưởng URL đích. Khi kiểm soát đầu vào yếu, SSRF trở thành pivot từ web app sang nội mạng, cloud plane và hệ thống phụ trợ.

## 3. Bản chất kỹ thuật

Mô hình kỹ thuật chung:

1. Attacker kiểm soát một phần hoặc toàn bộ URL/host/path/scheme.
2. Ứng dụng dùng HTTP client/server-side fetch để gọi đích đó.
3. Request đi từ server nội bộ nên có quyền truy cập khác client internet.
4. Kết quả trả về có thể:
   - phản chiếu trực tiếp (in-band SSRF), hoặc
   - không phản chiếu (blind SSRF) nhưng vẫn tạo side-channel.

## 4. Các dạng SSRF thường gặp

1. SSRF against localhost/server:
   - Truy cập `127.0.0.1`, `localhost`, port quản trị nội bộ.
2. SSRF against internal backend:
   - Truy cập dải private IP và dịch vụ nội mạng.
3. Cloud SSRF:
   - Truy cập metadata service (ví dụ `169.254.169.254`).
4. Blind SSRF:
   - Không đọc response trực tiếp, phải xác minh bằng OAST/time/error.
5. Protocol SSRF:
   - Lợi dụng scheme ngoài HTTP như `file://`, `dict://`, `gopher://`.

## 5. Tác động điển hình

1. Đọc dữ liệu nhạy cảm:
   - metadata token, config, file cục bộ.
2. Truy cập admin API nội bộ không expose internet.
3. Quét mạng nội bộ và fingerprint service.
4. Gửi payload cấp giao thức thấp (gopher) tới dịch vụ TCP nội bộ.
5. Chaining sang RCE hoặc data integrity compromise tùy bối cảnh.

## 6. SSRF trong kill-chain pentest

SSRF thường không phải "đích cuối", mà là "điểm xoay":

- Từ web app -> internal control plane.
- Từ blind primitive -> OAST signal -> internal recon.
- Từ internal service access -> protocol abuse -> command/data manipulation.

## 7. Mô hình tư duy tương tự SQLi knowledge base

Có thể mô hình hóa SSRF theo 4 lớp:

1. Input control: attacker kiểm soát được gì trong URL.
2. Parser behavior: ứng dụng parse URL như thế nào.
3. Network reachability: server đi được đến đâu.
4. Post-fetch behavior: response được xử lý/hiển thị ra sao.

Khai thác thành công khi attacker kiểm soát đủ 4 lớp hoặc tìm được điểm yếu ở từng lớp để bù trừ.
