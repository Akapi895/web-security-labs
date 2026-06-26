# Phòng thủ và giảm thiểu

## Mục tiêu

Xây dựng chiến lược phòng thủ nhiều lớp trước clickjacking/UI redressing, ưu tiên kiểm soát ở máy chủ và bổ sung ma sát hợp lý ở tầng UX.

## 1. Chặn framing ở tầng máy chủ

Kiểm soát ưu tiên:

1. `Content-Security-Policy: frame-ancestors ...`
2. `X-Frame-Options` cho tương thích hệ cũ

Ví dụ CSP mạnh cho endpoint nhạy cảm:

```http
Content-Security-Policy: frame-ancestors 'none'
```

Hoặc allowlist chặt chẽ:

```http
Content-Security-Policy: frame-ancestors 'self' https://trusted.partner.example
```

XFO nên dùng như lớp tương thích bổ sung:

```http
X-Frame-Options: DENY
```

## 2. Không phụ thuộc frame-buster phía client

JavaScript frame-busting không nên là lớp bảo vệ chính vì dễ lệ thuộc môi trường thực thi và hành vi trình duyệt.

## 3. Gia cố UX cho hành động rủi ro cao

1. Re-auth cho thao tác nhạy cảm.
2. Bước xác nhận có ngữ cảnh rõ ràng.
3. Transaction binding (ràng buộc ý định thao tác).
4. Chống lạm dụng thao tác một cú nhấp với quyền cao.

## 4. Thu hẹp bề mặt endpoint nhạy cảm

1. Tách route hiển thị và route thực thi hành động.
2. Giảm endpoint “nhấp là xong” cho chức năng nguy cơ cao.
3. Bổ sung kiểm tra server-side theo ngữ cảnh hành vi.

## 5. Chính sách nhất quán toàn bộ route

Nhiều hệ thống chỉ gắn header bảo vệ ở một phần route, tạo lỗ hổng nằm rải rác. Cần audit đầy đủ và áp policy đồng nhất.

## 6. Regression test bảo mật

Tối thiểu nên có kiểm tra tự động:

1. Mọi endpoint nhạy cảm đều trả về `frame-ancestors` mong đợi.
2. Header không bị mất sau thay đổi reverse proxy/CDN.
3. Kiểm tra thủ công định kỳ trên trình duyệt mục tiêu.

## 7. Giám sát và phát hiện

1. Phát hiện bất thường ở luồng consent/cấu hình nhạy cảm.
2. Theo dõi pattern thay đổi trạng thái trái ngữ cảnh sử dụng bình thường.
3. Kết hợp logging hành động quan trọng với cảnh báo rủi ro.

## 8. Chiến lược xử lý theo mức độ ưu tiên

1. Đóng ngay framing cho endpoint có tác động kinh doanh cao.
2. Bổ sung re-auth/confirm cho thao tác không thể hoàn tác.
3. Chuẩn hóa policy ở gateway/nginx/app middleware.
4. Cập nhật checklist secure design cho đội sản phẩm.

## Checklist triển khai nhanh

1. Đã xác định danh sách endpoint nhạy cảm chưa?
2. Đã áp CSP `frame-ancestors` phù hợp cho từng nhóm chưa?
3. Đã giữ XFO tương thích cho môi trường legacy chưa?
4. Đã có regression test header ở CI/CD chưa?
5. Đã thêm ma sát UX cho thao tác rủi ro cao chưa?

## Tệp liên quan

- [Điều kiện và nguyên nhân gốc rễ](03-conditions-and-root-causes.md)
- [Workflow khai thác](11-exploitation-workflows.md)
- [Kịch bản lab và huấn luyện agent](14-labs-and-agent-training-scenarios.md)
