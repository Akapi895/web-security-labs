# SQL Injection (SQLi) - Báo Cáo Tổng Hợp

## 1. Bản chất SQLi

SQLi là lỗi khi dữ liệu do người dùng kiểm soát được đưa vào câu lệnh SQL như một phần của mã lệnh, thay vì được xử lý như dữ liệu thường.

Bản chất của SQLi:

- Trình ứng dụng xây chuỗi truy vấn bằng nối chuỗi (string concatenation)
- Input không được ràng buộc bởi prepared statement/parameter binding
- DB engine phân tích toàn bộ chuỗi thành câu lệnh hợp lệ và thực thi

Ví dụ bản chất:

- Truy vấn mong muốn: `SELECT * FROM users WHERE username = 'alice'`
- Nếu nối chuỗi trực tiếp với input độc hại, cấu trúc SQL bị thay đổi logic (bypass xác thực, đọc/ghi dữ liệu, ...)

## 2. Nguyên nhân gốc rễ gây SQLi

SQLi không phải do "ký tự nháy đơn"; dấu nháy chỉ là triệu chứng. Nguyên nhân gốc là mất ranh giới giữa code và data.

### 2.1 Nguyên nhân kỹ thuật

- Nối chuỗi SQL trực tiếp từ input (GET/POST/JSON/Cookie/Header)
- Dùng dynamic SQL không tham số hóa
- Tin tưởng dữ liệu đã lưu (second-order SQLi)
- Lộ thông báo lỗi SQL chi tiết ra ngoài
- Quyền DB quá lớn (có thể leo thang tác động)

### 2.2 Điều kiện để khai thác thành công

- Có điểm nhận input đi vào truy vấn SQL
- Có dấu hiệu phản hồi (nội dung, lỗi, hoặc độ trễ)
- Có khả năng điều chỉnh payload phù hợp context (string/numeric/comment)

## 3. Cách detect SQLi

Mục tiêu phát hiện: (1) có SQLi hay không, (2) thuộc loại nào, (3) là DBMS gì.

### 3.1 Xác định điểm tiềm năng

Kiểm tra toàn bộ kênh input:

- URL param, form POST, JSON/XML body
- Cookie, Header (`User-Agent`, `Referer`, custom header)

### 3.2 Kiểm tra hành vi True/False

Dùng cặp payload logic để so sánh phản hồi:

- Điều kiện đúng so với điều kiện sai
- Nếu phản hồi khác nhau có quy luật thì có khả năng là Boolean SQLi

### 3.3 Dấu hiệu theo nhóm kỹ thuật

- Error-based: thấy lỗi DBMS, stack trace, thông điệp parse/cast
- Union-based: kết quả bổ sung xuất hiện trên giao diện
- Boolean blind: khác biệt nội dung/trạng thái/chiều dài response
- Time-based blind: độ trễ có điều kiện
- OOB: hệ thống phát sinh kết nối DNS/HTTP ra ngoài

### 3.4 Nhận diện DBMS (Fingerprint)

Nhận diện DBMS qua:

- Mẫu lỗi đặc trưng
- Hàm delay đặc trưng
- Cú pháp đặc thù (ví dụ Oracle cần `FROM dual`, MSSQL dùng `TOP`)

## 4. Quy trình khai thác SQLi

1. Phát hiện: tìm điểm inject và xác nhận khả năng thao túng truy vấn.
2. Nhận diện: fingerprint DBMS và context payload.
3. Liệt kê: đếm số cột, tìm cột hiển thị, liệt kê schema/table/column.
4. Trích xuất: lấy dữ liệu mục tiêu (tài khoản, token, PII, thông tin hệ thống).
5. Leo thang: mở rộng ảnh hưởng nếu quyền DB cho phép (file/network/OS).
6. Rò rỉ dữ liệu: đưa dữ liệu ra ngoài bằng kênh phù hợp.

## 5. Các kỹ thuật khai thác và khi nào dùng

### 5.1 Error-based SQLi

Dùng khi ứng dụng trả lỗi SQL rõ ràng.

- Ưu điểm: nhanh, trích xuất trực tiếp.
- Nhược điểm: phụ thuộc mức độ lộ lỗi.

### 5.2 Union-based SQLi

Dùng khi kết quả truy vấn được hiển thị trên giao diện.

