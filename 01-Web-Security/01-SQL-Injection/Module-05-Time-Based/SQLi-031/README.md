# SQLi-031: PostgreSQL Time-based - pg_sleep

**URL:** `http://localhost:5031/api/check?key=key_abc123`

**Technique:** `pg_sleep(seconds)`

```sql
'; SELECT CASE WHEN (condition) THEN pg_sleep(2) END--
```

## 🏁 Flag: `FLAG{...}`
