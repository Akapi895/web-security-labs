# Module 1: Detection & Fingerprinting

## 🎯 Mục Tiêu Module

Học cách phát hiện lỗ hổng SQL Injection và xác định loại DBMS mà ứng dụng đang sử dụng.

## 📚 Kiến Thức Yêu Cầu

Trước khi bắt đầu module này, bạn cần nắm:
- Cơ bản về SQL queries
- HTTP requests/responses
- Cách sử dụng Burp Suite hoặc browser developer tools

## 🔬 Labs Trong Module

| Lab ID | Tên Lab | DBMS | Kỹ Thuật | Độ Khó |
|--------|---------|------|----------|--------|
| [SQLi-001](./SQLi-001/) | Quote-based Detection | MySQL | `'`, `"`, `` ` `` testing | ⭐ Dễ |
| [SQLi-002](./SQLi-002/) | Logic-based Detection | PostgreSQL | `OR 1=1`, `AND 1=2` testing | ⭐ Dễ |
| [SQLi-003](./SQLi-003/) | Arithmetic Detection | MSSQL | `1/0`, `1/1` testing | ⭐ Dễ |
| [SQLi-004](./SQLi-004/) | Comment Detection | Oracle | `--`, `#`, `/**/` testing | ⭐ Dễ |
| [SQLi-005](./SQLi-005/) | Error-based Fingerprinting | MySQL | Error message analysis | ⭐⭐ Trung bình |
| [SQLi-006](./SQLi-006/) | Version Query Fingerprinting | PostgreSQL | `@@version`, `version()` | ⭐⭐ Trung bình |
| [SQLi-007](./SQLi-007/) | Time-based Fingerprinting | MSSQL | `SLEEP`, `WAITFOR DELAY` | ⭐⭐ Trung bình |
| [SQLi-008](./SQLi-008/) | Concatenation Fingerprinting | Oracle | `||`, `+`, `CONCAT` | ⭐⭐ Trung bình |

## 📖 Lý Thuyết Cốt Lõi

### 1. Phát Hiện SQL Injection

#### Quote-based Testing
```
' → Triggers SQL syntax error if vulnerable
" → Alternative quote testing
` → MySQL backtick testing
') → Closing parenthesis + quote
```

#### Logic-based Testing
```sql
' OR '1'='1    -- Always true
' OR '1'='2    -- Always false
' AND 1=1--    -- True condition
' AND 1=2--    -- False condition
```

#### Arithmetic Testing
```sql
1/1    -- Valid (returns 1)
1/0    -- Error or different response
1*1    -- Valid
1-0    -- Valid
```

### 2. DBMS Fingerprinting

#### Error Message Patterns
| DBMS | Error Pattern |
|------|---------------|
| MySQL | `You have an error in your SQL syntax` |
| MSSQL | `Unclosed quotation mark` |
| Oracle | `ORA-XXXXX` |
| PostgreSQL | `ERROR: syntax error at or near` |

#### Version Queries
| DBMS | Query |
|------|-------|
| MySQL | `SELECT @@version` |
| MSSQL | `SELECT @@version` |
| Oracle | `SELECT banner FROM v$version WHERE ROWNUM=1` |
| PostgreSQL | `SELECT version()` |

#### String Concatenation
| DBMS | Syntax |
|------|--------|
| MySQL | `CONCAT('a','b')` or `'a' 'b'` |
| MSSQL | `'a'+'b'` |
| Oracle | `'a'||'b'` |
| PostgreSQL | `'a'||'b'` |

## 🚀 Cách Chạy Labs

```bash
# Vào thư mục lab cụ thể
cd SQLi-XXX

# Khởi động lab
docker-compose up -d

# Truy cập theo hướng dẫn trong README.md của từng lab

# Dọn dẹp sau khi hoàn thành
docker-compose down -v
```

## ✅ Checklist Hoàn Thành

- [ ] SQLi-001: Phát hiện SQLi bằng quote test
- [ ] SQLi-002: Phát hiện SQLi bằng logic test
- [ ] SQLi-003: Phát hiện SQLi bằng arithmetic test
- [ ] SQLi-004: Phát hiện SQLi bằng comment test
- [ ] SQLi-005: Xác định MySQL qua error messages
- [ ] SQLi-006: Xác định PostgreSQL qua version queries
- [ ] SQLi-007: Xác định MSSQL qua time-based detection
- [ ] SQLi-008: Xác định Oracle qua concatenation

## 📚 Tài Liệu Tham Khảo

- [Knowledge Base - Detection](../../../_knowledge_base/Web/SQLi/01-detection.md)
- [Knowledge Base - Overview](../../../_knowledge_base/Web/SQLi/00-overview.md)
