# Command Injection Defense & Mitigation

## Primary Defense: Avoid OS Commands

**Nguyên tắc #1**: Không gọi OS commands từ application code nếu có thể tránh được.

### Use Built-in Functions Instead

| Instead of | Use |
|------------|-----|
| `system("cp src dst")` | PHP: `copy("src", "dst")` |
| `system("mkdir dir")` | PHP: `mkdir("dir")` |
| `exec("cat file")` | PHP: `file_get_contents("file")` |
| `os.system("ping " + ip)` | Python: Use socket library |
| `Runtime.exec("ls")` | Java: `Files.list(path)` |

### Example: Safe File Operations

**Vulnerable (PHP):**

```php
$file = $_GET['file'];
system("cat /docs/" . $file);
```

**Safe Alternative:**

```php
$file = $_GET['file'];
$path = "/docs/" . basename($file);  // Strip path traversal
if (file_exists($path)) {
    echo file_get_contents($path);
}
```

## Input Validation

### Allowlist Approach (Recommended)

Chỉ accept input matching expected pattern:

```php
// PHP: Only allow alphanumeric
if (!preg_match('/^[a-zA-Z0-9]+$/', $input)) {
    die("Invalid input");
}
```

```python
# Python: Only allow IP addresses
import re
if not re.match(r'^(\d{1,3}\.){3}\d{1,3}$', ip):
    raise ValueError("Invalid IP")
```

```java
// Java: Only allow specific values
String[] allowed = {"value1", "value2", "value3"};
if (!Arrays.asList(allowed).contains(input)) {
    throw new IllegalArgumentException("Invalid input");
}
```

### Numeric Validation

```php
// PHP
if (!is_numeric($input)) {
    die("Must be numeric");
}

// Or cast to int
$id = intval($_GET['id']);
```

### Blocklist Approach (Less Secure)

Nếu phải dùng blocklist, cần filter nhiều characters:

**Linux blocklist:**

```
{ } ( ) > < & * ' | = ? ; [ ] $ - # ~ ! . " % / \ : + , `
```

**Windows blocklist:**

```
( ) < > & * ' | = ? ; [ ] ^ ~ ! . " % @ / \ : + , `
```

**Lưu ý**: Blocklist thường bị bypass. Luôn prefer allowlist.

## Dangerous APIs by Language

### Java

```java
// DANGEROUS - avoid or sanitize carefully
Runtime.exec(command);
ProcessBuilder.command(command);

// Example vulnerable code
String cmd = "ping " + userInput;
Runtime.getRuntime().exec(cmd);
```

**Safe Alternative:**

```java
// Use ProcessBuilder with arguments as array
ProcessBuilder pb = new ProcessBuilder("ping", "-c", "4", sanitizedIP);
pb.start();
```

### C/C++

```c
// DANGEROUS
system(command);
exec(command);
popen(command, mode);
ShellExecute(...);

// Example vulnerable
char cmd[256];
sprintf(cmd, "ping %s", userInput);
system(cmd);
```

**Safe Alternative:**

```c
// Use execve with argument array
char *args[] = {"ping", "-c", "4", sanitized_ip, NULL};
execve("/bin/ping", args, NULL);
```

### Python

```python
# DANGEROUS
os.system(command)
os.popen(command)
subprocess.call(command, shell=True)
subprocess.Popen(command, shell=True)
eval(string)
exec(string)

# Example vulnerable
os.system("ping " + user_input)
```

**Safe Alternative:**

```python
# Use subprocess without shell=True
import subprocess
subprocess.run(["ping", "-c", "4", sanitized_ip], shell=False)
```

### PHP

```php
// DANGEROUS
system($command);
shell_exec($command);
exec($command);
passthru($command);
proc_open($command, ...);
eval($code);
popen($command, $mode);
preg_replace('/e', ...);  // deprecated

// Example vulnerable
system("ping " . $_GET['ip']);
```

**Safe Alternative:**

```php
// Use escapeshellarg() and escapeshellcmd()
$ip = escapeshellarg($_GET['ip']);
system("ping -c 4 " . $ip);

// Better: avoid shell entirely
// Use built-in socket functions instead
```

### Node.js

```javascript
// DANGEROUS
const { exec } = require('child_process');
exec(command);  // Spawns shell

