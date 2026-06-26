# CORS Overview

## Definition

Cross-Origin Resource Sharing (CORS) là cơ chế trên trình duyệt cho phép một origin truy cập có kiểm soát tới tài nguyên thuộc origin khác. CORS không thay thế server-side authorization. CORS chỉ quyết định JavaScript có được đọc response hay không.

## Core Security Model

| Concept        | Meaning                                                          |
| -------------- | ---------------------------------------------------------------- |
| Origin         | Bộ ba `scheme + host + port`                                     |
| SOP            | Same-Origin Policy mặc định chặn đọc dữ liệu cross-origin        |
| CORS           | Cơ chế nới lỏng SOP có điều kiện thông qua HTTP headers          |
| Trust Boundary | Ranh giới tin cậy giữa origin yêu cầu và origin cung cấp dữ liệu |

## Why CORS Exists

SOP rất an toàn nhưng quá hạn chế với hệ thống hiện đại (SPA, API gateway, micro-frontend, third-party integration). CORS được thêm vào để cho phép chia sẻ tài nguyên cross-origin một cách có kiểm soát.

## Security Impact of CORS Misconfiguration

Khi CORS cấu hình sai, trang tấn công có thể dùng trình duyệt của nạn nhân để:

- Gửi request đến API đích trong ngữ cảnh phiên đang đăng nhập (nếu cho phép credentials).
- Đọc response chứa dữ liệu nhạy cảm như API key, profile, token anti-CSRF, dữ liệu nội bộ.
- Pivot vào hệ thống intranet trong các tình huống cho phép wildcard/không cần credentials.

## Typical Attack Preconditions

| Condition                                                                 | Why It Matters                       |
| ------------------------------------------------------------------------- | ------------------------------------ |
| Endpoint trả về dữ liệu nhạy cảm                                          | Có giá trị để exfiltrate             |
| Header `Access-Control-Allow-Origin` tin cậy sai origin                   | Trình duyệt cho phép đọc response    |
| Header `Access-Control-Allow-Credentials: true` (trong case credentialed) | Cookie/session được gửi cùng request |
| Nạn nhân đang có phiên hợp lệ                                             | Response chứa dữ liệu của nạn nhân   |

## CORS Is Not CSRF Protection

CORS không ngăn CSRF. CSRF vẫn khai thác được bằng form, image, script include, hoặc các cơ chế khác không cần đọc response. CORS chỉ ảnh hưởng đến khả năng đọc response của JavaScript.

## Learning Roadmap

```
1) SOP foundation
2) CORS protocol and headers
3) Preflight and browser decisions
4) Detection and policy mapping
5) Root-cause misconfigurations
6) Exploitation workflows and PoC patterns
7) Defense and lab design
```

## Related Files

- [SOP Foundation](01-same-origin-policy.md)
- [CORS Protocol and Headers](02-cors-protocol-and-headers.md)
- [Preflight and Flows](03-preflight-and-request-flows.md)
- [Detection and Mapping](04-detection-and-mapping.md)
- [Misconfiguration Root Causes](05-misconfiguration-root-causes.md)
- [Origin Reflection](06-origin-reflection.md)
- [Whitelist and Parser Bypasses](07-whitelist-and-parser-bypasses.md)
- [Null Origin](08-null-origin-and-sandbox.md)
- [Trust Chains, XSS, TLS](09-trust-chains-xss-and-tls.md)
- [Intranet Pivot](10-intranet-and-credentialless-abuse.md)
- [Exploitation Workflows](11-exploitation-workflows.md)
- [Payloads Cheatsheet](12-payloads-cheatsheet.md)
- [Defense and Mitigation](13-defense-mitigation.md)
- [Labs and Training](14-labs-and-training-scenarios.md)
