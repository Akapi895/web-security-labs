# File Upload — Defense & Mitigation

## Nguyên tắc tổng quát

Phòng thủ File Upload hiệu quả dựa trên nguyên tắc **defense in depth** — không dựa vào một lớp kiểm tra duy nhất mà kết hợp nhiều lớp validation, storage isolation, và execution prevention. Mỗi lớp giả định rằng lớp phía trước có thể bị bypass.

## Kiến trúc Upload An toàn

```
Client                    Application Layer           Storage Layer
  |                            |                           |
  |-- Upload request --------> |                           |
  |                            |-- 1. Extension whitelist   |
  |                            |-- 2. Content-Type check    |
  |                            |-- 3. Magic bytes verify    |
  |                            |-- 4. Content scanning      |
  |                            |-- 5. Rename (random)       |
  |                            |-- 6. Size limit check      |
  |                            |                           |
  |                            |-- Store to isolated -----> |
  |                            |   non-exec storage         |
  |                            |                           |
  |<-- Response (status) ----- |                           |
  |                            |                           |
  |-- Access request --------> |                           |
  |                            |-- Serve via download       |
  |                            |   endpoint (not direct)    |
  |<-- File content ---------- |                           |
```

## 1. Extension Validation

### Dùng Whitelist, không Blacklist

Whitelist chỉ cho phép các extension cần thiết cho business logic:

```python
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.pdf'}

def validate_extension(filename):
    ext = os.path.splitext(filename)[1].lower()
    return ext in ALLOWED_EXTENSIONS
```

**Tại sao không dùng blacklist**: Blacklist luôn không đầy đủ — bỏ sót extension thay thế (`.php5`, `.phtml`, `.cer`...), không theo kịp extension mới.

### Validate full filename

Không chỉ kiểm tra extension mà phải validate **toàn bộ tên file**:

