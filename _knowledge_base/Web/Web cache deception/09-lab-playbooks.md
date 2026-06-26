# Kịch bản lab thực hành

## Mục tiêu module

Chuyển hóa kiến thức WCD thành các kịch bản thao tác được ngay trong lab/pentest có ủy quyền.

## Nguyên tắc chung trước khi bắt đầu

1. Đăng nhập tài khoản test để có response dynamic chứa dữ liệu nhạy cảm.
2. Kiểm tra oracle cache (`X-Cache`, `CF-Cache-Status`, `Age`, timing).
3. Luôn sử dụng cache buster khi lặp payload.
4. Tách rõ hai vai trò: attacker và victim.

## Kịch bản 1 - Path mapping discrepancy

## Mục tiêu

Khai thác endpoint dynamic bằng cách thêm path segment + static extension để cache lưu response nhạy cảm.

## Trình tự

1. Xác định endpoint dynamic (ví dụ `/my-account`).
2. Thử `/my-account/abc` và `/my-accountabc` để hiểu route behavior.
3. Fuzz delimiter nếu cần (tìm ký tự origin cắt path).
4. Tạo payload dạng `/my-account;wcd.js` hoặc `/my-account/abc.js`.
5. Xác nhận `miss -> hit` trên cùng payload.
6. Gửi exploit URL cho victim với cache buster mới.
7. Attacker truy cập lại URL và thu hồi dữ liệu victim.

## Dấu hiệu thành công

- Body chứa dữ liệu victim.
- Cache hit tại payload URL.

## Kịch bản 2 - Origin normalization discrepancy

## Mục tiêu

Dùng static directory rule để cache response, trong khi origin resolve traversal về endpoint dynamic.

## Trình tự

1. Xác nhận origin normalize: thử `/aaa/..%2fmy-account`.
2. Tìm static directory được cache (ví dụ `/resources`).
3. Xác nhận `/resources/aaa` có thể bị cache theo prefix rule.
4. Tạo payload `/resources/..%2fmy-account?cb=<new>`.
5. Kiểm tra `miss -> hit`.
6. Victim priming và harvest dữ liệu.

## Dấu hiệu thành công

- Payload trả về dynamic content của endpoint đích.
- Response payload được cache theo static prefix rule.

## Kịch bản 3 - Cache normalization discrepancy + delimiter

## Mục tiêu

Khai thác trường hợp cache resolve traversal nhưng origin không; cần delimiter để origin truncate path về dynamic endpoint.

## Trình tự

1. Xác nhận origin không normalize traversal (`/aaa/..%2fmy-account` trả 404 hoặc body khác).
2. Xác nhận cache normalize trên static prefix (`/aaa/..%2fresources/...` có cache signal).
3. Tìm delimiter hiệu lực với origin (`?`, `%23`, `%3f`, ...).
4. Thử payload dạng `/my-account%23%2f%2e%2e%2fresources?cb=<new>`.
5. Chọn payload vừa trả body dynamic vừa có cache signal.
6. Victim priming và harvest.

## Dấu hiệu thành công

- Encoded delimiter hiệu quả hơn plain delimiter.
- Cache hit sau lần gửi lại payload.

## Kịch bản 4 - Delimiter decoding discrepancy

## Mục tiêu

Khai thác khác biệt decode delimiter giữa cache và origin.

## Trình tự

1. Fuzz cặp delimiter plain/encoded: `#` vs `%23`, `?` vs `%3f`.
2. So sánh response body và cache signal.
3. Nếu encoded variant mới kích hoạt cache, ưu tiên payload encoded.
4. Build exploit URL có extension static.
5. Victim priming + harvest.

## Dấu hiệu thành công

- Plain variant thất bại, encoded variant thành công.

## Kịch bản 5 - Exact file-name cache rule

## Mục tiêu

Khai thác cache rule khớp chính xác tên file (`index.html`, `robots.txt`, `favicon.ico`) khi có normalization discrepancy.

## Trình tự

1. Xác nhận file-name rule tồn tại bằng GET đến file mục tiêu.
2. Test traversal payload để cache normalize về exact filename.
3. Kết hợp delimiter nếu cần để origin trả dynamic endpoint.
4. Xác nhận `miss -> hit` và leak data victim.

## Dấu hiệu thành công

- Payload bắt đầu từ dynamic route nhưng object cache được map về exact file-name rule.

## Checklist bằng chứng sau mỗi lab

1. Baseline request/response.
2. Bảng fuzz delimiter/normalization (payload -> status/body/cache signal).
3. Payload exploit cuối cùng.
4. Bằng chứng victim priming.
5. Bằng chứng harvest.
6. Root cause + đề xuất fix.

## Liên kết đọc tiếp

- [08-exploitation-workflows.md](08-exploitation-workflows.md)
- [10-defense-mitigation.md](10-defense-mitigation.md)
- [12-agent-training-blueprint.md](12-agent-training-blueprint.md)
