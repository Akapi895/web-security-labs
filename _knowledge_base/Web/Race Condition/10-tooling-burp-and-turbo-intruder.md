# Tooling: Burp Repeater and Turbo Intruder

## Objective

Khai thác race condition phụ thuộc mạnh vào độ chính xác timing. File này tập trung vào cách dùng công cụ để giảm jitter và tăng xác suất va chạm trong race window.

## Burp Repeater Strategy

### 1. Benchmark Sequential First

Luôn gửi group request theo thứ tự trước để lấy baseline:

- Status code kỳ vọng.
- Response body kỳ vọng.
- Phân bố thời gian xử lý.

### 2. Then Run Parallel

Gửi cùng group ở chế độ parallel để tìm deviation.

Điểm cần so sánh:

- Có thêm response thành công ngoài baseline không?
- Có thay đổi trạng thái hệ thống sau khi chạy không?
- Có side effect bậc hai (email, logics sau đó) khác thường không?

### 3. Trigger Race Conditions Action

Với Burp Professional, có thể dùng custom action "Trigger race conditions" để tự động nhân bản và gửi song song nhanh hơn.

## Delivery Techniques

### HTTP/2 Single-packet Attack

- Dùng một kết nối HTTP/2.
- Hàng loạt request được hoàn tất gần như cùng lúc.
- Giảm ảnh hưởng network jitter đáng kể.

### HTTP/1.1 Last-byte Synchronization

- Gửi phần lớn request trước.
- Giữ lại byte/frame cuối và release đồng thời.
- Hữu dụng khi target không hỗ trợ HTTP/2.

## Turbo Intruder Essentials

### Engine Selection

| Target Protocol | Recommended Engine                   |
| --------------- | ------------------------------------ |
| HTTP/2          | `Engine.BURP2`                       |
| HTTP/1.1        | `Engine.THREADED` hoặc `Engine.BURP` |

### Gate-based Parallel Flush

Ý tưởng:

1. `engine.queue(..., gate='race1')` để xếp request vào cùng nhóm.
2. `engine.openGate('race1')` để release đồng loạt.

Pseudo-template:

```python
def queueRequests(target, wordlists):
    engine = RequestEngine(
        endpoint=target.endpoint,
        concurrentConnections=1,
        engine=Engine.BURP2
    )

    for payload in wordlists.clipboard:
        engine.queue(target.req, payload, gate='race1')

    engine.openGate('race1')

def handleResponse(req, interesting):
    table.add(req)
```

### Multi-endpoint Pattern in Turbo Intruder

Mẫu thường dùng:

1. Queue một request "mở sub-state".
2. Queue nhiều request "khai thác sub-state".
3. Open gate theo từng attempt.

Điều này đặc biệt hữu ích cho partial construction hoặc multi-endpoint race.

### Reliability Tuning

1. Connection warming: gửi request vô hại trước khi gửi attack batch.
2. Retry theo vòng: race tinh vi thường cần nhiều attempt.
3. Giảm payload noise: request càng gọn, timing càng ổn định.
4. Theo dõi dấu hiệu overlap trong timeline/response behavior.

### Session Lock Handling

Nếu framework lock theo session, song song trong cùng session có thể bị serialize.

Cách xử lý:

- Dùng nhiều session token cho các request cần chạy đồng thời.
- So sánh performance/hiệu ứng giữa same-session và multi-session.

### Common Pitfalls

- Bỏ qua baseline tuần tự.
- Chỉ nhìn status code mà không kiểm tra state hậu kỳ.
- Không kiểm soát side effect reset giữa các lần thử.
- Kết luận quá sớm khi chưa có độ lặp đủ lớn.

## Related Files

- [03-detection-and-scoping](03-detection-and-scoping.md)
- [09-exploitation-workflows](09-exploitation-workflows.md)
- [13-testing-and-review-checklists](13-testing-and-review-checklists.md)
