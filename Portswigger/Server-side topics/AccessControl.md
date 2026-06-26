# Access Control - Báo Cáo Tổng Hợp

## 1. Access control là gì và bản chất kỹ thuật

Access control là cơ chế xác định ai được phép làm gì trên tài nguyên nào, trong bối cảnh nào.

Trong ứng dụng web, access control phụ thuộc vào 3 thành phần:

- Authentication: xác minh danh tính người dùng
- Session management: liên kết request với danh tính đã đăng nhập
- Authorization (access control): quyết định hành động nào được phép

Nếu tóm gọn trong 1 câu:

- Authentication trả lời "bạn là ai".
- Access control trả lời "bạn được làm gì".

Lỗi broken access control xảy ra khi ứng dụng không ràng buộc đúng quyền trên server-side, khiến người dùng thực hiện được hành động hoặc truy cập dữ liệu ngoài quyền được cấp.

## 2. Mô hình access control và ma trận rủi ro

### 2.1 Vertical access control

Hạn chế chức năng nhạy cảm theo vai trò (user, moderator, admin).

Lỗi thường gặp:

- User thường truy cập được endpoint admin
- Bypass check role bằng cách sửa tham số role/cookie

### 2.2 Horizontal access control

Hạn chế dữ liệu cùng loại theo từng chủ sở hữu.

Lỗi thường gặp:

- User A đọc/sửa dữ liệu của user B
- Tampering ID, UUID, orderId, customer_number

### 2.3 Context-dependent access control

Hạn chế theo trạng thái hoặc thứ tự nghiệp vụ.

Lỗi thường gặp:

- Bỏ qua các bước xác nhận trong quy trình nhiều bước
- Thực hiện hành động khi điều kiện nghiệp vụ chưa hợp lệ

## 3. Nguyên nhân gốc rễ

Broken access control không phải do 1 payload cụ thể, mà do thiết kế và thi hành quyền không đồng nhất.

### 3.1 Nguyên nhân kỹ thuật

- Chỉ ẩn link/URL trên UI mà không enforce quyền ở backend
- Tin vào dữ liệu do client kiểm soát (`role`, `isAdmin`, hidden field, query param, cookie)
- Kiểm tra quyền phân tán, mỗi endpoint làm một kiểu
- Sai lệch URL matching giữa reverse proxy, framework và middleware
- Chỉ chặn một HTTP method (POST) nhưng bỏ sót method khác (GET, PUT...)
- Kiểm tra quyền ở bước 1-2 nhưng bỏ qua bước xác nhận cuối
- Dựa vào `Referer` để quyết định quyền truy cập

### 3.2 Nguyên nhân tổ chức/thiết kế

- Không có ma trận quyền rõ ràng theo tài nguyên-hành động-vai trò
- Không áp dụng nguyên tắc deny by default
- Không kiểm thử đặc thù cho authorization trong SDLC

## 4. Các dạng lỗi điển hình

### 4.1 Unprotected functionality

Chức năng nhạy cảm có thể gọi trực tiếp qua URL nếu biết đường dẫn.

Ví dụ:

- `/admin`
- `/admin/deleteUser`

Security by obscurity (đổi URL khó đoán) không phải là access control.

### 4.2 Parameter-based access control

Ứng dụng quyết định quyền dựa trên giá trị client gửi lên:

- `?admin=true`
- `?role=1`

Người tấn công chỉ cần sửa tham số để leo thang quyền.

### 4.3 Platform misconfiguration và URL override

Nếu hệ thống cho phép header override URL (như `X-Original-URL`, `X-Rewrite-URL`) thì có thể bypass lớp chặn phía trước.

### 4.4 URL-matching discrepancies

Sai lệch khi map endpoint:

- khác hoa thường/hoa (`/ADMIN/DELETEUSER`)
- thêm đuôi file extension
- thêm dấu `/` cuối đường dẫn

Nếu lớp authz và app route không đồng bộ, có thể bypass được quyền.

### 4.5 IDOR (Insecure Direct Object Reference)

Đây là dạng lỗi kinh điển của horizontal privilege escalation.

Bản chất:

- Input do client kiểm soát được dùng trực tiếp để truy cập object
- Không có kiểm tra owner/permission trên object đó

Ví dụ:

- `/myaccount?id=123` đổi thành `/myaccount?id=124`
- `/static/12144.txt` đổi thành `/static/12145.txt`

## 5. Horizontal to vertical privilege escalation

Một lỗi horizontal có thể trở thành vertical nếu đối tượng bị truy cập trái phép là tài khoản có đặc quyền cao hơn.

Ví dụ:

- User thường chiếm được tài khoản admin qua IDOR/reset flow
- Sau đó sử dụng quyền admin để truy cập chức năng quản trị

Ý nghĩa bảo mật:

- Không thể đánh giá horizontal là "mức độ thấp" một cách cơ học
- Cần xét chuỗi leo thang theo graph quyền

## 6. Cách phát hiện theo tư duy hệ thống

