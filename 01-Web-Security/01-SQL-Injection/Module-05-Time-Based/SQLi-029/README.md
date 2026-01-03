# SQLi-029: MySQL Time-based Blind - SLEEP/BENCHMARK

## 🎯 Mục Tiêu

Khai thác Time-based Blind SQLi trên MySQL dùng `SLEEP()` hoặc `BENCHMARK()`.

## 📝 Mô Tả

**URL:** `http://localhost:5029/product?id=1`

Response giống nhau cho mọi input (không có Boolean difference), phải dùng time delay để xác định TRUE/FALSE.

## 🎓 Techniques

```sql
-- SLEEP (most common)
IF(condition, SLEEP(3), 0)

-- BENCHMARK (alternative khi SLEEP bị block)
IF(condition, BENCHMARK(10000000, SHA1('test')), 0)
```

## 🚀 Run

```bash
docker-compose up -d
time curl "http://localhost:5029/product?id=1"
```

## 🏁 Flag: `FLAG{...}`
