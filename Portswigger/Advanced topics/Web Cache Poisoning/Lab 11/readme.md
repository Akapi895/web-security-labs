# Lab: URL normalization

Thử Param Miner -> `Guess everything!` nhưng không tìm thấy query/header nào dùng được.

Thử khai thác URL normalization, đổi `/` thành `%2f`.
![slash](images/slash.png)

thấy `cache hit`, khi truy cập lại Home thì response đã bị ảnh hưởng:
![home](images/home.png)

-> có sai khác normalize URL giữa cache và backend, khai thác được cache poisoning

Đổi payload thành:

```
/</p><script>alert(1)</script>
```

![res](images/res.png)

-> deliver to victim, Lab solved
