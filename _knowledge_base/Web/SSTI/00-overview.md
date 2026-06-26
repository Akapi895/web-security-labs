# Server-Side Template Injection (SSTI) - Tổng Quan

## Định Nghĩa

**Server-Side Template Injection (SSTI)** là một lỗ hổng bảo mật xảy ra khi dữ liệu do người dùng cung cấp được nhúng trực tiếp vào template code (code template) thay vì được truyền như dữ liệu (data context), dẫn đến việc template engine thực thi các chỉ thị mã độc trên máy chủ.

### Cơ Chế Tấn Công

SSTI tận dụng cách mà các ứng dụng web xây dựng động các template bằng cách ghép nối (concatenation) hoặc render trực tiếp dữ liệu do người dùng kiểm soát vào template trước khi được xử lý bởi template engine.

**Ví dụ thực tế:**

```python
# Lỗ hổng SSTI
user_input = request.args.get('name')
output = template.render("Hello " + user_input)  # Ghép nối trực tiếp

# Không lỗ hổng - sử dụng dữ liệu
output = template.render("Hello {{name}}", {"name": user_input})  # Truyền dữ liệu
```

Khi template engine xử lý template, nó sẽ đánh giá (evaluate) bất kỳ cú pháp template engine nào được tìm thấy, bao gồm cả mã độc do attacker inject.

## Tác Động

SSTI có thể dẫn đến các hậu quả nghiêm trọng:

| Hậu Quả                           | Mô Tả                                                        |
| --------------------------------- | ------------------------------------------------------------ |
| **Remote Code Execution (RCE)**   | Attacker có thể thực thi mã tùy ý trên máy chủ               |
| **Truy cập dữ liệu nhạy cảm**     | Đọc file hệ thống, biến môi trường, API keys                 |
| **Chiếm quyền kiểm soát máy chủ** | Thực hiện các lệnh hệ thống, làm thay đổi cấu hình           |
| **Lateral movement**              | Sử dụng máy chủ bị compromised để tấn công các hệ thống khác |

## Các Template Engine Phổ Biến

### Theo Ngôn Ngữ

| Ngôn Ngữ               | Template Engine            | Cú Pháp          | Độ Nguy Hiểm |
| ---------------------- | -------------------------- | ---------------- | ------------ |
| **Python**             | Jinja2, Mako, Django       | `{{ }}`, `${ }`  | Cao          |
| **PHP**                | Twig, Smarty, Blade        | `{{ }}`, `{ }`   | Cao          |
| **Java**               | FreeMarker, Velocity, SpEL | `${ }`, `#{ }`   | Cao          |
| **JavaScript/Node.js** | Handlebars, Pug, EJS       | `{{ }}`, `<% %>` | Cao          |
| **Ruby**               | ERB, Haml, Liquid          | `<%= %>`, `#{ }` | Cao          |
| **.NET**               | Razor                      | `@{ }`           | Trung bình   |
| **Elixir**             | EEx                        | `<%= %>`         | Cao          |

## Ngữ Cảnh Xuất Hiện SSTI

### 1. Plaintext Context

User input được ghép nối vào template như một chuỗi văn bản:

```twig
{# Twig #}
render('Hello ' + username)
```

Attacker có thể inject biểu thức template:

```
username = {{7*7}}
```

Output: `Hello 49`

### 2. Code Context

User input được đặt trong một biểu thức template:

```twig
{# Twig #}
render("Hello {{" + greeting + "}}", data)
```

Attacker có thể break out khỏi biểu thức hiện tại:

```
greeting = username}}<tag>
```

Output: `Hello username<tag>`

## Vai Trò Template Engine

Template engine là một phần mềm xử lý template - một chuỗi văn bản chứa:

- **Nội dung tĩnh**: HTML, văn bản thường
- **Placeholder/Variables**: `{{ }}`, `<% %>` - để chèn dữ liệu động
- **Biểu thức logic**: if/else, loops, filters để xử lý dữ liệu

### Quy Trình Render Chuẩn

```
Template File + Data Context → Template Engine → Output HTML
```

**Ví dụ:**

Template:

```twig
Hello {{ user.name }}!
```

Data:

```json
{ "user": { "name": "Alice" } }
```

Output:

```
Hello Alice!
```

### Điểm Khác Biệt: Template vs Data

**Template (mã)** - được xử lý bởi template engine:

```twig
{{7*7}}        # Được đánh giá → 49
{%if x%}       # Câu lệnh điều kiện
```

**Data (dữ liệu)** - được truyền như context:

```json
{"user": "{{7*7}}"}  # Treated as literal string → "{{7*7}}"
```

### Vì Sao SSTI Nguy Hiểm

Khi dữ liệu người dùng được **ghép nối vào template**, nó trở thành **phần của template code**, không phải data:

```python
# Mã lỗ hổng
template_string = "Hello " + user_input
engine.render(template_string)  # user_input được parse như template code

# Mã an toàn
template_string = "Hello {{ username }}"
engine.render(template_string, {"username": user_input})  # user_input như data
```

## Điều Kiện Hình Thành SSTI

1. **Ứng dụng sử dụng template engine** để xây dựng dynamic content
2. **Dữ liệu người dùng được ghép nối trực tiếp vào template** (không được escape/sanitize)
3. **Template engine xử lý template** trước rendering
4. **Không có sandbox hoặc sandbox bị bypass** để giới hạn xử lý template

## Phân Biệt SSTI với Client-Side Template Injection (CSTI)

| Tiêu Chí      | SSTI                              | CSTI                                |
| ------------- | --------------------------------- | ----------------------------------- |
| **Vị trí**    | Máy chủ                           | Trình duyệt client                  |
| **Thực thi**  | Code phía server                  | Code phía client (JS)               |
| **Tác động**  | RCE trên server, truy cập backend | XSS, DOM-based attacks              |
| **Nguy Hiểm** | Cao (toàn bộ server compromised)  | Trung bình (session theft, malware) |

## Tổng Quát Quy Trình Khai Thác

```
1. Phát hiện (Detect)
   ↓
2. Xác định Template Engine (Identify)
   ↓
3. Khai thác để có RCE
   - Đánh giá biểu thức đơn giản
   - Access object nội bộ
   - Gọi hàm nguy hiểm
   - Thực thi lệnh hệ thống
```

## Tài Liệu Liên Quan

- [01-fundamentals.md](01-fundamentals.md) - Kiến thức cơ bản về template engine
- [02-vulnerability-analysis.md](02-vulnerability-analysis.md) - Phân tích chi tiết nguyên nhân lỗ hổng
- [03-detection-identification.md](03-detection-identification.md) - Phátỉ hiện và xác định template engine
