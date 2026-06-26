# 01 - Kiến Thức Cơ Bản về Template Engine

## Template Engine Là Gì?

Template engine là một công cụ phần mềm cho phép lập trình viên tách biệt logic xử lý dữ liệu khỏi presentation (giao diện). Nó xử lý các file template chứa placeholder và biểu thức, sau đó thay thế những phần này bằng dữ liệu thực tế.

### Các Thành Phần Chính

**1. Template (Mẫu)**

- Một chuỗi văn bản (HTML, email, etc.)
- Chứa nội dung tĩnh và placeholder
- Viết bằng cú pháp riêng của template engine

**Ví dụ (Jinja2):**

```jinja2
<h1>Welcome, {{ user.name }}!</h1>
<p>You have {{ user.notifications | length }} notifications</p>
{% if user.is_admin %}
  <p>Admin Panel: <a href="/admin">Click here</a></p>
{% endif %}
```

**2. Data Context (Dữ Liệu)**

- Các biến và object được truyền vào template
- Được sử dụng để điền vào placeholder

```json
{
  "user": {
    "name": "Alice",
    "notifications": [1, 2, 3],
    "is_admin": true
  }
}
```

**3. Template Engine (Engine)**

- Đọc template
- Parse cú pháp template engine
- Đánh giá biểu thức
- Thay thế placeholder bằng dữ liệu
- Trả về output cuối cùng

## Quy Trình Render Chi Tiết

```
┌─────────────────────────────────────────────────────┐
│ Input: Template + Data Context                      │
├─────────────────────────────────────────────────────┤
│ 1. Lexer: Chia template thành tokens                │
│ 2. Parser: Xây dựng Abstract Syntax Tree (AST)     │
│ 3. Compiler: Chuyển đổi AST thành code             │
│ 4. Evaluator: Thực thi code với data context       │
│ 5. Renderer: Sinh ra output HTML                    │
├─────────────────────────────────────────────────────┤
│ Output: Rendered HTML                               │
└─────────────────────────────────────────────────────┘
```

### Ví Dụ Chi Tiết - Jinja2

**Template:**

```jinja2
Total: {{ items | sum }}
```

**Data:**

```json
{ "items": [1, 2, 3] }
```

**Quy trình:**

1. **Lexer**: `{{ items | sum }}` → `[VAR, IDENT(items), FILTER, IDENT(sum)]`

2. **Parser**: Tạo AST biểu diễn biểu thức filter

3. **Compiler**: Tạo bytecode để thực thi filter

4. **Evaluator**:
   - Lấy giá trị `items` từ context: `[1, 2, 3]`
   - Áp dụng filter `sum`: `6`

5. **Renderer**: Output `Total: 6`

## Cú Pháp Cơ Bản Các Template Engine Phổ Biến

### Python - Jinja2

```jinja2
{# Comment #}
{{ variable }}                    {# Output variable #}
{{ user.name }}                   {# Access attribute #}
{{ items[0] }}                    {# Access index #}
{{ value | default('N/A') }}      {# Apply filter #}
{% if condition %}...{% endif %}  {# Conditional #}
{% for item in items %}...{% endfor %}  {# Loop #}
{% set var = 'value' %}           {# Set variable #}
```

### Python - Mako

```mako
${ variable }                     {# Output variable #}
<% code in Python %>              {# Python code block #}
<%
  result = some_function()
  print(result)
%>
```

### PHP - Twig

```twig
{# Comment #}
{{ variable }}
{{ user.getName() }}
{% if condition %}...{% endif %}
{% for item in items %}...{% endfor %}
```

### PHP - Smarty

```smarty
{* Comment *}
{$variable}
{$user->getName()}
{if $condition}...{/if}
{foreach $items as $item}...{/foreach}
```

### Java - FreeMarker

```freemarker
<#-- Comment -->
${variable}
${user.name}
<#if condition>...</#if>
<#list items as item>...</#list>
```

### Java - Velocity

```velocity
## Comment
$variable
$user.getName()
#if($condition)...#end
#foreach($item in $items)...#end
```

### JavaScript/Node.js - Handlebars

```handlebars
{{! Comment }}
{{variable}}
{{user.name}}
{{#if condition}}...{{/if}}
{{#each items}}...{{/each}}
```

### Ruby - ERB

```erb
<% # Comment %>
<%= variable %>
<%= user.name %>
<% if condition %>...<% end %>
<% items.each do |item| %>...<% end %>
```

## Hoạt Động của Biểu Thức Template

### Variable Lookup (Tra Cứu Biến)

Khi template engine gặp `{{ name }}`, nó:

