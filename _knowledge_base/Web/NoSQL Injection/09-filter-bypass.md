# Filter Bypass Va Tinh Huong Dac Biet

## Tong quan

Voi NoSQLi, bypass thuong khong chi la obfuscate keyword.

Diem can tap trung la:

- parser behavior
- content-type transition
- object merge/overwrite
- nested operator pass qua sanitize khong de quy

## 1) Doi Content-Type

Nhieu endpoint an toan voi form scalar, nhung loi khi doi sang JSON object.

Form:

```text
username=admin&password=test
```

JSON:

```json
{"username":"admin","password":{"$ne":"x"}}
```

Khi test, nen thu:

1. GET -> POST
2. `application/x-www-form-urlencoded` -> `application/json`
3. payload logic giong nhau nhung doi transport format

## 2) Bracket notation

Form parser thuong bien:

```text
username[$ne]=x
password[$regex]=^adm
username[$nin][]=admin
```

thanh nested object. Day chinh la cau noi dua payload tu scalar sang operator object.

## 3) Duplicate key overwrite

```json
{"id":"10","id":"100"}
```

Neu parser giu key cuoi, dieu kien an toan co the bi ghi de.

## 4) Null-byte truncation

```text
fizzy'%00
```

Co the lam mat phan dieu kien phia sau trong mot so stack.

## 5) HTTP parameter pollution

Repeated parameter co the bi merge bat ngo:

```text
?username=admin&username[$ne]=x
?filter[name]=alice&filter[$where]=1
```

Phu thuoc framework:

- lay gia tri dau
- lay gia tri cuoi
- hoac merge thanh object

## 6) Reserved key collision

Key bat dau bang `$` vua la operator cua Mongo-style query, vua co the trung voi co che bien cua ngon ngu/framework.

Neu layer app xu ly khong dung, operator co the bi shadow/replace.

## 7) Nested operator hiding

Nhieu sanitize chi strip top-level `$`, nhung bo sot nested branch.

Vi du:

- block `$where` o top-level
- nhung van cho `$or` chua object co `$where` ben trong

=> sanitize phai de quy.

## 8) GraphQL filter confusion

GraphQL schema khong tu dong chan NoSQLi neu resolver van forward filter object truc tiep vao query layer.

Can map filter theo allow-list thay vi spread object.

## Luu y an toan khi test

Khong nen test bypass manh tren write path (`updateMany`, `deleteMany`) neu khong co scope ro rang, vi selector mo rong co the anh huong nhieu document.

## Checklist bypass nhanh

1. Thu lai payload voi nhieu content-type.
2. Test bracket notation va nested object.
3. Test duplicate key/repeated parameter.
4. Test nested operator bypass.
5. Xac minh signal tren read path truoc khi sang write path.
