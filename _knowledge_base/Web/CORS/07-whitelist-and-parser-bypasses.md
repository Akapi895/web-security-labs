# Whitelist and Origin Parser Bypasses

## Problem Context

Nhiều hệ thống dùng whitelist origin thay vì reflection. Tuy nhiên, whitelist nếu implement sai vẫn bị bypass.

## Typical Bad Matching Patterns

| Anti-pattern                        | Example                                | Bypass Idea                         |
| ----------------------------------- | -------------------------------------- | ----------------------------------- |
| `endsWith("example.com")`           | Cho phép mọi domain kết thúc chuỗi này | `https://hackersnormal-website.com` |
| `startsWith("https://example.com")` | So khớp prefix đơn giản                | `https://example.com.evil-user.net` |
| Regex dấu chấm không escape         | `^api.example.com$`                    | `https://apiiexample.com`           |
| Regex không khóa biên               | Match 1 phần chuỗi                     | Chèn thêm ký tự/phụ tố              |

## Parser and Browser Inconsistency

Một số trường hợp parser server và browser hiểu origin khác nhau, dẫn đến bypass:

- Ký tự đặc biệt trong host.
- Canonicalization không đồng nhất.
- Xử lý malformed header không chặt.

Thực tế testing cần cover edge-cases theo browser engine và parser backend.

## Example Bypass Probes

```http
Origin: https://example.com.attacker.net
Origin: https://evilexample.com
Origin: https://apiiexample.com
Origin: https://target_.attacker.com
Origin: https://target}.attacker.com
```

## Advanced Risk: Header Parsing Bugs

Nếu ứng dụng không sanitize header đúng cách, có thể dẫn tới:

- Header injection logic.
- Cache poisoning side effects.

Nhóm này ít phổ biến hơn reflection, nhưng impact cao trong hệ thống có cache và parser legacy.

## Secure Validation Principles

1. Parse origin bằng URI parser chuẩn, không so khớp chuỗi thủ công.
2. So sánh exact tuple `scheme + host + port`.
3. Tránh wildcard ngắt quãng qua regex mở rộng.
4. Reject request có origin malformed.

## Related Files

- [Misconfiguration Root Causes](05-misconfiguration-root-causes.md)
- [Null Origin](08-null-origin-and-sandbox.md)
- [Defense and Mitigation](13-defense-mitigation.md)
