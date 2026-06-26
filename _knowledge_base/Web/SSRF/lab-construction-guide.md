# Lab Construction Guide

## 1. Mục tiêu của bộ lab SSRF

1. Dạy đúng bản chất SSRF: server request thay user.
2. Huấn luyện tư duy từ detection đến chaining.
3. Tách rõ mức độ: cơ bản, trung cấp, nâng cao.

## 2. Blueprint lab theo cấp độ

### 2.1 Level 1 - Basic SSRF

Kịch bản:

1. Endpoint nhận full URL.
2. In-band response phản chiếu nội dung fetch.
3. Mục tiêu:
   - truy cập localhost admin,
   - truy cập backend private IP.

Năng lực đạt được:

- nhận diện SSRF sink,
- xác nhận exploit cơ bản.

### 2.2 Level 2 - Filtered SSRF

Kịch bản:

1. Có blacklist/whitelist đơn giản.
2. Cho phép redirect follow.
3. Mục tiêu:
   - bypass bằng host notation/encoding,
   - bypass qua open redirect.

Năng lực đạt được:

- parser-oriented thinking,
- bypass có hệ thống.

### 2.3 Level 3 - Blind SSRF

Kịch bản:

1. Không trả response nội bộ.
2. Có OAST endpoint để ghi callback.
3. Mục tiêu:
   - chứng minh DNS/HTTP callback,
   - nội suy internal reachability,
   - thực hiện probe có kiểm soát.

Năng lực đạt được:

- xử lý blind conditions,
- correlation bằng chứng.

### 2.4 Level 4 - Protocol Abuse

Kịch bản:

1. Sink chấp nhận nhiều scheme.
2. Nội mạng có service TCP mô phỏng.
3. Mục tiêu:
   - gửi payload cấp giao thức qua gopher,
   - chứng minh thay đổi trạng thái service.

Năng lực đạt được:

- hiểu SSRF như primitive đa giao thức,
- đánh giá nguy cơ chain nâng cao.

### 2.5 Level 5 - Cloud/Architecture SSRF

Kịch bản:

1. Có mock metadata service.
2. Có egress policy một phần để học bypass và hardening.
3. Mục tiêu:
   - lấy metadata/token mô phỏng,
   - đề xuất fix kiến trúc đúng.

Năng lực đạt được:

- tư duy thực chiến cloud-native.

## 3. Thành phần kỹ thuật nên có trong lab

1. Front-end chức năng fetch URL.
2. Internal service mock (admin panel, config API, metadata API).
3. OAST simulator hoặc callback collector.
4. Reverse proxy để mô phỏng parser/redirect edge-case.
5. Logging dashboard cho outbound requests.

## 4. Rubric chấm bài cho learner/agent

1. Có xác định đúng injection point không.
2. Có chứng minh SSRF bằng evidence rõ ràng không.
3. Có mô tả trust boundary bị phá vỡ không.
4. Có thực hiện chain phù hợp và giải thích điều kiện không.
5. Có đề xuất phòng thủ đúng root cause không.

## 5. Thiết kế challenge theo workflow

1. Challenge A: Detect basic SSRF.
2. Challenge B: Bypass filter.
3. Challenge C: Blind SSRF + OAST.
4. Challenge D: Protocol abuse.
5. Challenge E: Defense patch validation.

Thiết kế này giúp người học đi từ "payload-driven" sang "model-driven".

## 6. Nguyên tắc an toàn khi vận hành lab

1. Cách ly hoàn toàn khỏi mạng production.
2. Không dùng credential thật hoặc endpoint cloud thật.
3. Dùng dữ liệu giả lập và reset environment tự động.
4. Gắn cảnh báo đạo đức/pháp lý về phạm vi kiểm thử được phép.
