# Lab: DOM XSS in document.write sink using source location.search inside a select element

Script:
    
```javascript   
var stores = ["London","Paris","Milan"];
var store = (new URLSearchParams(window.location.search)).get('storeId');
document.write('<select name="storeId">');
if(store) {
    document.write('<option selected>'+store+'</option>');
}
for(var i=0;i<stores.length;i++) {
    if(stores[i] === store) {
        continue;
    }
    document.write('<option>'+stores[i]+'</option>');
}
document.write('</select>');
```

Thấy web có url `/product?productId=1`, khi thử thêm param `&productId=RandomChar` thì thấy reflect tại:
```
<select name="storeId">
    <option selected="">RandomChar</option>
    <option>London</option>
    <option>Paris</option>
    <option>Milan</option>
</select>
```

-> Cần đóng thẻ `select` để inject xss payload.