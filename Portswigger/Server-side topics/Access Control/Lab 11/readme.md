# Lab: URL-based access control can be circumvented

Khi vừa mở web, thấy `Admin panel`, tuy nhiên truy cập vào thì lỗi:
```
"Access denied"
```

Không có tài khoản nào được cấp sẵn, vì vậy dùng param miner với `GET /admin` để tìm xem có header nào có thể giúp truy cập vào `/admin` không. 