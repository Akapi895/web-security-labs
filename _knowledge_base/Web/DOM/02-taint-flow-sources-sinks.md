# Taint flow, nguồn, điểm nhận và luồng dữ liệu

## Taint flow là gì?

Taint flow là quá trình lan truyền dữ liệu không đáng tin cậy từ nguồn dữ liệu đến điểm nhận.

Lỗ hổng DOM-based xuất hiện khi luồng này đi tới điểm nhận nguy hiểm mà không có bước kiểm tra, làm sạch hoặc mã hóa theo đúng ngữ cảnh.

## Định nghĩa nguồn dữ liệu

Nguồn dữ liệu là thuộc tính hoặc kênh dữ liệu có thể nhận giá trị do attacker kiểm soát.

## Các nguồn dữ liệu phổ biến

| Nhóm nguồn dữ liệu        | Ví dụ                                                                                           |
| ------------------------- | ----------------------------------------------------------------------------------------------- |
| URL và metadata tài liệu  | `document.URL`, `document.documentURI`, `document.URLUnencoded`, `document.baseURI`, `location` |
| Dữ liệu phiên/trình duyệt | `document.cookie`, `document.referrer`, `window.name`                                           |
| Lịch sử và trạng thái     | `history.pushState`, `history.replaceState`                                                     |
| Lưu trữ phía client       | `localStorage`, `sessionStorage`, API IndexedDB                                                 |
| Source từ ứng dụng        | Dữ liệu reflected, dữ liệu stored, web message                                                  |

## Định nghĩa điểm nhận

Điểm nhận là hàm hoặc đối tượng có thể tạo tác động an ninh khi nhận dữ liệu do attacker kiểm soát.

## Ánh xạ điểm nhận -> loại lỗ hổng

| Loại lỗ hổng                    | Ví dụ sink                                                |
| ------------------------------- | --------------------------------------------------------- |
| DOM XSS                         | `document.write()`, `innerHTML`, các HTML sink của jQuery |
| Open redirection                | `location`, `location.assign()`, `open()`                 |
| Thao túng cookie                | `document.cookie`                                         |
| JavaScript injection            | `eval()`, `Function()`, thực thi chuỗi trong timer        |
| Thao túng document-domain       | `document.domain`                                         |
| WebSocket URL poisoning         | `WebSocket()`                                             |
| Thao túng link                  | `element.href`, `element.src`, `element.action`           |
| Thao túng web message           | `postMessage()`                                           |
| Thao túng Ajax header           | `XMLHttpRequest.setRequestHeader()`                       |
| Thao túng đường dẫn file cục bộ | `FileReader.readAsText()` và các API file liên quan       |
| Client-side SQL injection       | `executeSql()`                                            |
| Thao túng HTML5 storage         | `sessionStorage.setItem()`, `localStorage.setItem()`      |
| XPath injection                 | `document.evaluate()`                                     |
| JSON injection                  | `JSON.parse()`                                            |
| Thao túng dữ liệu DOM           | `setAttribute()` và các trường DOM có thể ghi             |
| DoS phía client                 | `RegExp()`, các platform API dễ gây quá tải               |

## Mẫu luồng dữ liệu

### Luồng không an toàn điển hình

```text
source -> gán vào biến -> biến đổi dữ liệu -> sink
```

### Ví dụ: DOM-based open redirect

```javascript
const target = location.hash.slice(1);
if (target.startsWith("https:")) {
  location = target;
}
```

Hash do attacker kiểm soát có thể ép điều hướng sang domain bên ngoài.

## Lưu ý về reflected/stored/messaging

Source không chỉ là dữ liệu do browser cung cấp. Nó còn có thể là:

1. Dữ liệu được server phản chiếu vào trang rồi script tiêu thụ tiếp.
2. Dữ liệu attacker lưu từ trước, sau đó được server trả lại và script đưa vào sink.
3. Dữ liệu từ kênh web message giữa các cửa sổ.

## Checklist rà soát

1. Attacker có kiểm soát được giá trị nguồn dữ liệu không?
2. Có bước biến đổi nào vẫn giữ khả năng khai thác không?
3. Điểm nhận cuối cùng nhận dữ liệu là gì?
4. Ngữ cảnh chính xác là thực thi, điều hướng hay parser?
5. Trước khi vào điểm nhận có lớp kiểm soát đủ mạnh không?

## Tệp liên quan

- [Mô hình xử lý DOM phía trình duyệt](01-dom-js-processing-model.md)
- [Nguyên nhân gốc rễ và API không an toàn](03-root-causes-and-insecure-apis.md)
- [Phát hiện và phân tích luồng dữ liệu](04-detection-and-dataflow-analysis.md)
- [DOM XSS](05-dom-xss.md)
