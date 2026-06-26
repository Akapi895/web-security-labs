# Detection - Path Traversal / LFI

## 1. Tham số cần test (high hit-rate)

- `file`
- `filename`
- `path`
- `page`
- `include`
- `template`
- `download`
- `folder`
- `doc`
- `view`
- `content`
- `layout`
- `mod`
- `conf`

## 2. Dấu hiệu phát hiện

- Response chứa nội dung file hệ thống (`root:x:0:0:`, `[extensions]`, `daemon:`).
- Response length thay đổi mạnh so với baseline.
- Lỗi filesystem:
  - `No such file or directory`
  - `failed to open stream`
  - `include():` / `require():`
  - `Access denied` / `Permission denied`
- App trả về source code thực thi một phần (config, template, stack trace).
- Param bị normalize bất thường (input khác nhau cho cùng response).

## 3. Quy trình phát hiện thủ công nhanh (5-10 phút)

1. Chụp baseline với input hợp lệ (`filename=1.png`).
2. Thử payload Linux: `../../../etc/passwd`.
3. Thử absolute payload: `/etc/passwd`.
4. Thử bypass payload: `....//....//etc/passwd`.
5. Thử encoded payload: `%252e%252e%252fetc%252fpasswd`.
6. Thử payload Windows nếu nghi stack Windows: `..\..\..\windows\win.ini`.
7. So sánh status/size/body với baseline.

## 4. Hành vi bất thường có thể khai thác

- Có check prefix nhưng không canonicalization (`/var/www/images/../../../etc/passwd`).
- Có check extension (`.png`) nhưng parser mismatch/null byte (legacy).
- WAF strip `../` nhưng bỏ sót nested pattern (`....//`).
- Web tier và app tier decode khác nhau (double decode).
- Reverse proxy và backend parse URL khác nhau (`..;/`).

## 5. Mẹo Burp/tự động hóa

- Intruder payload set: traversal plain + encoded + double encoded + Windows separator.
- Group theo response metrics: status code, content length, word count.
- Luôn thêm 1-2 control payload không hợp lệ để loại false positive.

## 6. CTF/PortSwigger-first checklist

- Endpoint có thao tác file chưa?
- Baseline đã lưu chưa?
- Đã thử Linux + Windows + encoded + nested chưa?
- Đã check `--path-as-is` nếu dùng curl chưa?
- Đã có proof file read rõ ràng (snippet) chưa?
