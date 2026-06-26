# Mô hình xử lý DOM phía trình duyệt

## DOM là gì?

Document Object Model (DOM) là biểu diễn phân cấp của trình duyệt cho các phần tử, thuộc tính và đối tượng trên trang.

JavaScript dùng mô hình này để đọc và thay đổi trạng thái trang ở thời gian chạy.

Bản thân thao tác DOM không phải là không an toàn. Rủi ro xuất hiện khi dữ liệu không đáng tin cậy bị đưa vào các thao tác trình duyệt nguy hiểm.

## JavaScript tương tác với DOM như thế nào

Mã phía client thường chạy theo 3 giai đoạn:

1. Đọc input từ dữ liệu do trình duyệt cung cấp.
2. Biến đổi hoặc chuyển tiếp dữ liệu qua biến và hàm.
3. Ghi dữ liệu vào đối tượng DOM hoặc API thực thi/điều hướng.

Khi bước 1 đọc dữ liệu do attacker ảnh hưởng và bước 3 dùng sink rủi ro, trang có thể hình thành lỗ hổng.

## Ranh giới tin cậy phía client

Mọi dữ liệu attacker có thể tác động đều phải coi là không đáng tin cậy ở phía client, gồm:

- Thành phần URL (`search`, `hash`, path trong một số ngữ cảnh)
- Referrer và web message từ cửa sổ khác
- Cookie, dữ liệu storage, dữ liệu reflected/stored được script xử lý

## Các ngữ cảnh thực thi trong trình duyệt

Cùng một payload có thể cho kết quả khác nhau theo ngữ cảnh:

| Ngữ cảnh                     | Sink thường gặp                       | Hệ quả an ninh                                    |
| ---------------------------- | ------------------------------------- | ------------------------------------------------- |
| Ngữ cảnh parse HTML          | `innerHTML`, `document.write()`       | DOM XSS hoặc biến đổi UI                          |
| Ngữ cảnh thực thi JavaScript | `eval()`, `Function()`                | Thực thi mã tùy ý                                 |
| Ngữ cảnh điều hướng          | `location`, `open()`                  | Chuyển hướng/phishing hoặc lạm dụng `javascript:` |
| Ngữ cảnh parser dữ liệu      | `JSON.parse()`, `document.evaluate()` | Phá vỡ logic phía client                          |

## Ví dụ: logic chuyển hướng phía client

```javascript
const next = location.hash.slice(1);
if (next.startsWith("https:")) {
  location = next;
}
```

Mẫu này dễ bị khai thác khi attacker kiểm soát `location.hash` và ép điều hướng sang domain ngoài.

## Vì sao lỗi DOM-based hay bị bỏ sót

1. Lỗ hổng phụ thuộc hành vi thời gian chạy của JavaScript, không chỉ template server.
2. "View source" không thể hiện các thay đổi DOM động.
3. Mã đã rút gọn và thư viện bên thứ ba làm mờ luồng nguồn-điểm nhận.

## Tệp liên quan

- [Taint flow, nguồn và điểm nhận](02-taint-flow-sources-sinks.md)
- [Nguyên nhân gốc rễ và API không an toàn](03-root-causes-and-insecure-apis.md)
- [Phát hiện và phân tích luồng dữ liệu](04-detection-and-dataflow-analysis.md)