// Example vulnerable
exec(`ping ${userInput}`);
```

**Safe Alternative:**

```javascript
// Use execFile() - no shell spawned
const { execFile } = require('child_process');
execFile('ping', ['-c', '4', sanitizedIP], (err, stdout) => {
    console.log(stdout);
});

// Or spawn() without shell option
const { spawn } = require('child_process');
spawn('ping', ['-c', '4', sanitizedIP]);
```

## Escaping Functions

### PHP

```php
// escapeshellarg() - wrap in quotes and escape
$safe = escapeshellarg($input);
// 'user input' -> 'user'\''input' (with escaping)

// escapeshellcmd() - escape metacharacters
$safe = escapeshellcmd($input);
// Escapes: #&;`|*?~<>^()[]{}$\

// Example
$ip = escapeshellarg($_GET['ip']);
system("ping -c 4 " . $ip);
```

### Python

```python
# shlex.quote() - shell escaping
import shlex
safe = shlex.quote(user_input)

# pipes.quote() - deprecated, use shlex
```

### Important Warning

> ⚠️ **Never rely solely on escaping**. Escaping is error-prone and can be bypassed. Always combine with validation and prefer avoiding shell commands.

## Permission Hardening

### Principle of Least Privilege

1. **Web server user**: Run as non-root user
2. **Limited permissions**: Only necessary read/write access
3. **Chroot/Container**: Isolate web application
4. **Disable dangerous functions**: In PHP via `disable_functions`

### PHP Configuration

```ini
; php.ini
disable_functions = exec,passthru,shell_exec,system,proc_open,popen,curl_exec,curl_multi_exec,parse_ini_file,show_source
```

### File System Permissions

```bash
# Web files read-only where possible
chmod 644 /var/www/html/*.php
chown www-data:www-data /var/www/html/

# Limit write access
chmod 755 /var/www/html/uploads/  # Only if needed
```

### Network Restrictions

- Limit outbound connections từ web server
- Block unnecessary ports
- Use firewall rules

## Automation Tools

### Detection Tools

| Tool | Description | URL |
|------|-------------|-----|
| **Commix** | Automated command injection exploitation | https://github.com/commixproject/commix |
| **Interactsh** | OOB interaction server | https://github.com/projectdiscovery/interactsh |

### Obfuscation Tools (For Research)

| Tool | Description |
|------|-------------|
| **DOSfuscation** | Windows command obfuscation | 
| **Bashfuscator** | Bash command obfuscation |

### Using Commix

```bash
# Basic scan
commix -u "http://target.com/page.php?ip=INJECT_HERE"

# POST data
commix -u "http://target.com/page.php" --data="ip=INJECT_HERE"

# Specify technique
commix -u "http://target.com/page.php?ip=INJECT_HERE" --technique=T
# T=time-based, B=file-based, E=results-based
```

## Secure Coding Checklist

- [ ] Avoid OS commands where possible - use built-in functions
- [ ] Validate input against strict allowlist
- [ ] Use parameterized functions (argument arrays, not shell strings)
- [ ] Never concatenate user input into command strings
- [ ] If must use shell, apply multiple layers:
  - [ ] Allowlist validation
  - [ ] Type checking
  - [ ] escapeshellarg() / shlex.quote()
- [ ] Run web server with minimal privileges
- [ ] Disable dangerous functions in production
- [ ] Log and monitor command execution
- [ ] Regularly audit code for vulnerable patterns

## Defense Summary

```
┌──────────────────────────────────────────────────────────────────┐
│                    DEFENSE PRIORITIES                            │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. AVOID         ──► Don't use OS commands                      │
│     (Best)             Use built-in APIs instead                 │
│                                                                  │
│  2. PARAMETERIZE  ──► Use argument arrays, not strings           │
│     (Good)             execFile(['cmd','arg1','arg2'])           │
│                                                                  │
│  3. VALIDATE      ──► Strict allowlist validation                │
│     (Required)         Only accept expected patterns             │
│                                                                  │
│  4. ESCAPE        ──► escapeshellarg(), shlex.quote()            │
│     (Last resort)      Combined with validation                  │
│                                                                  │
│  5. HARDEN        ──► Least privilege, disable functions         │
│     (Always)           Defense in depth                          │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```