1. Tìm kiếm key `name` trong data context
2. Nếu không tìm thấy, thử các fallback:
   - Global scope
   - Built-in objects
   - Có thể null hoặc empty string
3. Chuyển đổi sang string nếu cần
4. Xuất output

**Ví dụ (Jinja2):**

```jinja2
{{ undefined_var }}     {# Output: (trống) #}
{{ none_var or 'default' }}  {# Output: default #}
```

### Attribute/Method Access

```jinja2
{{ user.name }}         {# Truy cập thuộc tính name #}
{{ user['name'] }}      {# Truy cập như dictionary #}
{{ user.getName() }}    {# Gọi method #}
```

**Cơ chế:**

- Engine cố gắng truy cập theo thứ tự: property → dictionary key → method
- Kết quả thường được cache

### Filters/Transformations

Filters là các hàm được áp dụng trên dữ liệu:

```jinja2
{{ text | uppercase }}
{{ text | truncate(10) }}
{{ items | length }}
{{ value | default('N/A') }}
```

### Biểu Thức Logic

Các template engine cho phép các biểu thức không quá phức tạp:

```jinja2
{{ 7 * 7 }}             {# Arithmetics #}
{{ 'hello' + ' world' }} {# String concatenation #}
{{ value > 10 }}        {# Comparison #}
{{ a and b or c }}      {# Boolean logic #}
```

## Scope và Context

### Global Scope

Các biến được định nghĩa toàn cục trong template engine:

```jinja2
{{ self }}              {# Tham chiếu đến template hiện tại #}
{{ loop }}              {# Biến loop trong vòng lặp #}
{{ range(5) }}          {# Built-in function #}
```

### Local Scope

Các biến được định nghĩa cục bộ:

```jinja2
{% for item in items %}
  {{ item }}            {# item là local scope trong loop #}
{% endfor %}
```

### Namespace/Object Attributes

Truy cập vào object properties:

```python
class User:
    name = "Alice"
    email = "alice@example.com"
    def get_display_name(self):
        return f"{self.name} ({self.email})"

# Trong template:
{{ user.name }}
{{ user.get_display_name() }}
```

## Template Inheritance (Kế Thừa)

Một tính năng quan trọng của các template engine hiện đại:

```jinja2
{# base.html #}
<html>
  <head><title>{% block title %}{% endblock %}</title></head>
  <body>
    {% block content %}{% endblock %}
  </body>
</html>

{# page.html #}
{% extends "base.html" %}
{% block title %}My Page{% endblock %}
{% block content %}<p>Hello World</p>{% endblock %}
```

Tính năng này có thể là vector tấn công nếu template names được kiểm soát bởi user.

## Macros/Include (Bao Gồm)

Cho phép tái sử dụng code template:

```jinja2
{% macro greeting(name) %}
  Hello {{ name }}!
{% endmacro %}

{{ greeting('Alice') }}

{# Include file #}
{% include 'header.html' %}
```

## Object Introspection (Nội Soi Object)

Nhiều template engine cho phép inspect object:

```jinja2
{{ object.__class__ }}
{{ object.__dict__ }}
{{ dir(object) }}
```

Đây là kỹ thuật quan trọng để exploit SSTI - attacker có thể:

1. Lấy class của object
2. Truy cập các attributes
3. Gọi các methods không dự kiến
4. Access runtime modules

## Sandbox vs Unsandboxed

### Unsandboxed (Nguy Hiểm)

- Template engine có toàn quyền truy cập
- Có thể nhập module (import os, subprocess)
- Có thể gọi hàm hệ thống
- SSTI → RCE ngay lập tức

**Ví dụ (Mako unsandboxed):**

```mako
<%
import os
os.system('whoami')
%>
```

### Sandboxed (Hạn Chế)

- Các module/hàm nguy hiểm bị cấm
- Chỉ cho phép một tập hợp các biểu thức an toàn
- SSTI vẫn nguy hiểm nhưng cần bypass logic

**Ví dụ (Jinja2 sandboxed):**

```python
from jinja2.sandbox import SandboxedEnvironment
env = SandboxedEnvironment()
```

## Access Modifiers (Kiểm Soát Truy Cập)

Một số template engine cho phép kiểm soát:

```jinja2
{# Ở Jinja2, một số attribute bị giới hạn #}
{{ object._private }}    {# Có thể bị chặn #}
{{ object.__class__ }}   {# Có thể bị chặn #}
```

## Tài Liệu Liên Quan

- [00-overview.md](00-overview.md) - Tổng quan về SSTI
- [02-vulnerability-analysis.md](02-vulnerability-analysis.md) - Phân tích lỗ hổng
- [03-detection-identification.md](03-detection-identification.md) - Phát hiện và xác định
