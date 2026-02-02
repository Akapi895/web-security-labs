# Command Injection Overview

## Definition

Command Injection (còn gọi là Shell Injection hoặc OS Command Injection) là lỗ hổng bảo mật cho phép kẻ tấn công thực thi các lệnh hệ điều hành tùy ý trên server đang chạy ứng dụng. Lỗ hổng xảy ra khi ứng dụng truyền trực tiếp dữ liệu từ người dùng vào system shell mà không qua validate hoặc sanitize đúng cách.

**Bản chất kỹ thuật**: Ứng dụng sử dụng các API như `system()`, `exec()`, `popen()` để gọi lệnh OS, và dữ liệu người dùng được nối trực tiếp vào command string.

## So sánh với các lỗ hổng tương tự

| Lỗ hổng | Injection Target | Execution Context | Ví dụ |
|---------|------------------|-------------------|-------|
| **Command Injection** | OS Shell | `/bin/sh`, `cmd.exe` | `system("ping " . $ip)` |
| SQL Injection | SQL Query | Database Engine | `query("SELECT * WHERE id=" . $id)` |
| Code Injection | Application Code | Interpreter (PHP, Python, etc.) | `eval($_GET['code'])` |

**Điểm khác biệt quan trọng**:
- Command Injection tác động trực tiếp đến hệ điều hành
- SQL Injection giới hạn trong database context
- Code Injection thực thi code trong application interpreter

## Impact Assessment

| Impact | Description | Severity |
|--------|-------------|----------|
| **Confidentiality** | Đọc file hệ thống, credentials, source code | Critical |
| **Integrity** | Sửa đổi, xóa file, cài backdoor | Critical |
| **Availability** | DoS, shutdown services, resource exhaustion | High |
| **Lateral Movement** | Pivot sang hệ thống khác trong mạng | Critical |
| **Full Compromise** | Toàn quyền kiểm soát server | Critical |

## Classification by Injection Context

| Context | Mô tả | Payload Example |
|---------|-------|-----------------|
| **Unquoted** | Input nằm ngoài quotes | `; whoami` |
| **Single Quoted** | Input trong `'...'` | `'; whoami #` |
| **Double Quoted** | Input trong `"..."` | `"; whoami #` |
| **Inside Command** | Input là argument của command | `` `whoami` `` hoặc `$(whoami)` |

## Classification by Output Visibility

| Type | Description | Detection Method |
|------|-------------|------------------|
| **In-band** | Output hiển thị trong response | Trực tiếp quan sát kết quả |
| **Blind** | Không có output trong response | Time delay, OOB channels |
| **Out-of-Band (OOB)** | Exfiltrate qua external channel | DNS lookup, HTTP callback |

## Shell Metacharacters Quick Reference

### Command Separators (Cross-platform)

| Character | Function | Windows | Linux |
|-----------|----------|---------|-------|
| `\|` | Pipe output to next command | ✓ | ✓ |
| `\|\|` | Execute if previous fails | ✓ | ✓ |
| `&&` | Execute if previous succeeds | ✓ | ✓ |
| `&` | Execute in background/parallel | ✓ | ✓ |

### Linux-only Operators

| Character | Function | Example |
|-----------|----------|---------|
| `;` | Sequential execution | `cmd1; cmd2` |
| Newline (`\n`, `%0a`) | Command separator | `cmd1%0acmd2` |
| `` ` `` (backticks) | Command substitution | `` `whoami` `` |
| `$()` | Command substitution | `$(whoami)` |
| `<()`, `>()` | Process substitution | `cat <(whoami)` |

### Redirection Operators

| Operator | Function | Example |
|----------|----------|---------|
| `>` | Write output to file | `whoami > /tmp/out.txt` |
| `>>` | Append output to file | `id >> /tmp/out.txt` |
| `<` | Read input from file | `cmd < input.txt` |

## Attack Workflow

```
┌───────────────────────────────────────────────────────────────────────┐
│                    COMMAND INJECTION WORKFLOW                         │
├───────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  1. IDENTIFY     ──► Tìm injection points (params, headers, etc.)     │
│        │                                                              │
│        ▼                                                              │
│  2. DETECT       ──► Confirm vulnerability với basic payloads         │
│        │              ('; sleep 5 #, | id, etc.)                      │
│        ▼                                                              │
│  3. DETERMINE    ──► Xác định OS (Linux/Windows) và context           │
│        │              (quoted/unquoted)                               │
│        ▼                                                              │
│  4. BYPASS       ──► Vượt qua filters nếu có (encoding, obfuscation)  │
│        │                                                              │
│        ▼                                                              │
│  5. EXPLOIT      ──► Thực thi commands (recon, file read, etc.)       │
│        │                                                              │
│        ▼                                                              │
│  6. EXFILTRATE   ──► Trích xuất dữ liệu (DNS, HTTP, file write)       │
│        │                                                              │
│        ▼                                                              │
│  7. ESCALATE     ──► Privilege escalation, persistence, pivot         │
│                                                                       │
└───────────────────────────────────────────────────────────────────────┘
```

## Useful Reconnaissance Commands

| Purpose | Linux | Windows |
|---------|-------|---------|
| Current user | `whoami` | `whoami` |
| OS version | `uname -a` | `ver` |
| Network config | `ifconfig` | `ipconfig /all` |
| Network connections | `netstat -an` | `netstat -an` |
| Running processes | `ps -ef` | `tasklist` |
| Environment variables | `env` | `set` |
| Current directory | `pwd` | `cd` |
| List files | `ls -la` | `dir` |

## Related Files

- [Detection](01-detection.md)
- [Exploitation](02-exploitation.md)
- [Blind Injection](03-blind-injection.md)
- [Filter Bypass](04-filter-bypass.md)
- [OS Specific](05-os-specific.md)
- [Data Exfiltration](06-exfiltration.md)
- [Payloads Cheatsheet](07-payloads-cheatsheet.md)
- [Defense & Mitigation](08-defense-mitigation.md)
