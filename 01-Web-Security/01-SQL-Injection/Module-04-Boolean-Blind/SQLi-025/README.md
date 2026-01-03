# SQLi-025: MySQL Boolean Blind via Cookie

## 🎯 Mục Tiêu

Khai thác Boolean Blind SQLi qua **Cookie header** (`tracking_id`).

## 📝 Mô Tả

Ứng dụng Analytics tracking lưu tracking_id trong cookie:

**URL:** `http://localhost:5025/`

### Tính năng:

1. **Login Page:** `http://localhost:5025/login`
   - Đăng nhập với credentials từ database
   - Tự động hiển thị tracking cookie sau khi login thành công
   - Không cần mở Web Developer Tools để lấy cookie

2. **Cookie Tracking:**
   - Cookie `tracking_id` được dùng trong SQL query
   - Response khác nhau dựa trên cookie valid/invalid:
     - ✅ Valid tracking → "Welcome back! X page views"
     - ❌ Invalid → "Welcome, new visitor!"

### Credentials mặc định:
- `cookie_admin:C00k13_Adm1n_P@ss!`
- `analytics_mgr:An4lyt1cs_2024`

## 🎓 Kiến Thức

### Cookie Injection

```bash
# Inject via Cookie header
curl -b "tracking_id=abc123xyz' AND '1'='1" http://localhost:5025/
```

## 🚀 Hướng Dẫn

```bash
docker-compose up -d
curl -b "tracking_id=abc123xyz" http://localhost:5025/
```

## 🏁 Flag: `FLAG{...}`
