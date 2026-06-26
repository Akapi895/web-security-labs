# Lab: Server-side template injection using documentation

## Mục tiêu

Xác định FreeMarker, tìm cách gọi class thực thi lệnh từ documentation, rồi xóa `morale.txt` của Carlos.

## Ý tưởng lỗi

Template cho phép expression kiểu `${...}` và có thể lộ error khi tham chiếu tới biến không tồn tại. Từ đó ta xác định engine, rồi tra docs để tìm primitive thực thi code.

## Writeup từng bước: từ detect đến exploit

### Bước 1: Detect engine

1. Sửa template mô tả sản phẩm và chèn thử:

`${7*7}`

2. Nếu preview trả về `49`, template đang evaluate expression.
3. Thử thêm `${foobar}` để ép lỗi.
4. Error message cho biết đây là FreeMarker template.

### Bước 2: Tìm primitive trong documentation

1. Đọc FreeMarker docs phần `new()` built-in.
2. Docs chỉ ra `new()` có thể tạo object Java implement `TemplateModel`.
3. Tra `TemplateModel` JavaDoc và tìm class `Execute`.
4. `Execute` cho phép chạy shell command.

### Bước 3: Exploit để solve lab

1. Chèn payload:

`<#assign ex="freemarker.template.utility.Execute"?new()> ${ ex("rm /home/carlos/morale.txt") }`

2. Xóa phần syntax lỗi cũ nếu còn.
3. Save template và mở lại product page để thực thi payload.

## Vì sao detect này đáng tin cậy?

`${7*7}` xác nhận có template evaluation, còn `${foobar}` giúp định danh engine là FreeMarker. Sau đó docs dẫn thẳng tới `Execute`, nên đường exploit rất rõ ràng và ổn định.

## Gợi ý phòng thủ

1. Không cho user chỉnh template trực tiếp nếu không có sandbox.
2. Chặn các built-in nguy hiểm như `new()`.
3. Giới hạn class/object mà template được phép khởi tạo.
