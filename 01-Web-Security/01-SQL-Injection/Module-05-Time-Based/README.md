# Module 5: Time-based Blind SQL Injection

> **Mục tiêu**: Khai thác SQLi bằng cách quan sát response time delay
>
> **Lưu ý:** Focus vào advanced scenarios vì basic time-based tương tự Boolean Blind.

## 📋 Danh Sách Labs

### Sub-module 5.1: Core Time-based Techniques

| Lab ID   | DBMS       | Scenario           | Technique                     | Complexity |
| -------- | ---------- | ------------------ | ----------------------------- | ---------- |
| SQLi-029 | MySQL      | Heavy traffic site | BENCHMARK() alternative       | ⭐⭐⭐ Khó |
| SQLi-030 | MSSQL      | Email validation   | WAITFOR DELAY (no stacked)    | ⭐⭐⭐ Khó |
| SQLi-031 | PostgreSQL | Rate limited API   | GENERATE_SERIES heavy query   | ⭐⭐⭐ Khó |
| SQLi-032 | Oracle     | Restricted env     | Heavy query join technique    | ⭐⭐⭐ Khó |

### Sub-module 5.2: Advanced Injection Points

| Lab ID   | DBMS       | Injection Point | Complexity      |
| -------- | ---------- | --------------- | --------------- |
| SQLi-033 | MySQL      | **Cookie**      | ⭐⭐ Trung bình |
| SQLi-034 | PostgreSQL | **User-Agent**  | ⭐⭐⭐ Khó      |

## 🎓 Kiến Thức Cần Biết

### Time-based Functions

| DBMS       | Function                                    |
| ---------- | ------------------------------------------- |
| MySQL      | `SLEEP(seconds)`, `BENCHMARK(count, expr)`  |
| MSSQL      | `WAITFOR DELAY '0:0:5'`                     |
| PostgreSQL | `pg_sleep(seconds)`, `GENERATE_SERIES()`    |
| Oracle     | `DBMS_PIPE.RECEIVE_MESSAGE()`, Heavy joins  |

### Conditional Time Delay

```sql
-- MySQL
IF(condition, SLEEP(5), 0)

-- MSSQL
IF (condition) WAITFOR DELAY '0:0:5'

-- PostgreSQL
SELECT CASE WHEN condition THEN pg_sleep(5) END
```

## 🚀 Cách Chạy Lab

```bash
cd SQLi-029
docker-compose up -d
# Test with timing measurement
time curl "http://localhost:5029/..."
```
