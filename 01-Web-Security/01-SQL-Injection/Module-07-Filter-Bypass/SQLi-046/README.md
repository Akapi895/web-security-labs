# SQLi-046: MySQL SELECT Filter Bypass with Version Comments

## 🎯 Mục Tiêu

Bypass WAF filter chặn từ khóa `SELECT` bằng MySQL version comments `/*!50000SELECT*/`.

## 📝 Mô Tả

**Scenario:** Một hệ thống inventory có WAF filter từ khóa `SELECT` để ngăn chặn data extraction.

**URL:** `http://localhost:5046/inventory?item=laptop`

**WAF Behavior:**
- Request chứa "select" → ❌ "SELECT keyword blocked"
- Request không chứa "select" → ✅ Query thực thi

## 🎓 Kiến Thức Cần Biết

### MySQL Version Comments

MySQL có tính năng đặc biệt: thực thi code trong comments `/*!...*/` nếu version >= số trong comment.

```sql
-- Chỉ thực thi nếu MySQL >= 5.0.0
/*!50000SELECT*/ * FROM users

-- Luôn thực thi (version 0)
/*!00000SELECT*/ * FROM users

-- Mix với UNION
UNION /*!50000SELECT*/ 1,2,3
```

## 🚀 Khởi Chạy Lab

```bash
cd Module-07-Filter-Bypass/SQLi-046
docker-compose up -d
```

Truy cập: `http://localhost:5046`

## 💡 Gợi Ý

1. Xác định filter chặn những gì
2. MySQL version comments là đặc điểm unique của MySQL
3. Thử các format: `/*!SELECT*/`, `/*!50000SELECT*/`

## 🏁 Flag Format

```
FLAG{...}
```
