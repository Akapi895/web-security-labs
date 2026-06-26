# CORS Detection and Policy Mapping

## Detection Goal

Mục tiêu không chỉ là thấy header CORS, mà là xác định:

- Policy trust origin đang dùng.
- Điều kiện nào cho phép đọc dữ liệu nhạy cảm.
- Khả năng kết hợp với credentials, XSS, intranet.

## Step-by-Step Methodology

1. Xác định endpoint có giá trị (`/accountDetails`, `/api/profile`, `/token`, `/admin/data`).
2. Quan sát request/response gốc để tìm `Origin`, `ACAO`, `ACAC`.
3. Replay request với các origin test để map hành vi server.
4. Xác minh browser có đọc được response trong tình huống tấn công hay không.
5. Đánh giá impact theo loại dữ liệu và mức độ xác thực.

## Origin Test Matrix

| Test Origin                        | Muc dich                         |
| ---------------------------------- | -------------------------------- |
| `https://attacker.com`             | Kiểm tra reflection/mirror       |
| `null`                             | Kiểm tra trusted null            |
| `http://trusted-sub.example.com`   | Kiểm tra trust protocol insecure |
| `https://example.com.attacker.com` | Kiểm tra suffix/prefix bypass    |
| `https://evilexample.com`          | Kiểm tra matching mơ hồ          |
| `https://target_.attacker.com`     | Kiểm tra parser/regex edge-case  |

## What to Capture as Evidence

| Evidence                       | Why Required                      |
| ------------------------------ | --------------------------------- |
| Request có `Origin` tấn công   | Chứng minh input channel          |
| Response `ACAO`/`ACAC`         | Chứng minh policy lỗi             |
| PoC JS đọc được response       | Chứng minh exploitability thực tế |
| Dữ liệu nhạy cảm bị exfiltrate | Chứng minh impact                 |

## Severity Orientation

| Case                                                 | Typical Severity Driver |
| ---------------------------------------------------- | ----------------------- |
| Reflection + credentials + sensitive API             | Cao/rất cao             |
| Trusted null + credentials                           | Cao                     |
| Wildcard không credentials trên public data          | Thấp-trung bình         |
| Wildcard trên intranet/no direct access              | Trung bình-cao          |
| Trusted insecure protocol có khả năng MITM/XSS chain | Cao                     |

## Common False Positives

- Endpoint có CORS nhưng chỉ trả về dữ liệu công khai.
- Browser chặn đọc response do thiếu header cần thiết dù server có reflect một phần.
- Request tool-side (không qua browser) thành công nhưng không chuyển thành browser exploit.

## Quick Workflow for Pentest

```
Find sensitive endpoint
-> Probe Origin handling
-> Probe credentials behavior
-> Build browser PoC
-> Validate real data read
-> Report root cause + exploit chain + fix
```

## Related Files

- [Misconfiguration Root Causes](05-misconfiguration-root-causes.md)
- [Exploitation Workflows](11-exploitation-workflows.md)
- [Payloads Cheatsheet](12-payloads-cheatsheet.md)
