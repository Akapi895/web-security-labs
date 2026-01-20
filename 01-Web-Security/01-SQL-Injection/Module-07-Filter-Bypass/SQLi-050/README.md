# SQLi-050: MSSQL Double URL Encoding Bypass

## 🎯 Mục Tiêu

Bypass WAF sử dụng double URL encoding khi server decode input 2 lần.

## 📝 Mô Tả

**Scenario:** Server decode URL một lần, sau đó WAF check, sau đó lại decode một lần nữa trước khi query.

**URL:** `http://localhost:5050/search?q=test`

## 🎓 Kiến Thức Cần Biết

### Double URL Encoding

```
' (quote) → %27 (URL encode) → %2527 (double encode)

Flow:
1. Input: %2527
2. First decode: %27 (WAF sees this)
3. WAF passes (không thấy ')
4. Second decode: ' (query nhận được ')
```

### Ví dụ

```
%2527 → %27 → '
%253B → %3B → ;
%252D%252D → %2D%2D → --
```

## 🚀 Khởi Chạy Lab

```bash
cd Module-07-Filter-Bypass/SQLi-050
docker-compose up -d
```

## 💡 Gợi Ý

1. Test payload bình thường → bị block
2. Thử double encode các ký tự đặc biệt
3. `%25` = `%` → `%2527` = `%27` = `'`

## 🏁 Flag Format

```
FLAG{...}
```