Mục tiêu phát hiện:

1. Có bypass quyền hay không
2. Bypass ở tầng nào (endpoint, object, workflow, method, header)
3. Tác động đến tài nguyên nào

### 6.1 Kiểm thử theo ma trận quyền

Lập bảng kiểm thử theo trục:

- Role (anonymous/user/admin)
- Resource (profile, order, invoice, admin action)
- Action (read/create/update/delete/approve)

### 6.2 Kiểm thử endpoint và method

- Thử truy cập trực tiếp endpoint nhạy cảm
- Thử đổi HTTP method trên cùng hành động
- Thử biến thể URL (case, slash, extension)

### 6.3 Kiểm thử object-level authorization

- Tampering ID/UUID/slug/reference
- Kiểm tra phản hồi khi truy cập object không thuộc sở hữu
- Đảm bảo server trả về đúng trạng thái và không lộ dữ liệu nhạy cảm trong response redirect

### 6.4 Kiểm thử workflow authorization

- Thử bỏ qua bước trung gian trong quy trình nhiều bước
- Gửi trực tiếp request của bước xác nhận cuối

### 6.5 Kiểm thử tín hiệu quyền từ client

- Sửa hidden field, cookie, query param liên quan role
- Thử giả mạo `Referer` và các header điều hướng

## 7. Quy trình khai thác mang tính phương pháp

1. Recon endpoint/chức năng theo role.
2. Chọn vector bypass (URL, method, parameter, object reference, workflow).
3. Xác nhận oracle (status code, response body, state change).
4. Mở rộng từ read sang write/delete/approve.
5. Thử chuỗi leo thang horizontal -> vertical.
6. Đánh giá tác động kinh doanh (dữ liệu, tài chính, vận hành, tuân thủ).

Bản chất của quy trình này là biến lỗi authz thành abuse path hoàn chỉnh.

## 8. Tác động bảo mật

### 8.1 Confidentiality

- Lộ dữ liệu người dùng khác
- Lộ tài liệu nội bộ, log, transcript, metadata

### 8.2 Integrity

- Sửa thông tin profile, đơn hàng, quyền, cấu hình
- Thực hiện hành động quản trị trái phép (xóa user, đổi role)

### 8.3 Availability

- Trigger hành động gây gián đoạn hệ thống
- Abuse endpoint quản trị làm ảnh hưởng vận hành

## 9. Phòng thủ đúng bản chất

### 9.1 Nguyên tắc cốt lõi

1. Deny by default với mọi resource không public.
2. Enforce authorization ở backend cho mọi request.
3. Sử dụng cơ chế tập trung (policy/middleware) thay vì check rời rạc.
4. Kiểm tra object-level permission theo owner/tenant/role.
5. Không tin vào bất kỳ tín hiệu quyền nào do client gửi lên.

### 9.2 Kiểm soát bổ trợ

- Chuẩn hóa route matching giữa gateway/proxy/app
- Chốt method cho từng endpoint và reject method ngoài hợp đồng
- Loại bỏ sự phụ thuộc vào `Referer` trong quyết định quyền
- Logging sự kiện authz (allow/deny) để audit và phát hiện bất thường
- Test tự động cho authorization theo ma trận role-resource-action

### 9.3 Anti-pattern cần tránh

- Che URL admin rồi coi như đã an toàn
- Kiểm tra quyền ở frontend thay vì backend
- Truyền và tin `isAdmin=true` từ client
- Chỉ test happy-path theo vai trò đúng

## 10. Mapping "nguyên nhân -> hậu quả -> giải pháp"

| Nguyên nhân                     | Hậu quả                              | Giải pháp ưu tiên                                             |
| ------------------------------- | ------------------------------------ | ------------------------------------------------------------- |
| Không enforce quyền ở backend   | Truy cập trái phép endpoint nhạy cảm | Authorization middleware/policy bắt buộc mọi request          |
| Tin role từ cookie/param/client | Leo thang quyền vertical             | Role/permission chỉ lấy từ server-side session/token đã ký    |
| Không check owner object        | IDOR, lộ dữ liệu ngang cấp           | Object-level authorization theo owner/tenant                  |
| Sai lệch URL/method matching    | Bypass qua biến thể đường dẫn/method | Chuẩn hóa route + enforce method nhất quán                    |
| Bỏ sót bước cuối trong workflow | Vượt quy trình phê duyệt/xác nhận    | Kiểm tra quyền và trạng thái ở mọi bước, đặc biệt bước commit |

## 11. Kết luận

Broken access control là lỗi thiết kế và thi hành quyền, không phải lỗi payload đơn lẻ.

Nếu cần nhớ 2 câu:

- Nếu backend không xác minh quyền trên mọi request và mọi object, bypass sẽ xảy ra sớm hoặc muộn.
- Nếu áp dụng deny by default, enforce tập trung, và object-level checks nghiêm ngặt, nhóm lỗi access control sẽ giảm mạnh từ gốc.
