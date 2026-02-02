# Module 01: In-band Command Injection

> **Mức độ**: Beginner  
> **Prerequisite**: Kiến thức cơ bản về Linux shell và HTTP

## 📋 Tổng Quan

Module này tập trung vào **In-band Command Injection** - trường hợp output của injected command hiển thị trực tiếp trong HTTP response. Đây là dạng Command Injection dễ exploit nhất vì feedback loop ngắn.

## 🎯 Mục Tiêu Học Tập

Sau khi hoàn thành module này, bạn sẽ:

1. **Nhận diện** các injection points trong web applications
2. **Hiểu** cách shell interpret các metacharacters
3. **Phân biệt** các loại command separators và khi nào dùng loại nào
4. **Vượt qua** các cơ chế filtering không đầy đủ
5. **Áp dụng** workflow khai thác chuẩn: RECON → HYPOTHESIS → EXPLOITATION → VALIDATION

## 📚 Danh Sách Labs

| Lab | Tên | Trọng Tâm Kỹ Thuật | Port |
|-----|-----|-------------------|------|
| [CMDi-001](./CMDi-001/) | Basic Semicolon Separator | Semicolon (`;`) injection trong unquoted context | 5101 |
| [CMDi-002](./CMDi-002/) | Pipe Operator Injection | Pipe (`\|`) bypass khi `;` bị filter | 5102 |
| [CMDi-003](./CMDi-003/) | Command Substitution | `$()` và backticks khi separators bị filter | 5103 |

## 🧠 Điểm Mấu Chốt

### In-band vs Blind Injection

| Aspect | In-band | Blind |
|--------|---------|-------|
| Output visibility | ✅ Thấy trong response | ❌ Không thấy |
| Detection | Dễ - quan sát trực tiếp | Khó - cần timing/OOB |
| Exploitation | Nhanh - trial-and-error | Chậm - cần automation |

### Command Separators Reference

| Operator | Function | Example |
|----------|----------|---------|
| `;` | Sequential execution | `cmd1; cmd2` |
| `\|` | Pipe output | `cmd1 \| cmd2` |
| `\|\|` | OR (run if fails) | `cmd1 \|\| cmd2` |
| `&&` | AND (run if succeeds) | `cmd1 && cmd2` |
| `&` | Background | `cmd1 & cmd2` |
| `$()` | Command substitution | `$(cmd)` |
| `` ` `` | Command substitution | `` `cmd` `` |

## 🔄 Workflow Khai Thác Chuẩn

```
┌─────────────────────────────────────────────────────────────┐
│                   EXPLOITATION WORKFLOW                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. RECON       ──► Quan sát behavior bình thường            │
│       │              Xác định input parameters               │
│       ▼                                                      │
│  2. HYPOTHESIS  ──► Đoán injection context (quoted/unquoted) │
│       │              Xác định OS (Linux/Windows)             │
│       ▼                                                      │
│  3. EXPLOITATION──► Test separators: ; | || && & $() ``      │
│       │              Confirm với id, whoami                  │
│       ▼                                                      │
│  4. VALIDATION  ──► Recon system (ls, cat, find)             │
│                     Thu thập flag/sensitive data             │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## 📖 Knowledge Base References

- [Command Injection Overview](../../../_knowledge_base/Web/Command%20Injection/00-overview.md)
- [Detection Techniques](../../../_knowledge_base/Web/Command%20Injection/01-detection.md)
- [Exploitation Techniques](../../../_knowledge_base/Web/Command%20Injection/02-exploitation.md)

## 🚀 Quick Start

```bash
# Chạy tất cả labs trong module
docker-compose -f CMDi-001/docker-compose.yml up -d
docker-compose -f CMDi-002/docker-compose.yml up -d
docker-compose -f CMDi-003/docker-compose.yml up -d

# Truy cập:
# Lab 1: http://localhost:5101
# Lab 2: http://localhost:5102
# Lab 3: http://localhost:5103

# Dừng tất cả
docker-compose -f CMDi-001/docker-compose.yml down
docker-compose -f CMDi-002/docker-compose.yml down
docker-compose -f CMDi-003/docker-compose.yml down
```

## ✅ Khi Nào Chuyển Sang Module Tiếp Theo?

Bạn đã sẵn sàng cho Module 02 (Injection Context) khi:

- [ ] Hoàn thành cả 3 labs
- [ ] Hiểu được sự khác biệt giữa `;`, `|`, và `$()`
- [ ] Có thể giải thích tại sao mỗi payload hoạt động
- [ ] Biết cách xác định filter đang chặn gì
- [ ] Thuộc workflow RECON → HYPOTHESIS → EXPLOITATION → VALIDATION
