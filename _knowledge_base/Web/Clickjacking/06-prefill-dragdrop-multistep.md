# Prefill, Kéo-thả, Nhiều bước

## Mục tiêu

Mô tả các pattern clickjacking vượt ra ngoài kịch bản nhấp một nút ẩn duy nhất.

## 1. Clickjacking với form điền sẵn

Một số endpoint cho phép nhận giá trị form từ URL trước khi người dùng bấm gửi.

Ý tưởng tấn công:

1. Attacker tạo URL mục tiêu với dữ liệu điền sẵn do attacker chọn.
2. Nạn nhân bị dẫn dụ nhấp vào phần tử trông như nút mồi.
3. Nút submit ẩn trên trang mục tiêu ghi nhận dữ liệu do attacker chỉ định.

Use case thường gặp trong tài liệu huấn luyện:

1. Cập nhật trường hồ sơ.
2. Đổi email/thông tin liên hệ.
3. Đổi cài đặt nhẹ chỉ cần một lần submit.

## 2. Pattern kéo-thả hỗ trợ

Trong một số bối cảnh UI/trình duyệt, kéo-thả có thể đặt dữ liệu do attacker kiểm soát vào field thuộc trang mục tiêu, sau đó một cú nhấp sẽ hoàn tất hành động.

Chuỗi mức cao:

1. Nạn nhân thực hiện thao tác kéo trên trang attacker.
2. Dữ liệu từ payload rơi vào input bị nhúng ẩn.
3. Nạn nhân thực hiện cú nhấp tiếp theo vào control submit đã căn chỉnh.

## 3. Clickjacking nhiều bước

Một số hành động mục tiêu cần nhiều tương tác (ví dụ thêm vào giỏ rồi xác nhận). Attacker phải mô hình hóa bằng các lớp mồi theo từng bước.

Thách thức chính:

1. Trạng thái UI thay đổi giữa các bước.
2. Nhạy cảm theo thời điểm.
3. Xác suất nạn nhân nhận ra bất thường cao hơn.

## Mô hình pattern nhiều bước

```text
BƯỚC 1: Căn control nhạy cảm đầu tiên với prompt mồi A
BƯỚC 2: Sau khi chuyển trạng thái, căn control thứ hai với prompt mồi B
BƯỚC 3: Kích hoạt xác nhận cuối
```

## Cân nhắc độ ổn định

| Yếu tố | Prefill | Kéo-thả | Nhiều bước |
| --- | --- | --- | --- |
| Phụ thuộc tham số URL | Cao | Thấp | Trung bình |
| Biến thiên theo trình duyệt | Trung bình | Cao | Cao |
| Mức công sức người dùng | Thấp | Trung bình | Trung bình-Cao |
| Rủi ro bị phát hiện | Trung bình | Trung bình | Cao |

## Góc nhìn phòng thủ

Các biến thể này hiệu quả nhất khi hành động tác động cao quá dễ hoàn tất. Gia cố UX (xác nhận, re-auth, màn hình review rõ ràng) sẽ giảm mạnh độ ổn định khai thác.

## Tệp liên quan

- [Khai thác cơ bản](05-basic-exploitation.md)
- [DoubleClickjacking và biến thể Popup](07-doubleclickjacking-and-popup-variants.md)
- [Phòng thủ và giảm thiểu](13-defense-mitigation.md)