- Điều kiện: cùng số cột và tương thích kiểu dữ liệu.
- Thường cần: dò số cột, tìm cột có thể hiển thị chuỗi.

### 5.3 Boolean-based Blind

Dùng khi không hiện lỗi/không hiện data trực tiếp.

- Cơ chế: hỏi đáp đúng/sai để suy diễn từng ký tự.
- Tối ưu: binary search trên mã ASCII.

### 5.4 Time-based Blind

Dùng khi chỉ còn tín hiệu thời gian.

- Cơ chế: điều kiện đúng thì gây delay.
- Rủi ro vận hành: dễ bị nhiễu bởi network latency, rate limit.

### 5.5 Out-of-Band (OOB)

Dùng khi kênh in-band kém hiệu quả hoặc bất đồng bộ.

- Cơ chế: đẩy dữ liệu qua DNS/HTTP callback.
- Điều kiện: DB/account cho phép hàm network, hệ thống có egress.

## 6. WAF bypass

Bộ lọc theo từ khóa đơn giản thường thất bại vì SQL parser của DBMS vẫn hiểu được nhiều biểu diễn tương đương:

- Biến thể chữ hoa/chữ thường
- Chèn comment/no-space/newline/tab
- URL encoding, double encoding
- Đổi hàm tương đương (`SUBSTRING` <-> `SUBSTR`, ...)

Bản chất phòng thủ: nếu code vẫn nối chuỗi SQL thì bypass chỉ là vấn đề thời gian.

## 7. Mục tiêu khai thác

Thay vì dump tất cả, ưu tiên dữ liệu giá trị cao:

- Credential, token, API key
- Dữ liệu thanh toán, thông tin cá nhân
- Tài khoản admin và bảng cấu hình

Kỹ thuật tối ưu:

- Tìm theo keyword tên bảng/cột
- Ưu tiên bảng lớn/có tần suất truy cập cao
- Gom nhiều giá trị vào một kết quả để giảm số request

## 8. Second-order SQLi (dễ bị bỏ sót)

Kiểu lỗi này xảy ra khi input được lưu xuống DB trước, sau đó được lấy ra và đưa vào truy vấn khác một cách không an toàn.

Vì sao nguy hiểm:

- Khó tái hiện bằng test đơn lẻ
- Dễ vượt qua nhiều lớp validate ban đầu

Phòng thủ phải nhất quán:

- Dữ liệu "đã lưu" vẫn là untrusted khi đưa lại vào SQL

## 9. Khắc phục đúng bản chất

### 9.1 Nguyên tắc cốt lõi

1. Parameterized queries/prepared statements ở mọi truy vấn có input biến.
2. Không nối chuỗi SQL trực tiếp.
3. Dynamic phần tên bảng/cột phải allow-list (không bind trực tiếp được).
4. Tài khoản DB theo least privilege.
5. Ẩn thông tin lỗi chi tiết, log nội bộ đầy đủ.

### 9.2 Kiểm soát bổ trợ

- Input validation theo schema (kiểu, độ dài, format)
- WAF là lớp giảm thiểu, không thay thế fix code
- Security test định kỳ: SAST + DAST + pentest + review truy vấn raw SQL

### 9.3 Anti-pattern cần tránh

- Tin vào escaping là đủ
- Tin rằng ORM là auto-safe khi vẫn viết raw query sai cách
- Chỉ sửa payload này payload kia mà không sửa thiết kế truy vấn

## 10. Mapping "nguyên nhân - hậu quả - giải pháp"

| Nguyên nhân                   | Hậu quả                      | Giải pháp ưu tiên                            |
| ----------------------------- | ---------------------------- | -------------------------------------------- |
| Nối chuỗi SQL từ input        | Bypass auth, đọc/ghi dữ liệu | Prepared statement cho tất cả input          |
| Lộ thông báo lỗi DB           | Lộ schema, dễ fingerprint    | Generic error cho user + logging nội bộ      |
| Quyền DB quá rộng             | Leo thang tác động           | Tách user DB theo chức năng, least privilege |
| Dynamic table/column từ input | Inject vào cấu trúc query    | Allow-list giá trị hợp lệ                    |
| Tin dữ liệu đã lưu            | Second-order SQLi            | Xem mọi dữ liệu là untrusted khi tái sử dụng |
