# CORS Misconfiguration Root Causes

## Root Cause Categories

## 1) Unsafe ACAO Policy

`Access-Control-Allow-Origin` được đặt quá rộng hoặc sai logic trust.

| Pattern           | Description                        | Exploit Condition                               |
| ----------------- | ---------------------------------- | ----------------------------------------------- |
| Reflection origin | Server copy `Origin` vào `ACAO`    | Có endpoint nhạy cảm, browser đọc được response |
| Wildcard `*`      | Cho phép mọi origin đọc response   | Data không cần auth hoặc intranet pivot         |
| Weak whitelist    | Match theo prefix/suffix/regex lỗi | Attacker tạo domain qua mặt validator           |
| Trusted `null`    | Chấp nhận `Origin: null`           | Có thể tạo request null từ sandbox iframe       |

## 2) Wrong Credential Combination

`Access-Control-Allow-Credentials: true` được bật khi policy origin không đủ chặt.

| Pattern                                 | Risk                                                        |
| --------------------------------------- | ----------------------------------------------------------- |
| Credentials + reflected origin          | Attacker đọc dữ liệu trong session nạn nhân                 |
| Credentials + trusted insecure protocol | Có thể chain với MITM/XSS trên HTTP subdomain               |
| Credentials + broad subdomain trust     | Một subdomain bị compromise là đủ để mở toàn bộ trust chain |

## 3) Origin Validation Implementation Flaws

Lỗi xử lý chuỗi/parsing:

- Dùng `endsWith("example.com")` thay vì parse host chuẩn.
- Dùng `startsWith("https://example.com")` dễ nhầm domain mở rộng.
- Regex escape sai dấu chấm (`.`) hoặc không khóa điểm đầu/cuối.
- Không canonicalize origin trước khi so sánh.
- Không tách riêng scheme-host-port khi whitelist.

## 4) Trust Model Mistakes

- Tin rằng CORS thay được authorization.
- Tin rằng chỉ cần whitelist "hệ sinh thái nội bộ" là an toàn.
- Không xem mỗi trusted origin là một trust dependency với rủi ro riêng (XSS, takeover, HTTP-only).

## Misconfiguration vs Exploitability

| Misconfiguration        | Có thể khai thác ngay?  | Điều kiện bổ sung                             |
| ----------------------- | ----------------------- | --------------------------------------------- |
| Reflection + ACAC true  | Thường có               | Nạn nhân đang login, endpoint nhạy cảm        |
| `ACAO: *`               | Có/không tùy trường hợp | Data public hay private, có auth hay không    |
| Trusted null            | Có                      | Có context tạo null origin request            |
| Broad whitelist         | Có                      | Domain bypass/takeover/XSS tại trusted origin |
| Insecure protocol trust | Có                      | MITM hoặc điểm chèn script trên HTTP origin   |

## Security Takeaway

Lỗi CORS hiếm khi là lỗi "protocol". Đa phần là lỗi thiết kế trust boundary và validate origin. Vì vậy fix đúng bản chất là:

- Thiết kế lại policy trust.
- Validate origin đúng parser URI.
- Tách CORS khỏi auth logic.

## Related Files

- [Origin Reflection](06-origin-reflection.md)
- [Whitelist and Parser Bypasses](07-whitelist-and-parser-bypasses.md)
- [Defense and Mitigation](13-defense-mitigation.md)
