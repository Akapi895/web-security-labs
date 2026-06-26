# Command Injection (CMDi) - Báo Cáo Tổng Hợp

## 1. Bản chất CMDi

Command Injection là lỗi cho phép dữ liệu do người dùng kiểm soát được chèn vào câu lệnh hệ điều hành và được thực thi bởi shell (`/bin/sh`, `bash`, `cmd.exe`, `powershell`).

Bản chất của CMDi:

- Ứng dụng dùng API gọi lệnh hệ điều hành (`system`, `exec`, `popen`, `os.system`, `child_process.exec`...)
- Input được nối trực tiếp vào command string
- Shell parser diễn giải metacharacter (`|`, `&&`, `;`, `&`, newline, command substitution...)
- Người tấn công biến dữ liệu thành lệnh

Ví dụ bản chất:

- Truy vấn mong muốn: `ping <host_hop_le>`
- Nếu nối chuỗi trực tiếp với input độc hại, shell có thể thực thi thêm lệnh ngoài ý muốn của lập trình viên.

## 2. Nguyên nhân gốc rễ gây CMDi

CMDi không chỉ do "ký tự đặc biệt". Nguyên nhân gốc là thiết kế sai khi truyền input vào shell.

### 2.1 Nguyên nhân kỹ thuật

- Gọi shell không cần thiết trong logic xử lý nghiệp vụ
- Nối chuỗi command trực tiếp từ input (URL, form, JSON, header, cookie, filename)
- Dùng API nguy hiểm (ví dụ `exec` với shell mode)
- Validation yếu hoặc dựa vào blocklist dễ bị bypass
- Chạy ứng dụng với quyền hệ thống quá rộng

### 2.2 Điều kiện để khai thác thành công

- Có điểm nhận input đi vào command execution
- Có dấu hiệu phản hồi (output, error, delay, callback)
- Có khả năng điều chỉnh payload theo context (quoted/unquoted, Linux/Windows)

## 3. Cách phát hiện CMDi theo tư duy hệ thống

Mục tiêu phát hiện: (1) có CMDi hay không, (2) thuộc kiểu nào, (3) là OS/shell gì.

### 3.1 Xác định điểm tiềm năng

Kiểm tra toàn bộ kênh input:

- URL params, form fields, JSON/XML body
- Cookie, HTTP headers (`User-Agent`, `X-Forwarded-For`...)
- Filename/file metadata, tham số chức năng hệ thống (ping, traceroute, convert, backup...)

### 3.2 Kiểm tra hành vi in-band

Nếu output được hiển thị trên response:

- Thử các separator cơ bản để quan sát sự thay đổi kết quả
- Kiểm tra các command vô hại để xác nhận khả năng thực thi

### 3.3 Kiểm tra hành vi blind

Nếu không thấy output trực tiếp:

- Time-based: dựa vào độ trễ có điều kiện
- OOB: quan sát DNS/HTTP callback ra ngoài
- File redirection: ghi output ra vị trí có thể đọc lại

### 3.4 Fingerprint môi trường

Cần xác định:

- Linux hay Windows
- Shell context (input nằm trong quote đơn, quote kép, hay unquoted)
- Khả năng outbound (DNS/HTTP), khả năng ghi file

## 4. Quy trình khai thác CMDi (mang tính phương pháp)

1. Phát hiện: tìm injection point và xác nhận có command execution.
2. Nhận diện: xác định OS, shell, context, và mức độ hiện output.
3. Vượt lọc: nếu có filter/WAF thì áp dụng kỹ thuật bypass phù hợp.
4. Khai thác: thực hiện recon hệ thống, user, process, network, file.
5. Trích xuất: lấy dữ liệu giá trị qua in-band, file-based, DNS/HTTP OOB.
6. Leo thang: mở rộng tác động nếu quyền cho phép (privilege escalation, persistence, pivot).

Ý nghĩa bản chất: quy trình này chuyển một "điểm lỗi" thành "rủi ro hệ thống".

## 5. Các kỹ thuật khai thác và khi nào dùng

### 5.1 In-band Command Injection

Dùng khi kết quả lệnh xuất hiện trực tiếp trên giao diện/response.

- Ưu điểm: nhanh, dễ xác minh.
- Nhược điểm: dễ bị phát hiện qua log, phụ thuộc giao diện trả output.

### 5.2 Blind Command Injection

Dùng khi lệnh vẫn chạy nhưng output không trả về response.

