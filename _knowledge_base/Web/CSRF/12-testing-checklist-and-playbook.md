# CSRF Testing Checklist and Playbook

## Playbook tổng quát

## Phase 1: Scope and Asset Prioritization

- Xác định nhóm endpoint state-changing.
- Ưu tiên account, admin, payment, integration endpoints.
- Lập sơ đồ auth/session và cookie attributes.

## Phase 2: Baseline Request Capture

- Thực hiện thao tác hợp lệ để lấy request chuẩn.
- Lưu method, params, headers, cookies, anti-CSRF signals.

## Phase 3: Protection Analysis

- Có token không? token ở đâu?
- Token bind session/action thế nào?
- Có Origin/Referer checks không?
- SameSite của session cookie ra sao?

## Phase 4: Bypass Testing Matrix

## Token checks

- [ ] Remove token parameter.
- [ ] Empty token value.
- [ ] Random token value.
- [ ] Token từ session khác.
- [ ] Method switch hoặc override.

## Header checks

- [ ] Thiếu Origin/Referer.
- [ ] Referer lookalike domain.
- [ ] Trường hợp null header handling.

## Browser behavior and request shape

- [ ] Top-level GET navigation test (Lax scenario).
- [ ] Form POST simple content types.
- [ ] Content-type variation (form/text/plain/json expectations).
- [ ] HEAD handling nếu router có map đặc biệt.

## Phase 5: PoC Validation

- Chạy PoC trong browser có session nạn nhân.
- Ghi nhận bằng chứng state change.
- Đánh giá reliability (nhiều lần chạy).

## Phase 6: Impact and Reporting

Báo cáo tối thiểu cần có:

1. Root cause cụ thể.
2. Preconditions khai thác.
3. PoC tái lập.
4. Business impact.
5. Khuyến nghị fix theo nhiều lớp.

## Decision tree nhanh

```text
Endpoint state-changing?
  No  -> giảm ưu tiên CSRF
  Yes -> cookie/auth tự gửi?
          No  -> đánh giá mô hình auth khác
          Yes -> anti-CSRF hiện diện?
                  No  -> direct CSRF test
                  Yes -> token/header/samesite bypass matrix
```

## Severity guidance (tham khảo)

| Mức độ   | Ví dụ                                                 |
| -------- | ----------------------------------------------------- |
| Critical | Tạo admin, takeover hàng loạt, tác động tài chính lớn |
| High     | Đổi email/mật khẩu hoặc tắt MFA                       |
| Medium   | Đổi profile, thao tác ảnh hưởng hạn chế               |
| Low      | Action ít giá trị hoặc khó khai thác thực tế          |

## Regression checklist sau khi vá

- [ ] Endpoint đã reject request thiếu token.
- [ ] Token sai/rỗng/session khác đều bị chặn.
- [ ] Origin/Referer xử lý fail-closed hợp lý.
- [ ] State-changing GET không còn tồn tại.
- [ ] Method override không phá policy CSRF.
- [ ] Tests tự động có case âm và case dương.

## Burp-centric workflow gợi ý

1. Proxy -> capture request chuẩn.
2. Repeater -> thử từng biến thể bypass.
3. Engagement tools -> Generate CSRF PoC.
4. Browser test -> xác nhận state change.

## Related Files

- [Discovery and Detection](03-discovery-and-detection.md)
- [Exploitation Workflow](04-exploitation-workflow.md)
- [Payloads Cheatsheet](09-payloads-cheatsheet.md)
- [Defense and Mitigation](10-defense-mitigation.md)
