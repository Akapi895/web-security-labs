# 20 - Phòng Chống và Giảm Thiểu SSTI

## Chiến Lược Phòng Chống (Defense in Depth)

```
┌──────────────────────────────────────────┐
│ Layer 1: Secure Architecture             │
│ - Never concatenate user input           │
│ - Use pre-compiled templates             │
│ - Separate template from data            │
├──────────────────────────────────────────┤
│ Layer 2: Input Validation & Sanitization │
│ - Whitelist approach                     │
│ - Escape template syntax                 │
│ - Validate template names                │
├──────────────────────────────────────────┤
│ Layer 3: Template Engine Configuration   │
│ - Sandboxing                             │
│ - Restricted object whitelist            │
│ - Disable dangerous functions            │
├──────────────────────────────────────────┤
│ Layer 4: Runtime Environment             │
│ - Limited file permissions               │
│ - Containerization                       │
│ - Firewall restrictions                  │
├──────────────────────────────────────────┤
│ Layer 5: Detection & Monitoring          │
│ - WAF rules                              │
│ - Logging & alerting                     │
│ - Regular scanning                       │
└──────────────────────────────────────────┘
```

## Layer 1: Secure Architecture

### Principle 1: Separate Template Logic từ Data

**❌ VULNERABLE:**

```python
# Flask - concatenating user input
@app.route('/greet')
def greet():
    name = request.args.get('name')
    template = Template("Hello " + name)  # WRONG!
    return template.render()
```

**✓ SAFE:**

```python
# Flask - passing data as context
@app.route('/greet')
def greet():
    name = request.args.get('name')
    template = Template("Hello {{ name }}")
    return template.render(name=name)  # Correct!
```

### Principle 2: Pre-Compiled Templates

**❌ VULNERABLE:**

```python
# Dynamic template loading
template_source = open(f"templates/{params['template']}.html").read()
template = Template(template_source)
```

**✓ SAFE:**

```python
# Pre-compiled at startup
from jinja2 import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader('templates'))
template = env.get_template('safe-template.html')  # Fixed template name
```

### Principle 3: No Dynamic Template Content

**❌ VULNERABLE:**

```python
# User can input template content
user_template = request.form.get('email_template')
engine.render(user_template, context)
```

**✓ SAFE:**

```python
# Template names only, content is fixed
template_choice = request.form.get('template_type')
if template_choice in ['welcome', 'confirmation', 'notification']:
    template = engine.get_template(f"{template_choice}.html")
    return template.render(context)
```

## Layer 2: Input Validation & Sanitization

### Whitelist Template Names

```python
ALLOWED_TEMPLATES = {
    'welcome': 'templates/welcome.html',
    'confirmation': 'templates/confirmation.html',
    'notification': 'templates/notification.html',
}

def safe_get_template(template_name):
    if template_name not in ALLOWED_TEMPLATES:
        raise ValueError("Invalid template name")
    return ALLOWED_TEMPLATES[template_name]
```

### Escape Template Syntax

```python
import re

def escape_template_syntax(user_input):
    # Escape common template syntax
    user_input = user_input.replace('{{', '{ {')
    user_input = user_input.replace('}}', '} }')
    user_input = user_input.replace('{%', '{ %')
    user_input = user_input.replace('%}', '% }')
    user_input = user_input.replace('<%', '< %')
    user_input = user_input.replace('%>', '% >')
    return user_input
```

### Validate Template Names

```python
import re

def is_valid_template_name(name):
    # Only alphanumeric and underscore
    if not re.match(r'^[a-zA-Z0-9_]+$', name):
        return False
    # No directory traversal
    if '..' in name or '/' in name or '\\' in name:
        return False
    return True

template_name = request.args.get('template')
if not is_valid_template_name(template_name):
    abort(400)
```

### HTML Entity Encoding

