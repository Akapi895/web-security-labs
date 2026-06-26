# CORS Defense and Mitigation

## Security Principles

1. CORS là browser policy, không phải cơ chế auth.
2. Mỗi origin được trust là một dependency bảo mật.
3. Policy CORS phải tối thiểu và explicit.

## Hard Requirements

## 1) Strict Allowlist

- Chỉ cho phép origin cần thiết.
- So sánh exact `scheme + host + port`.
- Không reflect `Origin` một cách động.

## 2) Safe Credential Handling

- Chỉ bật `Access-Control-Allow-Credentials: true` khi thật sự cần.
- Không bao giờ kết hợp credentials với wildcard trust logic.
- Tách API public (không credentials) và API private (strict allowlist).

## 3) No `null` and No Broad Wildcards for Sensitive Data

- Không allow `Access-Control-Allow-Origin: null` cho endpoint nhạy cảm.
- Không dùng `*` cho tài nguyên nội bộ/private.

## 4) Enforce Server-Side AuthN/AuthZ Independently

Dù CORS đúng hay sai, server vẫn phải:

- Xác thực identity.
- Kiểm tra quyền trên từng resource.
- Không dựa vào Origin như yếu tố auth duy nhất.

## 5) Protect Trusted Origins

- Kiểm tra XSS, subdomain takeover, legacy HTTP trên mỗi trusted origin.
- Loại bỏ trusted origin không còn sử dụng.
- Ưu tiên HTTPS-only allowlist.

## Engineering Guidance

| Area              | Recommendation                                             |
| ----------------- | ---------------------------------------------------------- |
| Origin validation | Dùng URI parser chuẩn, reject malformed input              |
| Header generation | Trả về 1 ACAO value hợp lệ duy nhất                        |
| Preflight         | Chỉ allow methods/headers tối thiểu                        |
| Logging           | Log origin bị từ chối, origin bất thường, ratio deny/allow |
| Testing           | Tự động hóa CORS regression trong CI/CD                    |

## Operational Checklist

1. Liệt kê toàn bộ endpoint có CORS.
2. Gán owner cho từng policy CORS.
3. Review policy định kỳ.
4. Alert khi policy mở rộng bất thường.
5. Kiểm thử browser-based PoC cho mỗi thay đổi policy.

## Secure Baseline Example

```text
Allow origins:
- https://app.example.com
- https://admin.example.com

Credentials:
- true chỉ cho /api/private/*

Wildcard:
- chỉ cho /public/* không chứa dữ liệu nhạy cảm

Null origin:
- deny
```

## Related Files

- [Misconfiguration Root Causes](05-misconfiguration-root-causes.md)
- [Trust Chains, XSS, TLS](09-trust-chains-xss-and-tls.md)
