# Ánh xạ nguồn tham chiếu cho cơ sở tri thức lỗ hổng dựa trên DOM

## Mục tiêu

Ánh xạ từng chương trong bộ kiến thức DOM tới tài liệu nguồn trong `reference/` để bảo đảm truy vết và nhất quán nội dung.

## Các tệp nguồn trong phạm vi

1. `reference/portswigger.txt`
2. `reference/PayloadsAllTheThings.md`

## Bản đồ chương -> nguồn tham chiếu

| Chương                                         | Trọng tâm                                                  | Nguồn tham chiếu chính                       |
| ---------------------------------------------- | ---------------------------------------------------------- | -------------------------------------------- |
| 00-overview                                    | Định nghĩa, phân loại, khung rủi ro                        | `portswigger.txt`                            |
| 01-dom-js-processing-model                     | Mô hình DOM, bản chất thực thi phía client                 | `portswigger.txt`                            |
| 02-taint-flow-sources-sinks                    | Mô hình source/sink/data-flow và danh mục                  | `portswigger.txt`                            |
| 03-root-causes-and-insecure-apis               | API không an toàn, lỗi logic, xử lý taint sai              | `portswigger.txt`                            |
| 04-detection-and-dataflow-analysis             | Kiểm thử thủ công, dấu vết debugger, DOM Invader           | `portswigger.txt`                            |
| 05-dom-xss                                     | Cơ chế DOM XSS, hành vi điểm nhận, trường hợp thư viện     | `portswigger.txt`                            |
| 06-dom-clobbering                              | Kỹ thuật clobbering và mẫu payload                         | `portswigger.txt`, `PayloadsAllTheThings.md` |
| 07-open-redirection-and-link-manipulation      | Lạm dụng sink điều hướng và link                           | `portswigger.txt`                            |
| 08-cookie-manipulation-and-html5-storage       | Đầu độc cookie/storage và chuỗi khai thác                  | `portswigger.txt`                            |
| 09-javascript-injection-and-document-domain    | Điểm nhận thực thi script và lạm dụng nới lỏng origin      | `portswigger.txt`                            |
| 10-websocket-web-message-and-ajax-manipulation | Thao túng kênh giao tiếp                                   | `portswigger.txt`                            |
| 11-local-file-path-and-client-query-injection  | Lạm dụng file API, bộ phân tích SQL/XPath/JSON phía client | `portswigger.txt`                            |
| 12-dom-data-manipulation-and-dos               | Thao túng UI/state và DoS phía client                      | `portswigger.txt`                            |
| 13-exploitation-workflows                      | Quy trình khai thác chuẩn hóa                              | `portswigger.txt`, `PayloadsAllTheThings.md` |
| 14-defense-mitigation                          | Nguyên tắc phòng ngừa và kiểm soát theo điểm nhận          | `portswigger.txt`                            |
| 15-labs-and-agent-training-scenarios           | Kịch bản huấn luyện trích từ mẫu tấn công đã ánh xạ        | `portswigger.txt`, `PayloadsAllTheThings.md` |

## Hướng dẫn bảo trì

1. Cập nhật file mapping này mỗi khi phạm vi chương thay đổi.
2. Giữ các luận điểm trong chương bám sát hai tài liệu nguồn.
3. Khi mở rộng chương, bổ sung artifact tham chiếu mới vào `reference/` trước.

## Tệp liên quan

- [Tổng quan](00-overview.md)
- [Quy trình khai thác](13-exploitation-workflows.md)
- [Phòng thủ và giảm thiểu](14-defense-mitigation.md)
