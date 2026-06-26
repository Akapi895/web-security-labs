# Essential Skills (PortSwigger Web Security Academy)

## Tổng quan

Theo em, ý chính của phần này là:

- Lab chỉ mô phỏng một tình huống, còn thực tế có nhiều biến thể hơn.
- Cần biết chỉnh payload để vượt filter/WAF.
- Nên kết hợp manual testing với công cụ để làm nhanh và chính xác hơn.

---

## 1. Obfuscating attacks using encodings

### Main idea

Obfuscation là đổi cách biểu diễn payload, nhưng khi backend decode thì ý nghĩa vẫn giữ nguyên.

- Mục tiêu: bypass filter dựa trên pattern đơn giản.
- Điểm quan trọng: mỗi tầng (client/proxy/WAF/backend) có thể decode khác nhau.

### Các kỹ thuật cần nhớ

- URL Encoding: encode ký tự đặc biệt.

```text
<script> -> %3Cscript%3E
```

- Double URL Encoding: encode 2 lần khi WAF/backend decode không đồng nhất.
- HTML Entity Encoding: dùng `&#x..;` hoặc `&#..;`.

```html
<img onerror="&#x61;lert(1)" />
```

- Leading Zeros: thêm số `0` để né filter thô.

```html
&#00000061;
```

- JS Escaping (Unicode/Hex/Octal):

```js
\u0061lert(1)
\x61lert(1)
\141lert(1)
```

- Multiple Encoding: chồng nhiều lớp encode.

```text
&bsol;u0061 -> \u0061 -> a
```

- SQL CHAR(): dựng từ khóa SQL bằng mã ASCII.

```sql
CHAR(83)+CHAR(69)+CHAR(76)+CHAR(69)+CHAR(67)+CHAR(84)
```

- XML Encoding: hữu ích khi dữ liệu đi qua XML parser (nhất là khi test SQLi/XXE).

---

## 2. Using Burp Scanner During Manual Testing

### Main idea

Burp Scanner giúp tiết kiệm thời gian, nhưng hiệu quả phụ thuộc vào việc chọn đúng chỗ để scan.

### Cách em áp dụng

1. Scan nhanh một request:

- Right click request -> **Do active scan**

2. Scan đúng insertion point:

- Highlight phần nghi ngờ
- Chọn **Scan selected insertion point**

3. Với dữ liệu không chuẩn (ví dụ `user=048857-carlos`):

- Burp có thể coi cả chuỗi là một giá trị
- Cần tách từng phần để scan riêng
- Nếu cần linh hoạt hơn thì dùng Intruder để đặt nhiều insertion points

---

## Kết luận

Key takeaway:

- Obfuscation hiệu quả khi hiểu luồng decode.
- Burp Scanner mạnh nhất khi chọn đúng insertion point.
- Kết hợp manual testing + scanner cho kết quả tốt hơn dùng riêng lẻ.
