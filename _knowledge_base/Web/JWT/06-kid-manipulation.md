# KID Manipulation

## Bản chất kỹ thuật

`kid` (key ID) dùng để chọn khóa verify chữ ký. Lỗ hổng phát sinh khi ứng dụng dùng `kid` trực tiếp trong truy vấn hoặc filesystem path mà không ràng buộc chặt.

Các dạng phổ biến:

1. Path traversal: `kid` bị dùng như đường dẫn file.
2. Injection vào truy vấn DB/cache lookup.
3. Fallback key nguy hiểm khi `kid` không hợp lệ.

## 1) Path traversal qua `kid`

### Cơ chế

Ứng dụng lấy key theo kiểu `read(basePath + kid)`.
Attacker chèn `../../..` để trỏ tới file có nội dung dự đoán được (`/dev/null`, `nul`, file rỗng, ...).

### Điều kiện khai thác

- `kid` đi vào API đọc file mà không canonicalize/allowlist.
- Verifier dùng nội dung file đó làm key HMAC hoặc input verify.

### Workflow

1. Đặt `kid` traversal tới file mục tiêu.
2. Chọn thuật toán phù hợp (thường HS256 trong kịch bản lab).
3. Ký token theo key tương ứng với nội dung file mục tiêu.
4. Gửi token, xác nhận leo thang quyền.

## 2) Lookup/injection qua `kid`

Trong một số triển khai, `kid` có thể đi vào query string concat hoặc cache key resolver. Nếu thiếu validation, attacker có thể:

- Bẻ lái chọn key không mong muốn
- Gây lỗi fallback dẫn đến bypass

## Dấu hiệu nhận biết

| Dấu hiệu                                           | Ý nghĩa                |
| -------------------------------------------------- | ---------------------- |
| `kid` dạng path (`../`) làm thay đổi verify result | Path traversal khả thi |
| `kid` lạ nhưng token vẫn pass bằng key predictable | Key selection flaw     |
| Lỗi theo pattern file-not-found/lookup-fallback    | Resolver không an toàn |

## Mapping PortSwigger lab

- Lab 6: JWT authentication bypass via `kid` header path traversal

## Phòng thủ

1. Không dùng `kid` làm file path/query trực tiếp.
2. Dùng map tĩnh `kid -> key` trong memory hoặc key store chuẩn.
3. Validate `kid` theo định dạng chặt (regex + length + charset).
4. Canonicalize path và chặn traversal tuyệt đối.
5. Không fallback về secret mặc định khi key lookup fail.

## Related Files

- [JKU Header Injection](05-jku-header-injection.md)
- [Algorithm Confusion](07-algorithm-confusion.md)
- [Defense and Mitigation](13-defense-mitigation.md)
