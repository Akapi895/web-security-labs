# SQLi-033: MySQL Time-based via Cookie

## 🎯 Mục Tiêu

Khai thác Time-based Blind SQLi trên MySQL thông qua HTTP Cookie.

## 📝 Mô Tả

**URL:** `http://localhost:5033/`

**Injection Point:** Cookie `session_id`

Ứng dụng kiểm tra session ID từ cookie và query database. Response luôn giống nhau bất kể query thành công hay thất bại.

## 🎓 Technique

Injection trong Cookie header:

```bash
curl -b "cookie_name=value' AND payload--" http://target/
```

## 🚀 Run

```bash
docker-compose up -d
curl -b "session_id=sess_abc123" http://localhost:5033/
```

## 🏁 Flag: `FLAG{...}`
