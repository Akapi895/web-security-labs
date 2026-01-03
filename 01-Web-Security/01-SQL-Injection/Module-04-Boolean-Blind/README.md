# Module 4: Boolean-based Blind SQL Injection

> **Mục tiêu**: Khai thác SQLi khi không có output trực tiếp, chỉ có true/false response
>
> **Lưu ý:** Module này tập trung vào **diverse injection points** với các kỹ thuật Boolean Blind nâng cao.

## 📋 Danh Sách Labs

### Sub-module 4.1: Core Boolean Techniques

| Lab ID   | DBMS       | Scenario            | Learning Objective                        | Complexity      |
| -------- | ---------- | ------------------- | ----------------------------------------- | --------------- |
| SQLi-023 | PostgreSQL | Username validation | SUBSTRING character-by-character extract  | ⭐⭐ Trung bình |
| SQLi-024 | Oracle     | Session validation  | SUBSTR() và ROWNUM pagination             | ⭐⭐ Trung bình |

### Sub-module 4.2: Advanced Injection Points

| Lab ID   | DBMS       | Injection Point   | Learning Objective               | Complexity      |
| -------- | ---------- | ----------------- | -------------------------------- | --------------- |
| SQLi-025 | MySQL      | **Cookie**        | Blind SQLi qua Cookie header     | ⭐⭐ Trung bình |
| SQLi-026 | PostgreSQL | **JSON body**     | Blind SQLi trong JSON payload    | ⭐⭐ Trung bình |
| SQLi-027 | MySQL      | **ORDER BY**      | Blind SQLi trong ORDER BY clause | ⭐⭐⭐ Khó      |
| SQLi-028 | MSSQL      | **Column name**   | Blind SQLi trong dynamic column  | ⭐⭐⭐ Khó      |

## 🎓 Kiến Thức Cần Biết

### Boolean Blind Cơ Bản

Khi ứng dụng không hiển thị output trực tiếp nhưng phản hồi khác nhau cho TRUE/FALSE:

```sql
-- Kiểm tra điều kiện TRUE
' AND 1=1-- → Response A (thành công)

-- Kiểm tra điều kiện FALSE  
' AND 1=2-- → Response B (thất bại)
```

### Character Extraction

Trích xuất data từng ký tự:

| DBMS       | Function                                        |
| ---------- | ----------------------------------------------- |
| MySQL      | `SUBSTRING(str, pos, len)` hoặc `MID()`         |
| PostgreSQL | `SUBSTRING(str FROM pos FOR len)`               |
| Oracle     | `SUBSTR(str, pos, len)`                         |
| MSSQL      | `SUBSTRING(str, pos, len)`                      |

```sql
-- Ví dụ: Kiểm tra ký tự đầu tiên của username = 'a'
' AND SUBSTRING(username,1,1)='a'--
```

### Binary Search Optimization

Thay vì brute-force 26+ ký tự, dùng binary search với ASCII:

```sql
-- Ký tự đầu > 'm' (ASCII 109)?
' AND ASCII(SUBSTRING(username,1,1))>109--

-- Sau đó tiếp tục chia đôi khoảng ASCII
```

## 🚀 Cách Chạy Lab

```bash
cd SQLi-023
docker-compose up -d
# Access the lab URL shown in each README
docker-compose down
```

## 📚 Tài Liệu Tham Khảo

- [PortSwigger - Blind SQL Injection](https://portswigger.net/web-security/sql-injection/blind)
- [OWASP - Blind SQL Injection](https://owasp.org/www-community/attacks/Blind_SQL_Injection)
