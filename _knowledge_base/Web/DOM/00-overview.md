# Tổng quan lỗ hổng dựa trên DOM

## Định nghĩa

Lỗ hổng DOM-based xuất hiện khi JavaScript phía client đọc dữ liệu do attacker kiểm soát (source) rồi đưa dữ liệu đó vào API hoặc đối tượng nguy hiểm (sink) mà không có biện pháp kiểm soát phù hợp.

Điểm dễ tổn thương nằm ở mã chạy trong trình duyệt và luồng thực thi thời gian chạy, không chỉ nằm ở phần render response phía server.

## Vì sao quan trọng

| Thuộc tính an ninh | Tác động điển hình                                                                      |
| ------------------ | --------------------------------------------------------------------------------------- |
| Tính bí mật        | Đánh cắp session hoặc dữ liệu nhạy cảm qua script execution hay logic client bị đầu độc |
| Tính toàn vẹn      | Thực hiện hành động trái phép, sửa link/form, thao túng trạng thái UI                   |
| Xác thực/Phiên     | Session fixation, chuyển hướng lừa đảo, lạm dụng niềm tin trong phiên hợp lệ            |
| Tính sẵn sàng      | Lạm dụng API gây tiêu tốn tài nguyên trình duyệt                                        |

## Mô hình tấn công cốt lõi

```text
Nguồn dữ liệu không đáng tin cậy
  -> biến đổi phía client
  -> sink nguy hiểm
  -> thực thi / điều hướng / thay đổi trạng thái
  -> tác động an ninh
```

## Phân loại cấp cao

| Nhóm                                 | Ví dụ sink thường gặp                                    |
| ------------------------------------ | -------------------------------------------------------- |
| DOM XSS và thực thi script           | `innerHTML`, `document.write()`, `eval()`                |
| Lạm dụng điều hướng và chuyển hướng  | `location`, `open()`, `element.href`                     |
| Đầu độc trạng thái phía client       | `document.cookie`, `localStorage.setItem()`              |
| Thao túng thông điệp và request      | `postMessage()`, `XMLHttpRequest.setRequestHeader()`     |
| Tiêm vào parser/truy vấn phía client | `executeSql()`, `document.evaluate()`, `JSON.parse()`    |
| Lạm dụng đối tượng/thuộc tính DOM    | DOM clobbering, `setAttribute()`, các trường dữ liệu DOM |
| DoS phía client                      | `RegExp()`, các API liên quan hệ thống tệp               |

## Quy trình thực hành

```text
1. Xác định source
2. Theo dõi luồng dữ liệu trong JavaScript
3. Xác nhận hành vi sink và ngữ cảnh thực thi
4. Xây payload phù hợp ngữ cảnh
5. Chứng minh tác động và khả năng chain
```

## Ghi chú phạm vi

Bộ kiến thức này dành cho kiểm thử bảo mật có ủy quyền, kỹ thuật phòng thủ, thiết kế lab và huấn luyện agent.

## Tệp liên quan

- [Mô hình xử lý DOM và trình duyệt](01-dom-js-processing-model.md)
- [Taint flow, nguồn và điểm nhận](02-taint-flow-sources-sinks.md)
- [Nguyên nhân gốc rễ và API không an toàn](03-root-causes-and-insecure-apis.md)
- [Phát hiện và phân tích luồng dữ liệu](04-detection-and-dataflow-analysis.md)
- [Quy trình khai thác](13-exploitation-workflows.md)
- [Phòng thủ và giảm thiểu](14-defense-mitigation.md)
