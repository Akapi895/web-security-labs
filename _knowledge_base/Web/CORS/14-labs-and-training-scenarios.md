# CORS Labs and Training Scenarios

## Purpose

Bộ scenario này giúp học viên và agent luyện theo đúng chuỗi: nhận diện policy -> khai thác -> đánh giá impact -> đề xuất fix.

## Scenario 1: Basic Origin Reflection

| Item             | Content                                                    |
| ---------------- | ---------------------------------------------------------- |
| Objective        | Khai thác reflection + credentials để lấy dữ liệu account  |
| Vulnerable setup | `ACAO` reflect theo `Origin`, `ACAC: true`                 |
| Core steps       | Probe origin, xác nhận reflection, tạo XHR PoC, exfiltrate |
| Success criteria | Lấy được API key/dữ liệu nhạy cảm của victim               |
| Blue-team fix    | Explicit allowlist, bỏ reflection                          |

## Scenario 2: Trusted Null Origin

| Item             | Content                                          |
| ---------------- | ------------------------------------------------ |
| Objective        | Vượt whitelist bằng `Origin: null`               |
| Vulnerable setup | `ACAO: null` + credentials                       |
| Core steps       | Probe null, dùng sandbox iframe, đọc response    |
| Success criteria | Exfiltrate dữ liệu account qua null origin chain |
| Blue-team fix    | Bỏ null origin khỏi policy production            |

## Scenario 3: Trusted Insecure Protocol

| Item             | Content                                                                       |
| ---------------- | ----------------------------------------------------------------------------- |
| Objective        | Chứng minh rủi ro trust HTTP subdomain                                        |
| Vulnerable setup | Allow `http://trusted-subdomain...` + credentials                             |
| Core steps       | Tìm điểm chèn script trên trusted HTTP origin (XSS/MITM model), gọi API HTTPS |
| Success criteria | Đọc được dữ liệu private từ origin chính                                      |
| Blue-team fix    | HTTPS-only allowlist, bỏ HTTP origin                                          |

## Scenario 4: Intranet Pivot Without Credentials

| Item             | Content                                                           |
| ---------------- | ----------------------------------------------------------------- |
| Objective        | Dùng browser victim truy cập tài nguyên intranet                  |
| Vulnerable setup | Intranet endpoint trả `ACAO: *`, auth yếu                         |
| Core steps       | Host attacker page, gửi request đến intranet, đọc response        |
| Success criteria | Thu được dữ liệu nội bộ mà attacker không truy cập trực tiếp được |
| Blue-team fix    | Bỏ wildcard, bật authN/authZ server-side                          |

## Suggested Agent Training Tasks

1. Từ request/response logs, phân loại misconfiguration type.
2. Đề xuất exploit workflow phù hợp và lý giải preconditions.
3. Sinh PoC browser-level tối thiểu.
4. Sinh fix recommendation theo risk-based priority.
5. Viết regression test matrix cho CORS policy.

## Evaluation Rubric

| Criterion                | Good Output                                  |
| ------------------------ | -------------------------------------------- |
| Technical accuracy       | Phân biệt đúng SOP, CORS, CSRF               |
| Exploitability reasoning | Nêu rõ điều kiện cần và đủ                   |
| Reproducibility          | Có request/response + PoC rõ ràng            |
| Defense quality          | Fix giải quyết root cause, không chỉ symptom |
| Communication            | Trình bày có cấu trúc, dễ mở rộng            |

## Mapping to This Knowledge Base

1. Nền tảng: [00-overview.md](00-overview.md), [01-same-origin-policy.md](01-same-origin-policy.md)
2. Protocol: [02-cors-protocol-and-headers.md](02-cors-protocol-and-headers.md), [03-preflight-and-request-flows.md](03-preflight-and-request-flows.md)
3. Detection: [04-detection-and-mapping.md](04-detection-and-mapping.md)
4. Misconfiguration: [05-misconfiguration-root-causes.md](05-misconfiguration-root-causes.md) đến [10-intranet-and-credentialless-abuse.md](10-intranet-and-credentialless-abuse.md)
5. Execution and defense: [11-exploitation-workflows.md](11-exploitation-workflows.md), [12-payloads-cheatsheet.md](12-payloads-cheatsheet.md), [13-defense-mitigation.md](13-defense-mitigation.md)
