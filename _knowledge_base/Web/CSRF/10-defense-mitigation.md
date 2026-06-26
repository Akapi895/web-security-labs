# CSRF Defense and Mitigation

## Mục tiêu phòng thủ

Không chỉ xác thực "ai gửi request", mà còn xác thực "request có chủ đích người dùng hay không".

## Kiến trúc phòng thủ nhiều lớp

## Layer 1: CSRF token chuẩn

## Synchronizer token pattern (khuyến nghị)

- Token sinh server-side, bí mật, khó đoán.
- Bind với session user (và lý tưởng là action/context).
- Bắt buộc trong mọi request state-changing.
- Thiếu/sai token phải fail-closed.

## Double-submit cookie (chỉ khi triển khai đúng)

Nếu dùng double-submit:

- Không chỉ so sánh chuỗi raw giữa cookie và body.
- Dùng token có chữ ký server-side (HMAC) và bind session context.

## Layer 2: Cookie strategy

| Thiết lập       | Khuyến nghị                                            |
| --------------- | ------------------------------------------------------ |
| `Secure`        | Bắt buộc cho session cookie                            |
| `HttpOnly`      | Bật để giảm rủi ro token/session theft qua JS          |
| `SameSite`      | `Strict` hoặc `Lax` tùy luồng nghiệp vụ                |
| `SameSite=None` | Chỉ dùng khi thực sự cần cross-site, bắt buộc `Secure` |

Lưu ý: SameSite không thay thế token.

## Layer 3: Header-based intent checks

- Ưu tiên validate `Origin` với action nhạy cảm.
- `Referer` dùng làm fallback có kiểm soát.
- Nếu thiếu cả hai: fail-closed với endpoint nhạy cảm.
- So sánh exact scheme + host + port, tránh contains/regex lỏng.

## Layer 4: Method and parser hardening

1. Không cho state-changing action chạy bằng GET.
2. Chuẩn hóa effective method trước khi áp dụng CSRF middleware.
3. Hạn chế/loại bỏ method override cho route nhạy cảm.
4. Chỉ parse content-type mong đợi, reject payload lệch chuẩn.

## Layer 5: User interaction controls cho action high-risk

- Re-auth password trước thao tác nguy hiểm.
- Step-up MFA.
- Transaction confirmation/signing (đặc biệt tác vụ tài chính).
- Delay + out-of-band notification cho action trọng yếu.

## Pseudocode kiểm tra phía server

```text
if request.is_state_changing():
    assert valid_session(request)
    assert valid_origin_or_referer(request)
    assert valid_csrf_token(request, session, action_context)
    assert method_and_content_type_allowed(request)
    if action_is_high_risk:
        assert step_up_auth_completed(request)
else:
    allow()
```

## Những biện pháp không đủ nếu đứng một mình

- Chỉ dùng POST.
- Chỉ rely vào HTTPS.
- Chỉ check Referer không chặt.
- Chỉ dựa vào multi-step workflow.

## Checklist hardening thực tiễn

- [ ] Mọi endpoint state-changing đi qua middleware CSRF thống nhất.
- [ ] Token bắt buộc, secret, unpredictable, bind session/action.
- [ ] Thiếu token hoặc token rỗng đều reject.
- [ ] Kiểm tra Origin/Referer fail-closed cho route nhạy cảm.
- [ ] Không cho state-changing qua GET.
- [ ] Review method override ở framework/router.
- [ ] Session cookie có Secure + HttpOnly + SameSite phù hợp.
- [ ] Login flow cũng có anti-CSRF protection.
- [ ] Có test regression CSRF trong CI/CD.

## Framework notes

Phần lớn framework hiện đại có cơ chế CSRF built-in, nhưng rủi ro thường phát sinh khi:

- Tự viết route đặc biệt bỏ qua middleware.
- Có nhiều framework thành phần không đồng bộ session/CSRF.
- API endpoint mới thêm nhưng quên policy kiểm tra.

## Related Files

- [Root Causes and Conditions](02-root-causes-and-conditions.md)
- [Token Validation Bypasses](05-token-validation-bypasses.md)
- [SameSite and Browser Behavior](06-samesite-and-browser-behavior.md)
- [Origin Referer and Request Shape Bypass](07-origin-referer-and-request-shape-bypass.md)
- [Testing Checklist and Playbook](12-testing-checklist-and-playbook.md)
