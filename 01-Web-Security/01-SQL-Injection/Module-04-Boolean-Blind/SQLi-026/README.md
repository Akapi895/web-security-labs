# SQLi-026: PostgreSQL Boolean Blind via JSON Body

## 🎯 Mục Tiêu

Khai thác Boolean Blind SQLi qua **JSON body** trong REST API.

## 📝 Mô Tả

REST API endpoint nhận JSON body với `id` field:

```bash
POST /api/product
Content-Type: application/json
{"id": "1"}
```

- ✅ Product found → `{"status": "found", "name": "..."}`
- ❌ Not found → `{"status": "not_found"}`

## 🚀 Hướng Dẫn

```bash
docker-compose up -d
curl -X POST http://localhost:5026/api/product -H "Content-Type: application/json" -d '{"id":"1"}'
```

## 🏁 Flag: `FLAG{...}`
