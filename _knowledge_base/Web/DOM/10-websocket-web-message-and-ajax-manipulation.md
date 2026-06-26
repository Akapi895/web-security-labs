# Đầu độc URL WebSocket, thao túng web message và header Ajax

## Đầu độc URL WebSocket dựa trên DOM

### Định nghĩa

Script dùng dữ liệu do attacker kiểm soát làm URL đích cho kết nối WebSocket.

### Điểm nhận

- `WebSocket()`

### Tác động

1. Trình duyệt có thể kết nối tới endpoint do attacker kiểm soát.
2. Dữ liệu nhạy cảm gửi qua socket có thể bị chặn bắt.
3. Logic phía client tin dữ liệu phản hồi từ socket có thể bị thao túng.

## Thao túng web message dựa trên DOM

### Định nghĩa

Dữ liệu do attacker kiểm soát được gửi qua `postMessage()`, hoặc logic xử lý message không an toàn tin tưởng dữ liệu đến từ origin chưa được xác minh.

### Điểm nhận và ranh giới tin cậy

- `postMessage()` cho thông điệp gửi ra
- Message event handlers ở phía nhận

### Tác động

1. Nhầm lẫn ranh giới tin cậy giữa các tài liệu/cửa sổ.
2. Tiêm dữ liệu/chỉ thị độc hại vào quy trình phía nhận.
3. Có thể chain sang DOM XSS hoặc lạm dụng logic trong message consumer.

### Kiểm soát quan trọng

Luôn xác minh origin và schema kỳ vọng của message trước khi xử lý.

## Thao túng header request Ajax dựa trên DOM

### Định nghĩa

Script phía client ghi giá trị do attacker kiểm soát vào header hoặc metadata của request bất đồng bộ.

### Các điểm nhận chính

- `XMLHttpRequest.setRequestHeader()`
- `XMLHttpRequest.open()`
- `XMLHttpRequest.send()`
- `jQuery.globalEval()` / `$.globalEval()` (trong các luồng không an toàn liên quan)

### Tác động

1. Hành vi xử lý phía server có thể bị thay đổi bởi header giả mạo.
2. Lỗ hổng có thể trở thành điểm neo cho các chuỗi khai thác mức cao hơn.

## Quy trình khai thác dùng chung

```text
1. Kiểm soát giá trị nguồn dữ liệu
2. Xác nhận luồng đi tới điểm nhận giao tiếp
3. Kích hoạt hành vi phía mạng
4. Quan sát điểm vỡ ranh giới tin cậy và tác động thứ cấp
```

## Trọng tâm giảm thiểu

1. Không để dữ liệu không đáng tin cậy quyết định URL socket hoặc request header.
2. Áp danh sách cho phép và lược đồ chặt cho tham số giao tiếp.
3. Kiểm tra origin và cấu trúc message đến trước khi sử dụng.
4. Tránh target origin quá rộng trong cơ chế cross-window messaging.

## Tệp liên quan

- [Phát hiện và phân tích luồng dữ liệu](04-detection-and-dataflow-analysis.md)
- [Quy trình khai thác](13-exploitation-workflows.md)
- [Phòng thủ và giảm thiểu](14-defense-mitigation.md)
