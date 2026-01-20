# 🛡️ Module 7: Filter Bypass Techniques

> **Mục tiêu**: Học cách bypass WAF và input validation để thực hiện SQL Injection

## 📋 Tổng Quan

Module này tập trung vào các kỹ thuật bypass filter phổ biến, bao gồm:
- Bypass space/whitespace filters
- Bypass keyword filters (UNION, SELECT, AND/OR)
- Bypass comment filters
- Bypass quote filters
- Encoding techniques (Hex, Double URL)
- Equals character bypass

## 🎯 Labs

| Lab ID | DBMS | Filter Type | Bypass Technique | Complexity |
|--------|------|-------------|------------------|------------|
| [SQLi-043](./SQLi-043/) | MySQL | Space `' '` | `/**/`, `%09`, `%0a` | ⭐⭐ Trung bình |
| [SQLi-044](./SQLi-044/) | PostgreSQL | Whitespace | Parentheses `(SELECT(x))` | ⭐⭐ Trung bình |
| [SQLi-045](./SQLi-045/) | MySQL | UNION keyword | `Un/**/IoN` | ⭐⭐ Trung bình |
| [SQLi-046](./SQLi-046/) | MySQL | SELECT keyword | `/*!50000SELECT*/` | ⭐⭐⭐ Khó |
| [SQLi-047](./SQLi-047/) | MSSQL | UNION SELECT | `UNunionION SEselectLECT` | ⭐⭐⭐ Khó |
| [SQLi-048](./SQLi-048/) | MySQL | `--` comment | `#`, `/**/` | ⭐⭐ Trung bình |
| [SQLi-049](./SQLi-049/) | MySQL | Quote `'` `"` | Hex `0x61646D696E` | ⭐⭐ Trung bình |
| [SQLi-050](./SQLi-050/) | MSSQL | URL encoding | Double `%2527` | ⭐⭐⭐ Khó |
| [SQLi-051](./SQLi-051/) | MySQL | AND/OR | `&&`, `\|\|` | ⭐⭐ Trung bình |
| [SQLi-052](./SQLi-052/) | PostgreSQL | Equals `=` | LIKE, BETWEEN, IN | ⭐⭐ Trung bình |

## 📊 DBMS Distribution

- **MySQL**: 6 labs (SQLi-043, 045, 046, 048, 049, 051)
- **PostgreSQL**: 2 labs (SQLi-044, 052)
- **MSSQL**: 2 labs (SQLi-047, 050)

## 🚀 Quick Start

```bash
# Chạy một lab cụ thể
cd SQLi-043
docker-compose up -d

# Truy cập
curl http://localhost:5043

# Dừng lab
docker-compose down
```

## 📖 Port Mapping

| Lab | Port |
|-----|------|
| SQLi-043 | 5043 |
| SQLi-044 | 5044 |
| SQLi-045 | 5045 |
| SQLi-046 | 5046 |
| SQLi-047 | 5047 |
| SQLi-048 | 5048 |
| SQLi-049 | 5049 |
| SQLi-050 | 5050 |
| SQLi-051 | 5051 |
| SQLi-052 | 5052 |

## 🎓 Learning Path

1. **Bắt đầu**: SQLi-043 (Space bypass) - Cơ bản nhất
2. **Tiếp theo**: SQLi-044, 045, 048, 049, 051 - Trung bình
3. **Nâng cao**: SQLi-046, 047, 050 - Kỹ thuật phức tạp

## 📚 Tham Khảo

- [OWASP - SQL Injection Bypassing WAF](https://owasp.org/www-community/attacks/SQL_Injection_Bypassing_WAF)
- [PortSwigger - Bypassing Common Filters](https://portswigger.net/web-security/sql-injection/bypassing-common-defenses)
- [PayloadsAllTheThings - SQLi Filter Bypass](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/SQL%20Injection#filter-bypass)

---

_Module 7 - Filter Bypass Techniques | 10 Labs | Created: January 2026_
