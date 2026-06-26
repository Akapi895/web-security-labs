# Web Cache Deception (WCD) - Bao Cao Tong Hop

## 1. WCD la gi va ban chat ky thuat

Web Cache Deception la lo hong cho phep ke tan cong danh lua cache layer de luu response dynamic chua du lieu nhay cam nhu mot tai nguyen static.

Ban chat cua WCD khong nam o mot payload don le, ma nam o **sai lech cach xu ly URL/request giua cache va origin**.

## 2. Dynamic content va cached content

| Loai noi dung   | Dac diem                | Caching policy mong doi |
| --------------- | ----------------------- | ----------------------- |
| Static content  | Dung chung, it thay doi | Co the cache cong khai  |
| Dynamic content | Phu thuoc user/session  | Thuong private/no-store |

WCD xay ra khi dynamic content bi cache nham do cache rule parser mismatch.

## 3. Nguyen nhan goc re

### 3.1 Path parsing va mapping discrepancy

- Origin route theo REST abstraction.
- Cache map theo file path va static extension.

### 3.2 Delimiter discrepancy

- Ky tu la delimiter o origin (vi du `;`) nhung khong la delimiter o cache.

### 3.3 Delimiter decoding discrepancy

- Origin decode `%23` thanh `#` truoc khi parse.
- Cache ap rule tren path chua decode.

### 3.4 Normalization discrepancy

- Origin va cache khac nhau o decode slash + resolve dot-segment.

### 3.5 Cache rules/key va config override

- Rule extension/prefix/file-name qua rong.
- Edge co the override cache policy cua origin.

## 4. Cache rules quan trong trong WCD

1. Extension-based rule (`.css`, `.js`, `.ico`, ...).
2. Static directory rule (`/static`, `/assets`, `/resources`, ...).
3. Exact file name rule (`robots.txt`, `favicon.ico`, `index.html`).

## 5. Quy trinh khai thac tong quat

1. Tim endpoint dynamic co du lieu nhay cam.
2. Tim discrepancy parser (mapping, delimiter, normalization).
3. Tao payload kich hoat cache rule.
4. Xac nhan cache oracle (`miss -> hit`).
5. Dan victim truy cap payload URL (victim priming).
6. Request lai cung URL de lay du lieu victim.

## 6. Cac pattern tan cong chinh

1. Path mapping + extension: `/dynamic/extra.js`
2. Delimiter + extension: `/dynamic;wcd.js`
3. Encoded delimiter: `/dynamic%23wcd.css`
4. Origin normalization: `/resources/..%2fdynamic`
5. Cache normalization + delimiter: `/dynamic%23%2f%2e%2e%2fresources`

## 7. Detection theo tu duy he thong

### 7.1 Oracle can theo doi

- `X-Cache`, `CF-Cache-Status`, `Age`, response time.

### 7.2 Nguyen tac test

- Luon dung cache buster de tao key moi.
- So sanh baseline (`/target`, `/targetabc`, `/target/abc`).
- Fuzz delimiter plain va encoded.
- Test traversal normalized payload (`..%2f`).

## 8. Tac dong bao mat

| Tac dong                      | Mo ta                                   |
| ----------------------------- | --------------------------------------- |
| Lo du lieu rieng tu           | API key, session/JWT, thong tin profile |
| Ho tro account takeover chain | Lo token/session tu endpoint auth       |
| Rui ro compliance             | Vi pham quy dinh bao ve du lieu         |

## 9. Phong thu dung ban chat

1. Dynamic endpoint nhay cam phai `Cache-Control: no-store, private`.
2. Khong cache route dynamic dua tren extension/prefix don thuan.
3. Bat kiem tra extension va `Content-Type` (neu CDN ho tro).
4. Dong bo parser/normalization giua CDN/proxy/origin.
5. Tu choi URL mo ho, encoded traversal, delimiter bat thuong.
6. Them regression tests cho cac payload WCD.

## 10. Mapping "nguyen nhan -> hau qua -> giai phap"

| Nguyen nhan               | Hau qua                          | Giai phap uu tien                                   |
| ------------------------- | -------------------------------- | --------------------------------------------------- |
| Mapping discrepancy       | Dynamic data bi cache nhu static | Strict routing, reject extra segments               |
| Delimiter discrepancy     | Cache luu response private       | Canonical parse policy, reject ambiguous delimiters |
| Decode/normalize mismatch | Bypass cache rule boundaries     | Parser parity tests, normalize policy dong nhat     |
| Cache rules qua rong      | Mo rong mat tan cong             | Cache allow-list theo route + content-type checks   |
| Edge override policy      | No-store khong con hieu luc      | Dong bo CDN config voi origin security intent       |

## 11. Ket luan

WCD la loi kien truc va dong bo parser/rule trong he thong nhieu lop, khong phai loi payload don gian. Muon triet tieu WCD, can sua tu goc:

- Chuan hoa URL parsing/normalization giua cache va origin.
- Giam cacheability cho dynamic endpoint.
- Kiem thu theo workflow discrepancy thay vi test theo tung payload roi rac.
