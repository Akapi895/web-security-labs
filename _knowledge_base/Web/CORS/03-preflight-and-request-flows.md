# Preflight and Request Flows

## Why Preflight Exists

Preflight (`OPTIONS`) là bước kiểm tra trước để browser xác minh server cho phép method/header dự kiến của request cross-origin. Cơ chế này giảm rủi ro với các request "không đơn giản".

## Typical Conditions Triggering Preflight

Preflight thường xảy ra khi:

- Method khác `GET/HEAD/POST`.
- Có custom headers (ví dụ `Authorization`, `X-*`).
- Content-Type không thuộc nhóm đơn giản.

## Example Preflight Exchange

```http
OPTIONS /data HTTP/1.1
Host: api.example.com
Origin: https://app.example.net
Access-Control-Request-Method: PUT
Access-Control-Request-Headers: Authorization
```

```http
HTTP/1.1 204 No Content
Access-Control-Allow-Origin: https://app.example.net
Access-Control-Allow-Methods: PUT, POST, OPTIONS
Access-Control-Allow-Headers: Authorization
Access-Control-Allow-Credentials: true
Access-Control-Max-Age: 240
```

Nếu browser thấy method/header hợp lệ theo response, nó mới gửi request thật.

## Browser Decision Logic

```
Cross-origin request
    -> Có cần preflight?
       -> Yes: gửi OPTIONS, validate response headers
             -> Hợp lệ: gửi request thật
             -> Không hợp lệ: chặn ở browser
       -> No: gửi request thật trực tiếp
    -> Kiểm tra ACAO/ACAC trên response request thật
       -> Hợp lệ: JS được đọc response
       -> Không hợp lệ: JS bị chặn đọc response
```

## Performance and Security Notes

- `Access-Control-Max-Age` cao giúp giảm preflight round-trip, nhưng có thể làm chậm cập nhật policy khi cần rollback.
- Không nên tin preflight như cơ chế auth. Auth và authorization vẫn phải xác thực tại server.

## CORS and CSRF Clarification

CORS không ngăn CSRF. Kẻ tấn công vẫn có thể làm nạn nhân gửi request CSRF mà không cần đọc response. Vì vậy CSRF token/SameSite/Origin checks vẫn cần thiết.

## Tester Checklist for Preflight

1. Kiểm tra endpoint nào phát sinh `OPTIONS`.
2. Thử thay đổi `Origin`, `Access-Control-Request-Method`, `Access-Control-Request-Headers`.
3. Đối chiếu response policy của preflight và request thật.
4. Kiểm tra cache behavior (`Access-Control-Max-Age`) trong các lần thử liên tiếp.

## Related Files

- [CORS Protocol and Headers](02-cors-protocol-and-headers.md)
- [Detection and Mapping](04-detection-and-mapping.md)