- Không chứa path traversal (`../`, `..\`)
- Không chứa null bytes
- Không chứa ký tự đặc biệt
- Chiều dài hợp lý

```python
import re

def validate_filename(filename):
    # Chỉ cho phép alphanumeric, 1 dot, extension hợp lệ
    pattern = r'^[a-zA-Z0-9]{1,200}\.[a-zA-Z0-9]{1,10}$'
    return bool(re.match(pattern, filename))
```

## 2. Content Validation

### Verify MIME type server-side

Không tin tưởng `Content-Type` header từ client. Sử dụng server-side detection:

```python
import magic

def validate_content(file_path):
    mime = magic.from_file(file_path, mime=True)
    allowed_mimes = {'image/jpeg', 'image/png', 'image/gif'}
    return mime in allowed_mimes
```

### Verify magic bytes

```python
SIGNATURES = {
    b'\xff\xd8\xff': 'jpeg',
    b'\x89PNG\r\n\x1a\n': 'png',
    b'GIF87a': 'gif',
    b'GIF89a': 'gif',
}

def check_magic(file_path):
    with open(file_path, 'rb') as f:
        header = f.read(8)
    return any(header.startswith(sig) for sig in SIGNATURES)
```

### Verify image properties

```python
from PIL import Image

def validate_image(file_path):
    try:
        img = Image.open(file_path)
        img.verify()  # Kiểm tra file integrity
        return True
    except Exception:
        return False
```

### Scan nội dung file

- Với ảnh: Kiểm tra dimensions, structure, strip metadata
- Với documents: Scan malware, macro, embedded objects
- Với archive: Kiểm tra entries trước khi giải nén

## 3. Filename Handling

### Đổi tên file bằng algorithm

Không bao giờ dùng tên file gốc từ client:

```python
import uuid
import os

def generate_safe_filename(original_filename):
    ext = os.path.splitext(original_filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError("Invalid extension")
    return f"{uuid.uuid4().hex}{ext}"
```

Hoặc dùng hash:

```python
import hashlib
import time

def generate_filename(original):
    ext = os.path.splitext(original)[1].lower()
    name_hash = hashlib.sha256(f"{original}{time.time()}".encode()).hexdigest()
    return f"{name_hash}{ext}"
```

### Strip all dangerous characters

```python
def sanitize_filename(filename):
    # Xóa control characters, unicode, special chars
    clean = re.sub(r'[^\w\-.]', '', filename)
    # Xóa multiple dots (giữ chỉ dot cuối cho extension)
    parts = clean.rsplit('.', 1)
    if len(parts) == 2:
        name = parts[0].replace('.', '')
        return f"{name}.{parts[1]}"
    return clean
```

## 4. Storage Security

### Lưu file ngoài web root

```
/var/www/html/          ← Web root — KHÔNG lưu file upload ở đây
/var/uploads/           ← Upload storage — ngoài web root
```

File được serve qua download endpoint, không truy cập trực tiếp:

```python
@app.route('/download/<file_id>')
def download(file_id):
    # Lookup file_id trong database → lấy path
    file_path = db.get_file_path(file_id)
    return send_file(file_path, as_attachment=True)
```

### Lưu trong database thay vì filesystem

```python
# Lưu binary content vào database
def store_file(file_data, metadata):
    db.execute(
        "INSERT INTO uploads (content, filename, mime_type, uploaded_at) VALUES (?, ?, ?, ?)",
        [file_data, metadata['name'], metadata['mime'], datetime.now()]
    )
```

### Dùng volume riêng / CDN

- Lưu file trên volume/partition riêng → tách biệt khỏi OS và application
- Dùng CDN (S3, CloudFront, Azure Blob) → file không bao giờ nằm trên application server
- Serve từ domain khác → ngăn same-origin attacks

## 5. Execution Prevention

### Tắt script execution trong upload directory

**Apache:**

```apache
<Directory "/var/www/uploads">
    php_admin_flag engine off
    RemoveHandler .php .phtml .php5 .php7
    RemoveType .php .phtml .php5 .php7

    # Deny all script handlers
    <FilesMatch ".*">
        SetHandler none
        ForceType application/octet-stream
    </FilesMatch>
</Directory>
```

**Nginx:**

```nginx
location /uploads/ {
    # Không có fastcgi_pass → không execute PHP
    # Serve tất cả file như static content
    location ~ \.php$ {
        deny all;
    }
}
```

**IIS (web.config):**

```xml
<configuration>
<system.webServer>
    <handlers>
        <clear />
        <add name="StaticFile" path="*" verb="*"
             modules="StaticFileModule"
             resourceType="Either" requireAccess="Read" />
    </handlers>
</system.webServer>
</configuration>
```

### Remove execute permission

```bash
# Linux
chmod -R -x+X /var/www/uploads/

# Chỉ cho phép read, không execute
chmod 644 /var/www/uploads/*
```

## 6. Access Control

### Chỉ authenticated users mới được upload

```python
@app.route('/upload', methods=['POST'])
@login_required
def upload():
    # ...
```

### Chỉ authorized users mới truy cập file

```python
@app.route('/files/<file_id>')
@login_required
def get_file(file_id):
    file = db.get_file(file_id)
    if file.owner_id != current_user.id:
        abort(403)
    return send_file(file.path)
```

### CSRF protection

Áp dụng CSRF token cho upload form để ngăn cross-site upload.

## 7. Size Limits

```python
# Giới hạn kích thước tối đa
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

# Giới hạn kích thước tối thiểu (ngăn DoS bằng file 0-byte)
MIN_FILE_SIZE = 100  # bytes

def validate_size(file):
    file.seek(0, 2)  # Seek to end
    size = file.tell()
    file.seek(0)     # Reset
    return MIN_FILE_SIZE <= size <= MAX_FILE_SIZE
```

## 8. Response Headers

Khi serve uploaded files, thêm security headers:

```
Content-Disposition: attachment; filename="safe_name.ext"
X-Content-Type-Options: nosniff
Content-Type: application/octet-stream
```

- `Content-Disposition: attachment` → force download, ngăn inline rendering
- `X-Content-Type-Options: nosniff` → ngăn browser MIME sniffing
- Đảm bảo Content-Type chính xác → ngăn browser interpret sai

## 9. Configuration File Protection

### Chặn upload config files

```python
BLOCKED_FILENAMES = {
    '.htaccess', '.htpasswd', 'web.config',
    '.user.ini', 'php.ini', '.env',
    'crossdomain.xml', 'clientaccesspolicy.xml'
}

def is_config_file(filename):
    return filename.lower() in BLOCKED_FILENAMES
```

### Cấu hình server bỏ qua config files trong upload directory

```apache
# Apache — Ignore .htaccess trong uploads/
<Directory "/var/www/uploads">
    AllowOverride None
</Directory>
```

## 10. Archive Handling

Khi cần xử lý archive (ZIP, TAR):

```python
import zipfile
import os

def safe_extract(zip_path, dest_dir):
    with zipfile.ZipFile(zip_path, 'r') as z:
        for entry in z.namelist():
            # Kiểm tra path traversal
            target = os.path.realpath(os.path.join(dest_dir, entry))
            if not target.startswith(os.path.realpath(dest_dir)):
                raise ValueError(f"Path traversal detected: {entry}")

            # Kiểm tra symlink
            info = z.getinfo(entry)
            if info.external_attr >> 16 & 0o120000 == 0o120000:
                raise ValueError(f"Symlink detected: {entry}")

        z.extractall(dest_dir)
```

## 11. CORS Headers

```
Access-Control-Allow-Origin: [specific trusted origins only]
Access-Control-Allow-Methods: [chỉ methods cần thiết]
Access-Control-Allow-Credentials: [true chỉ khi cần]
```

Không dùng `Access-Control-Allow-Origin: *` cho authenticated endpoints.

## 12. Logging & Monitoring

```python
import logging

def log_upload(user, filename, status, details=""):
    logging.info(
        f"UPLOAD | user={user} | filename={filename} | "
        f"status={status} | details={details}"
    )
```

Log cần capture:

- User thực hiện upload
- Tên file gốc và tên file sau sanitize
- Kết quả validation (pass/fail)
- Lý do reject (nếu có)
- IP address, timestamp

## Checklist phòng thủ

```
[ ] Whitelist extensions (không dùng blacklist)
[ ] Validate full filename (length, chars, no traversal)
[ ] Verify content server-side (magic bytes, MIME, structure)
[ ] Đổi tên file bằng hash/UUID
[ ] Lưu ngoài web root hoặc trên storage riêng
[ ] Tắt script execution trong upload directory
[ ] Serve file qua download endpoint + Content-Disposition: attachment
[ ] Thêm X-Content-Type-Options: nosniff
[ ] Giới hạn file size (min và max)
[ ] Chặn upload config files (.htaccess, web.config)
[ ] CSRF protection trên upload form
[ ] Authentication/authorization cho upload và download
[ ] Virus/malware scanning
[ ] Safe archive extraction (check traversal, symlinks)
[ ] Logging đầy đủ upload activities
[ ] CORS headers restrictive
[ ] Disable browser caching cho policy files
```
