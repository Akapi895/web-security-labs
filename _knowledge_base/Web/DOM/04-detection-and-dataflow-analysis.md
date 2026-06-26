# Phát hiện và phân tích luồng dữ liệu

## Mục tiêu

Xác định các đường đi từ nguồn đến điểm nhận có thể khai thác trong thời gian chạy phía client.

## Chiến lược kiểm thử thủ công

```text
1. Liệt kê các nguồn dữ liệu khả nghi
2. Theo dõi dữ liệu từ nguồn đi qua JavaScript như thế nào
3. Xác định loại điểm nhận và ngữ cảnh thực thi
4. Xây probe/payload phù hợp ngữ cảnh
5. Xác nhận tác động bằng bằng chứng tái hiện được
```

## Kiểm thử HTML sink

1. Đặt một marker chuỗi duy nhất vào nguồn dữ liệu (ví dụ query/hash trong URL).
2. Mở công cụ nhà phát triển để kiểm tra DOM trong thời gian chạy.
3. Tìm vị trí marker và xác định ngữ cảnh (text node, thuộc tính, fragment HTML).
4. Tinh chỉnh input để thử breakout theo đúng ngữ cảnh.

Lưu ý: "View source" của trình duyệt không đủ cho kiểm thử DOM XSS vì không phản ánh DOM đã bị script thay đổi trong thời gian chạy.

## Kiểm thử sink thực thi JavaScript

1. Tìm chỗ nguồn dữ liệu được tham chiếu trong mã JavaScript.
2. Đặt breakpoint tại nơi dữ liệu được đọc.
3. Step qua các bước gán và biến đổi dữ liệu.
4. Xác nhận dữ liệu nhiễm bẩn có đi tới execution sink hay không.

Với điểm nhận thực thi, payload có thể không bao giờ xuất hiện trong DOM hiển thị, nên dấu vết debugger là bắt buộc.

## Khác biệt hành vi giữa các trình duyệt

Một số trình duyệt URL-encode `location.search` và `location.hash` khác nhau trước khi script xử lý. Điều này ảnh hưởng trực tiếp đến khả năng khai thác và cần kiểm thử theo ma trận trình duyệt mục tiêu.

## Kiểm thử có hỗ trợ công cụ

DOM Invader (trong Burp browser) giúp tăng tốc phát hiện bằng cách chỉ ra các nguồn/điểm nhận DOM khả nghi trong mã JavaScript phức tạp hoặc đã rút gọn.

## Pattern cần rà soát khi audit mã

| Pattern                                          | Vì sao cần kiểm tra         |
| ------------------------------------------------ | --------------------------- |
| `location.*` -> điểm nhận điều hướng hoặc HTML   | Rủi ro chuyển hướng/XSS     |
| URL/referrer/cookie -> `innerHTML`               | Rủi ro DOM XSS              |
| nguồn -> `eval` hoặc timer dạng chuỗi            | Rủi ro chèn JavaScript      |
| nguồn -> `document.cookie`                       | Rủi ro thao túng cookie     |
| nguồn -> `postMessage` hoặc bộ lắng nghe message | Rủi ro lạm dụng web message |

## Checklist bằng chứng

1. Nguồn dữ liệu chính xác và cách attacker kiểm soát nguồn đó.
2. Đường đi dữ liệu chi tiết (biến/hàm liên quan).
3. Phân loại sink và ngữ cảnh.
4. Payload hoặc probe đã dùng.
5. Tác động quan sát được và điều kiện tái hiện.

## Tệp liên quan

- [DOM XSS](05-dom-xss.md)
- [Chuyển hướng mở và thao túng liên kết](07-open-redirection-and-link-manipulation.md)
- [Quy trình khai thác](13-exploitation-workflows.md)
- [Kịch bản lab và huấn luyện agent](15-labs-and-agent-training-scenarios.md)