```python
import html

def safe_render(template_string, context):
    # Encode user input dalam context
    safe_context = {}
    for key, value in context.items():
        if isinstance(value, str):
            safe_context[key] = html.escape(value)
        else:
            safe_context[key] = value
    return template.render(safe_context)
```

## Layer 3: Template Engine Configuration

### Jinja2 Safe Configuration

```python
from jinja2 import Environment, select_autoescape
from jinja2.sandbox import SandboxedEnvironment

# Sandboxed environment
env = SandboxedEnvironment(
    autoescape=select_autoescape(['html', 'xml']),
    trim_blocks=True,
    lstrip_blocks=True,
)

# Restrict builtins
safe_context = {
    'user_name': user.name,
    'items': items,
    # Don't include: os, sys, subprocess, __import__
}

template = env.from_string("Hello {{ user_name }}")
output = template.render(safe_context)
```

### Twig (PHP) Safe Configuration

```php
<?php
use Twig\Environment;
use Twig\Loader\FileSystemLoader;
use Twig\Sandbox\SandboxExtension;
use Twig\Sandbox\SecurityPolicy;

// Define what's allowed
$policy = new SecurityPolicy(
    ['range', 'constant', 'cycle'],  // functions
    ['abs', 'capitalize', 'upper'],   // filters
    ['for', 'if', 'set'],              // tags
    [],                                 // attributes
    []                                  // methods
);

$twig = new Environment(new FileSystemLoader('templates/'));
$twig->addExtension(new SandboxExtension($policy));

// Use with limited context
$template = $twig->load('safe.html');
echo $template->render(['name' => $user_input]);
?>
```

### FreeMarker Safe Configuration

```java
import freemarker.template.Configuration;
import freemarker.template.TemplateException;

Configuration config = new Configuration(Configuration.VERSION_2_3_31);
config.setClassLoaderForTemplateLoading(MyClass.class.getClassLoader(), "templates");

// Restrict object wrapper and class loading
config.setNewBuiltinClassResolver(Configuration.SAFER_RESOLVER);
config.setMaxTemplateNestingLevel(100);

// Pass limited data model
Map<String, Object> dataModel = new HashMap<>();
dataModel.put("user", user.getName());  // Only safe values
dataModel.put("items", items);

Template template = config.getTemplate("safe.ftl");
template.process(dataModel, out);
```

### Django Template Safe Configuration

```python
# settings.py
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            # Disable autoescape only if absolutely necessary
            'autoescape': True,  # Enable autoescaping
        },
    },
]

# View code
from django.template.loader import render_to_string
context = {
    'user_name': user.name,  # Automatically escaped
    'items': items,
}
html = render_to_string('safe-template.html', context)
```

### Mako Safe Configuration

```python
from mako.template import Template
from mako.lookup import TemplateLookup

# Restrict module imports
lookup = TemplateLookup(
    directories=['templates/'],
    module_directory='/tmp/mako_modules/',
    strict_undefined=True,
)

# Limited context
safe_context = {
    'user_name': user.name,
    'items': items,
}

template = lookup.get_template('safe.html')
output = template.render(**safe_context)
```

### Ruby ERB Safe Configuration

```ruby
require 'erb'

# Define safe helper methods
module SafeHelpers
  def escape_html(text)
    ERB::Util.html_escape(text)
  end

  def safe_url(url)
    # Whitelist URLs
    url.start_with?('/') ? url : '/'
  end
end

# Create context dengan safe methods
template_string = "<%= escape_html(name) %>"
erb = ERB.new(template_string)

# Pass limited data
safe_binding = Object.new.instance_eval do
  extend SafeHelpers
  define_singleton_method(:name) { user.name }
  binding
end

output = erb.result(safe_binding)
```

## Layer 4: Runtime Environment

### File System Permissions

```bash
# Restrict template engine process
# Run as unprivileged user
sudo -u templateuser app.py

# Limit file access via chroot
chroot /var/app /bin/app

# SELinux/AppArmor
aa-complain /path/to/app
```

