# SQLi-047: MSSQL Double Keyword Bypass (UNION SELECT)

## 🎯 Mục Tiêu

Bypass WAF filter xóa cả `UNION` và `SELECT` bằng kỹ thuật double keyword trên MSSQL.

## 📝 Mô Tả

**Scenario:** Enterprise WAF tìm và **XÓA** (không block) các từ khóa UNION và SELECT.

**URL:** `http://localhost:5047/employee?id=1`

**WAF Behavior:**
- `UNION` → được xóa thành `""`
- `SELECT` → được xóa thành `""`
- Ví dụ: `UNION SELECT` → `" "` (chỉ còn space)

## 🎓 Kiến Thức Cần Biết

### Double Keyword Technique

Khi WAF xóa keyword chỉ 1 lần, ta có thể nested keyword:

```sql
-- Original bị xóa
UNION SELECT → " "

-- Double keyword
UNunionION SEselectLECT → UNION SELECT
-- Sau khi WAF xóa union và select từ giữa
```

### MSSQL Specific

```sql
-- String concat trong MSSQL
SELECT 'a' + 'b'

-- MSSQL Comments
SELECT 1 -- comment
SELECT 1 /* comment */
```

## 🚀 Khởi Chạy Lab

```bash
cd Module-07-Filter-Bypass/SQLi-047
docker-compose up -d
```

Truy cập: `http://localhost:5047`

## 💡 Gợi Ý

1. Quan sát khi submit `UNION SELECT` - xem response
2. WAF xóa hay block keyword?
3. Nếu xóa → double keyword có thể work
4. `UNunionION` sau khi xóa "union" → `UNION`

## 🏁 Flag Format

```
FLAG{...}
```
