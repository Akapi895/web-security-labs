# DOM XSS

## Định nghĩa

DOM XSS xuất hiện khi dữ liệu do attacker kiểm soát đi từ nguồn dữ liệu vào điểm nhận có khả năng thực thi script trong ngữ cảnh trình duyệt.

## Các tổ hợp nguồn-điểm nhận điển hình

| Nguồn                              | Điểm nhận                    | Ghi chú                                                                                                |
| ---------------------------------- | ---------------------------- | ------------------------------------------------------------------------------------------------------ |
| `location.search`, `location.hash` | `document.write()`           | Có thể tiêm được phần tử script tùy ngữ cảnh HTML xung quanh                                           |
| Dữ liệu URL/phản chiếu/lưu trữ     | `innerHTML`                  | Trình duyệt hiện đại chặn một số vector cũ, nhưng payload dựa trên trình xử lý sự kiện vẫn có thể chạy |
| Tham số URL                        | jQuery `attr('href', value)` | Payload `javascript:` có thể thực thi khi người dùng click                                             |
| Cơ chế điều hướng theo hash        | jQuery selector sink         | Các mẫu `hashchange` kiểu cũ có thể khai thác được                                                     |

## Quy trình khai thác

```text
1. Chọn từng nguồn dữ liệu để kiểm thử riêng
2. Theo dõi luồng dữ liệu tới điểm nhận khả nghi
3. Xác định đúng ngữ cảnh parse/thực thi
4. Xây payload theo ngữ cảnh đó
5. Xác minh thực thi script và tác động
```

## Chi tiết hành vi của điểm nhận

### `document.write()`

`document.write()` có thể xử lý payload chứa markup có khả năng thực thi script, nhưng khả năng khai thác phụ thuộc chặt vào ngữ cảnh HTML bao quanh.

### `innerHTML`

Trên trình duyệt hiện đại, script tag trực tiếp thường không hiệu quả với điểm nhận này. Payload thường phải đi theo hướng dựa trên sự kiện qua các phần tử như `img` hoặc `iframe`.

Mẫu ví dụ:

```javascript
element.innerHTML = "<img src=1 onerror=alert(document.domain)>";
```

## Kịch bản với phụ thuộc bên thứ ba

### jQuery attribute sink

```javascript
$("#backLink").attr(
  "href",
  new URLSearchParams(location.search).get("returnUrl"),
);
```

Nếu `returnUrl` bị attacker kiểm soát và cho phép scheme `javascript:`, mã có thể thực thi khi người dùng bấm link.

### jQuery selector sink với hashchange

Các mẫu cũ truyền `location.hash` vào selector API có thể tạo DOM XSS, đặc biệt trên phiên bản thư viện cũ.

## DOM XSS phản chiếu và lưu trữ

DOM XSS có thể bao gồm phần xử lý phía server:

1. Reflected DOM XSS: server phản chiếu dữ liệu request vào trang, sau đó script phía client đưa dữ liệu đó vào điểm nhận.
2. Stored DOM XSS: server lưu dữ liệu attacker, phản hồi ở request sau, rồi script phía client chuyển dữ liệu vào điểm nhận.

## Trọng tâm phòng thủ

1. Không đưa dữ liệu không đáng tin cậy vào điểm nhận HTML hoặc điểm nhận thực thi.
2. Ưu tiên API dạng văn bản an toàn và kiểm tra danh sách cho phép nghiêm ngặt.
3. Khi buộc phải xử lý HTML, áp sanitize/encode theo đúng ngữ cảnh.
4. Rà soát điểm nhận của thư viện bên thứ ba, không chỉ mã nội bộ.

## Tệp liên quan

- [Phát hiện và phân tích luồng dữ liệu](04-detection-and-dataflow-analysis.md)
- [Nguyên nhân gốc rễ và API không an toàn](03-root-causes-and-insecure-apis.md)
- [Quy trình khai thác](13-exploitation-workflows.md)
- [Phòng thủ và giảm thiểu](14-defense-mitigation.md)
