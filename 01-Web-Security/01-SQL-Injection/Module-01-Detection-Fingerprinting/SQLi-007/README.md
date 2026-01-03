# SQLi-007: Time-based DBMS Fingerprinting

## 🎯 Mục Tiêu

Học cách xác định loại DBMS bằng **time-based delay functions** - mỗi DBMS có function delay riêng.

## 📝 Mô Tả Kịch Bản

Một **REST API endpoint** có SQLi nhưng không hiển thị error messages. Bạn cần sử dụng time-based techniques để fingerprint DBMS.

**URL Target:** `http://localhost:5007/api/user?id=1`

## 🎓 Kiến Thức Cần Học

### Time Delay Functions

| DBMS | Function |
|------|----------|
| MySQL | `SLEEP(5)` |
| MSSQL | `WAITFOR DELAY '0:0:5'` |
| PostgreSQL | `pg_sleep(5)` |
| Oracle | `DBMS_PIPE.RECEIVE_MESSAGE('a',5)` |

## 🚀 Hướng Dẫn Chạy Lab

```bash
docker-compose up -d
# Truy cập: http://localhost:5007
docker-compose down -v
```

## 💡 Hints

<details>
<summary>Hint 1: Test time delays</summary>

```sql
1; WAITFOR DELAY '0:0:5'--  (MSSQL)
1 AND SLEEP(5)--           (MySQL)
1; SELECT pg_sleep(5)--    (PostgreSQL)
```
Observe response time!

</details>

<details>
<summary>Hint 2: MSSQL indicators</summary>

- `WAITFOR DELAY` works
- Supports stacked queries (`;`)
- Uses TOP N instead of LIMIT

</details>

## 🏁 Flag

Identify MSSQL via time-based detection và extract flag.

**Flag Format:** `FLAG{...}`

## 📋 Checklist

- [ ] Test SLEEP(5) - should fail
- [ ] Test WAITFOR DELAY - should cause 5s delay
- [ ] Confirm MSSQL
- [ ] Extract flag

## 🔗 Tài Liệu

- [Time-based Blind SQLi](../../../../_knowledge_base/Web/SQLi/05-time-based-blind.md)
- [MSSQL Cheatsheet](../../../../_knowledge_base/Web/SQLi/09-dbms-mssql.md)
