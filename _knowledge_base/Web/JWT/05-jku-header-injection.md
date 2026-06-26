# JKU Header Injection (JWKS Spoofing)

## Bản chất kỹ thuật

Header `jku` cho phép token chỉ định URL chứa JWKS (JSON Web Key Set). Lỗ hổng xảy ra khi server fetch key từ URL do client cung cấp mà không có allowlist/pinning nghiêm ngặt.

Khi đó attacker có thể host JWKS của riêng mình, trỏ `jku` tới đó, và khiến server verify token theo key của attacker.

## Điều kiện khai thác

1. Server hỗ trợ lấy key qua `jku`.
2. Không giới hạn domain/protocol/port/path đủ chặt.
3. Authorization phụ thuộc claims trong JWT.

## Workflow detect -> exploit

### Bước 1: Baseline

- User thường không truy cập được endpoint đặc quyền.

### Bước 2: Chuẩn bị JWKS attacker-controlled

1. Tạo RSA keypair.
2. Publish public key theo format JWKS (`{"keys":[...]} `).

### Bước 3: Chỉnh token

1. Header:

- Đặt `jku` tới JWKS attacker-controlled.
- Đồng bộ `kid` với key trong JWKS.

2. Payload:

- Chỉnh claim quyền (`sub`, `role`, ...).

3. Ký token bằng private key tương ứng.

### Bước 4: Xác nhận impact

Gửi token, xác nhận truy cập tài nguyên admin hoặc thao tác đặc quyền.

## Dấu hiệu nhận biết

| Dấu hiệu                                        | Ý nghĩa                                           |
| ----------------------------------------------- | ------------------------------------------------- |
| Token chỉ pass khi `jku` trỏ host attacker      | Server đang fetch key theo client input           |
| Đổi `kid` + JWKS tương ứng làm thay đổi outcome | Key selection phụ thuộc nguồn ngoài không tin cậy |

## Mapping PortSwigger lab

- Lab 5: JWT authentication bypass via `jku` header injection

## Biến thể thường gặp

1. SSRF qua `jku` (truy cập host nội bộ).
2. Bypass allowlist bằng redirect hoặc parser confusion URL.
3. JWKS cache poisoning nếu cache key yếu.

## Phòng thủ

1. Không chấp nhận `jku` tùy ý từ client.
2. Allowlist domain + pin certificate + kiểm soát redirect.
3. Tách rõ `iss` -> trusted JWKS endpoint mapping server-side.
4. Giới hạn timeout, size, và schema khi fetch JWKS.
5. Cảnh báo token chứa `jku` lạ hoặc tần suất fetch key bất thường.

## Related Files

- [JWK Header Injection](04-jwk-header-injection.md)
- [KID Manipulation](06-kid-manipulation.md)
- [Defense and Mitigation](13-defense-mitigation.md)
