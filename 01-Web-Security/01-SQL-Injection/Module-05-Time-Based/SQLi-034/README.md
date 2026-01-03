# SQLi-034: PostgreSQL Time-based via User-Agent

## 🎯 Mục Tiêu

Khai thác Time-based Blind SQLi trên PostgreSQL thông qua HTTP User-Agent header.

## 📝 Mô Tả

**URL:** `http://localhost:5034/`

**Injection Point:** HTTP header `User-Agent`

Ứng dụng log visitor information bằng INSERT statement, lưu User-Agent vào database. Response luôn giống nhau.

## 🎓 Technique

Injection trong INSERT context (cần đóng quote và parenthesis):

```sql
-- Original: INSERT INTO visitors (user_agent, ip) VALUES ('UA', '...')
-- Inject: '); payload--
```

```bash
curl -A "payload_here" http://target/
```

## 🚀 Run

```bash
docker-compose up -d
curl -A "Mozilla/5.0" http://localhost:5034/
```

## 🏁 Flag: `FLAG{...}`
