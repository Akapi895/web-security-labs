# SQLi-027: MySQL Boolean Blind via ORDER BY

## 🎯 Mục Tiêu

Khai thác Boolean Blind SQLi qua **ORDER BY clause** trong product sorting.

## 📝 Mô Tả

Product listing cho phép sort theo các columns khác nhau:

**URL:** `http://localhost:5027/products?sort=price`

Injection point: `sort` parameter được đưa vào ORDER BY clause.

## 🎓 Kiến Thức

### ORDER BY Injection

Không thể dùng `'` vì ORDER BY không cần quotes. Thay vào đó dùng conditional:

```sql
-- Conditional ordering
ORDER BY (CASE WHEN (condition) THEN column1 ELSE column2 END)

-- Ví dụ
ORDER BY (CASE WHEN (SELECT 1)=1 THEN price ELSE name END)
```

## 🚀 Hướng Dẫn

```bash
docker-compose up -d
curl "http://localhost:5027/products?sort=price"
```

## 🏁 Flag: `FLAG{...}`