### Containerization

```dockerfile
FROM python:3.9-slim

# Non-root user
RUN useradd -m -u 1000 appuser

# Minimal dependencies
RUN pip install --no-cache-dir jinja2

# Mount template directory as read-only
COPY templates/ /app/templates/

USER appuser

WORKDIR /app

# Restrict network
CMD ["python", "app.py"]
```

### Docker Capabilities Limitation

```yaml
version: "3"
services:
  app:
    image: myapp
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL
    cap_add:
      - NET_BIND_SERVICE
    read_only: true
    tmpfs:
      - /tmp
```

## Layer 5: Detection & Monitoring

### WAF Rules (ModSecurity)

```
# Detect template injection syntax
SecRule ARGS|HEADERS|BODY "@rx \{\{.*?\}\}|<%.*?%>|<#.*?#>" \
    "id:1000,phase:2,deny,status:403,msg:'Template Injection Detected'"

# Detect Python __import__
SecRule ARGS|HEADERS|BODY "@contains __import__" \
    "id:1001,phase:2,deny,status:403,msg:'Python Import Detected'"

# Detect OS commands
SecRule ARGS "@rx (os\.system|os\.popen|subprocess|exec\()" \
    "id:1002,phase:2,deny,status:403,msg:'OS Command Pattern'"
```

### Application Logging

```python
import logging
from functools import wraps

logger = logging.getLogger(__name__)

def log_template_rendering(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.info(f"Template rendering: {func.__name__}")
        logger.debug(f"Context: {kwargs}")

        try:
            result = func(*args, **kwargs)
            logger.info("Template rendered successfully")
            return result
        except Exception as e:
            logger.error(f"Template error: {e}", exc_info=True)
            raise
    return wrapper

@log_template_rendering
def render_template(template_name, context):
    return template.render(**context)
```

### SIEM Rules

```json
{
  "rule_id": "SSTI_001",
  "title": "Potential SSTI Attack",
  "description": "Detected template syntax in user input",
  "events": [
    {
      "field": "request.body",
      "contains": ["{{", "<%", "{%"]
    }
  ],
  "threshold": 3, // Multiple attempts
  "action": "alert, block"
}
```

## Best Practices Checklist

- [ ] Never concatenate user input into template code
- [ ] Always pass data via context/variables
- [ ] Use pre-compiled templates with fixed names
- [ ] Implement strict input validation (whitelist)
- [ ] Enable template engine sandboxing
- [ ] Escape user input where necessary
- [ ] Keep template engine updated
- [ ] Run template engine with minimal privileges
- [ ] Implement logging and monitoring
- [ ] Regular security testing
- [ ] Code review for template usage
- [ ] Security scanning in CI/CD pipeline

## Testing untuk Verify Security

```python
# Security test suite
import pytest
from unittest.mock import patch

def test_template_injection_blocked():
    """Ensure SSTI is not possible"""
    payload = "{{7*7}}"

    # Template should not execute
    template = env.from_string("Result: {{ value }}")
    output = template.render(value=payload)

    # Should output literal, not 49
    assert "{{7*7}}" in output or output == "Result: {{7*7}}"

def test_object_introspection_blocked():
    """Ensure object introspection is blocked"""
    payload = "{{ ''.__class__ }}"

    with pytest.raises(Exception):  # Should raise error
        template = env.from_string(payload)
        template.render()

def test_file_access_blocked():
    """Ensure file operations are blocked"""
    payload = "{{ open('/etc/passwd').read() }}"

    with pytest.raises(Exception):
        template = env.from_string(payload)
        template.render()
```

## Tài Liệu Liên Quan

- [02-vulnerability-analysis.md](02-vulnerability-analysis.md) - Phân tích lỗ hổng
- [19-sandbox-bypass.md](19-sandbox-bypass.md) - Bypass techniques
