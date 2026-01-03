# SQLi-028: MSSQL Boolean Blind via Dynamic Column

## 🎯 Mục Tiêu

Khai thác Boolean Blind SQLi qua **dynamic column name** parameter.

## 📝 Mô Tả

Data export cho phép chọn column để hiển thị:

**URL:** `http://localhost:5028/export?column=report_name`

Injection: `column` parameter được đưa vào SELECT clause.

## 🎓 Kiến Thức

### Dynamic Column Injection

```sql
-- Conditional column selection
CASE WHEN (condition) THEN column1 ELSE column2 END

-- MSSQL-specific
IIF((SELECT 1)=1, column1, column2)
```

## 🚀 Hướng Dẫn

```bash
docker-compose up -d
# Đợi 1-2 phút cho MSSQL khởi động
curl "http://localhost:5028/export?column=report_name"
```

## 🏁 Flag: `FLAG{...}`