- Time-based: xác nhận bằng độ trễ.
- File-based: ghi output ra file có thể truy cập.

### 5.3 Out-of-Band (OOB) Command Injection

Dùng khi in-band và blind khó khai thác.

- Sử dụng kênh DNS/HTTP để gửi tín hiệu/dữ liệu ra ngoài.
- Hữu dụng trong hệ thống xử lý bất đồng bộ hoặc output bị ẩn.

### 5.4 Argument Injection

Không cần inject separator; chỉ cần chèn đối số nguy hiểm vào utility.

- Bản chất: thay đổi hành vi command hợp lệ bằng các option độc hại.
- Thường gặp với utility như `curl`, `wget`, `tar`, `ssh`...

## 6. Vì sao filter/WAF thường thất bại

Blocklist đơn giản thường không đủ vì shell parser và utility parser rất linh hoạt:

- Nhiều biểu diễn tương đương của separator/space/newline/tab
- Encoding/double encoding
- Obfuscation (quote insertion, variable expansion, wildcard...)
- Khác biệt giữa Linux shell và Windows CMD/PowerShell

Bản chất phòng thủ: nếu vẫn nối command string từ input thì bypass chỉ là vấn đề thời gian.

## 7. Nhắm mục tiêu dữ liệu và tác động

Sau khi xác nhận CMDi, ưu tiên mục tiêu giá trị cao:

- Thông tin tài khoản chạy service, biến môi trường, secret/config
- File cấu hình, source code, credentials
- Thông tin mạng nội bộ để đánh giá lateral movement

Tác động thường gặp:

- Confidentiality: lộ dữ liệu hệ thống và dữ liệu nghiệp vụ
- Integrity: sửa/xóa file, cài trojan, thay đổi cấu hình
- Availability: DoS, exhaust tài nguyên, làm sập dịch vụ

## 8. Khắc phục đúng bản chất

### 8.1 Nguyên tắc cốt lõi

1. Tránh gọi OS command nếu có API thư viện thay thế.
2. Nếu bắt buộc phải gọi command: dùng argument array, không dùng command string.
3. Tuyệt đối không nối trực tiếp input vào shell.
4. Validation theo allow-list, theo kiểu dữ liệu và domain nghiệp vụ.
5. Giảm quyền runtime theo least privilege.

### 8.2 Kiểm soát bổ trợ

- Tắt/hạn chế API nguy hiểm trong runtime production
- Chốt outbound network theo nhu cầu tối thiểu
- Isolate bằng container/chroot/sandbox
- Logging + monitoring hành vi command bất thường
- SAST/DAST và code review tập trung vào call-site thực thi command

### 8.3 Anti-pattern cần tránh

- Chỉ dựa vào escaping hoặc blocklist
- Dùng `shell=True` (hoặc tương đương) với input không tin cậy
- Tin rằng đã "sanitize 1 lần" là đủ trong mọi context
- Chạy app bằng quyền root/admin khi không cần thiết

## 9. Mapping "nguyên nhân -> hậu quả -> giải pháp"

| Nguyên nhân                 | Hậu quả                 | Giải pháp ưu tiên                                                     |
| --------------------------- | ----------------------- | --------------------------------------------------------------------- |
| Nối command string từ input | Thực thi lệnh tùy ý     | Dùng API không qua shell, argument array                              |
| Validation theo blocklist   | Dễ bị bypass            | Allow-list theo định dạng nghiệp vụ                                   |
| Dùng API exec nguy hiểm     | Mở rộng bề mặt tấn công | Chuyển sang API an toàn hơn (`execFile`, `subprocess` shell=False...) |
| Quyền runtime quá rộng      | Leo thang tác động      | Least privilege + hardening hệ thống                                  |
| Lộ thông tin lỗi/diagnostic | Dễ recon nhanh hơn      | Generic error cho user + log nội bộ                                   |

## 10. Kết luận

CMDi là lỗi "thiết kế giao tiếp với shell", không đơn thuần là ký tự đặc biệt.

Nếu tóm gọn 1 câu:

- Khi input không tin cậy đi qua shell parser, CMDi sẽ xuất hiện.
- Khi loại bỏ shell không cần thiết, tham số hóa đúng cách và hạn chế quyền, CMDi bị triệt tiêu từ gốc.

Do đó, mục tiêu bảo mật không phải là viết bộ lọc ngày càng phức tạp, mà là thiết kế lại luồng thực thi hệ thống để input không thể đổi nghĩa command.
