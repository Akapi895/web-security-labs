# JWT Signature Verification Flaws

## Bản chất kỹ thuật

Lớp lỗi này xảy ra khi server không verify signature đúng cách trước khi tin payload claims. Hai dạng phổ biến:

1. Không verify signature (decode-only).
2. Chấp nhận token không chữ ký (`alg=none`).

## 1) Unverified signature

### Cơ chế lỗi

Ứng dụng parse token và dùng payload ngay, bỏ qua bước xác minh cryptographic.

### Điều kiện khai thác

- JWT được dùng để authorize session/role.
- Server không ràng buộc bắt buộc verify signature.

### Cách detect

1. Đổi `sub` hoặc `role` trong payload.
2. Giữ nguyên signature cũ.
3. Gửi request và quan sát.

Nếu token vẫn hợp lệ, khả năng cao ứng dụng chỉ decode mà không verify.

## 2) Accepting `alg=none`

### Cơ chế lỗi

JWT header `alg` bị tin mù. Server cho phép token ở chế độ không chữ ký.

### Điều kiện khai thác

- Parser/library hoặc wrapper chấp nhận `none`.
- Filter chặn `none` yếu (đôi khi bypass được bằng obfuscation).

### Cách detect

1. Đổi header sang `{"alg":"none"}`.
2. Xóa phần signature, giữ dấu chấm cuối:

`<header>.<payload>.`

3. Gửi request và kiểm tra response.

## Workflow khai thác chuẩn

1. Baseline: user thường không vào được `/admin`.
2. Tamper payload không ký lại.
3. Nếu thất bại, thử nhánh `alg=none`.
4. Nếu thành công, xác nhận impact bằng thao tác đặc quyền.

## Indicators trong thực tế

| Dấu hiệu                                    | Diễn giải                      |
| ------------------------------------------- | ------------------------------ |
| Token tamper nhưng vẫn được chấp nhận       | Thiếu verify signature         |
| `alg=none` cho phép login hợp lệ            | Flawed signature verification  |
| Không có lỗi verify/không invalidate cookie | Kiểm tra chữ ký không hiệu lực |

## Mapping PortSwigger labs

- Lab 1: JWT authentication bypass via unverified signature
- Lab 2: JWT authentication bypass via flawed signature verification

## Giảm false positive

1. Test lặp lại trên cùng endpoint với token control.
2. So sánh rõ ràng 2 case true/false condition.
3. Xác nhận bằng hành động quyền cao, không chỉ dựa status code.

## Phòng thủ

1. Bắt buộc verify signature trước mọi logic authorize.
2. Cấm tuyệt đối `alg=none` trong production.
3. Ràng buộc cứng thuật toán expected ở server-side, không tin `alg` từ client.
4. Thêm test bảo mật regression cho tamper + none + mixed-case variants.

## Related Files

- [Detection Workflow](01-detection-workflow.md)
- [Claim Validation Logic](09-claim-validation-logic.md)
- [Defense and Mitigation](13-defense-mitigation.md)
