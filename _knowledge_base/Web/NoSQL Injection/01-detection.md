# Phat Hien NoSQL Injection

## Muc tieu phat hien

Khi test NoSQLi, can tra loi 3 cau hoi:

1. Input co di vao query khong?
2. Input duoc xu ly nhu value hay query structure?
3. Context thuc thi la filter object, expression (`$where`) hay `aggregation pipeline`?

NoSQL khong co syntax chung nhu SQL, nen phat hien tot phu thuoc vao viec map parser chain.

## Injection point thuong gap

| Vi tri | Ly do nguy hiem | Vi du |
|-------|------------------|------|
| GET parameter | parser co the tao nested object | `?user[$ne]=x` |
| POST form | bracket notation hay bi parse thanh object | `password[$regex]=^a` |
| POST JSON | object di thang vao query | `{"password":{"$gt":""}}` |
| GraphQL filter | resolver hay forward `args.filter` | `{"filter":{"$ne":{}}}` |
| Header/Cookie | co the bi deserialize | `X-Filter: {"role":{"$ne":"user"}}` |
| Stored input | second-order khi tai su dung | stored JSON filter |

## Quy trinh detection

### Buoc 1: map parser chain

Can xac dinh:

- `Content-Type` dang la gi (`x-www-form-urlencoded`, JSON, GraphQL)
- bracket notation co tao object khong
- scalar field co chap nhan object khong
- input vao `find()`, `findOne()`, `aggregate()`, hay `$where`

Dau hieu goi y:

- payload dang `name[$ne]=x` duoc he thong chap nhan
- response/co loi co chu `BSON`, `Mongo`, `selector`, `pipeline`
- endpoint search co ve xu ly regex

### Buoc 2: test syntax handling

Neu nghi ngo input nam trong string/expression, test fuzz string:

```text
'"`{
;$Foo}
$Foo \xYZ
```

URL context thi URL-encode; JSON context thi gui ban da escape.

### Buoc 3: xac dinh ky tu/key nao duoc xu ly

Test tung probe:

| Probe | Muc dich |
|------|---------|
| `'` | break string context |
| `\"` | test escaping |
| `{}` | test object acceptance |
| `%00` | test null-byte truncation |
| `$ne`, `$regex` | test operator acceptance |
| duplicate key | test overwrite behavior |

Pattern thuong thay:

```text
'      -> response thay doi
'\''   -> response on dinh
```

### Buoc 4: test operator injection

Test tren ca JSON va form-urlencoded:

| Muc dich | JSON | Form-urlencoded |
|---------|------|-----------------|
| broad match | `{"username":{"$ne":"invalid"}}` | `username[$ne]=invalid` |
| field exists | `{"username":{"$exists":true}}` | `username[$exists]=true` |
| regex oracle | `{"password":{"$regex":"^a"}}` | `password[$regex]=^a` |
| target account | `{"username":{"$in":["admin","root"]}}` | array format tuy stack |

Neu query logic thay doi, kha nang cao da co operator injection.

### Buoc 5: confirm true/false behavior

Dung cap payload de tao oracle:

Syntax-style:

```text
' && 0 && 'x
' && 1 && 'x
```

Operator-style:

```json
{"username":"admin","password":{"$regex":"^a"}}
{"username":"admin","password":{"$regex":"^z"}}
```

Neu response khac nhau co quy luat, co the dung de blind extraction.

### Buoc 6: timing va error-based

Khi content diff yeu, test delay hoac error leak:

```json
{"$where":"sleep(5000)"}
{"$where":"throw new Error(JSON.stringify(this))"}
```

Chi dung timing khi da do baseline on dinh.

## Response indicator can theo doi

| Dau hieu | Y nghia |
|---------|---------|
| redirect vao dashboard | auth bypass/oracle dung |
| ket qua tra ve rong hon | filter da bi mo rong |
| item an xuat hien | post-condition bi bo qua |
| status code doi | query/parser behavior doi |
| stack trace DB | syntax/deserialization issue |
| delay co dieu kien | JS clause dang duoc evaluate |

## Fingerprinting theo model

NoSQL fingerprinting uu tien xac dinh **execution model**, khong phai luc nao cung can version.

### Dau hieu MongoDB-style

| Quan sat | Dien giai |
|---------|-----------|
| `$ne`, `$gt`, `$regex` co tac dung | operator path lo ra |
| `username[$ne]=x` tao nested object | parser dang co coercion |
| regex prefix cho behavior on dinh | co the blind enum |
| `$where` anh huong response | expression path kha dung |
| duplicate key overwrite | parser behavior nguy hiem |
| chap nhan array stage | co kha nang `aggregate()` |

### Dau hieu app-layer query shaping

| Quan sat | Dien giai |
|---------|-----------|
| GraphQL filter nhan key la | resolver forward truc tiep |
| scalar field nhan object | type validation yeu |
| loi serializer/deserializer | parse/merge khong an toan |
| loi xuat hien khi tai su dung data | second-order NoSQLi |

## Second-order detection

Second-order NoSQLi thuong theo flow:

1. Input duoc luu.
2. Luc luu chua gay tac dong ro.
3. Sau do duoc deserialize/merge vao query khac.
4. Injection xay ra o lan su dung thu hai.

Vi du:

- saved search filter
- profile field duoc dung lai trong admin query
- JSON template luu trong DB/flat file

## Checklist nhanh

1. Liet ke toan bo endpoint co filter/search/login.
2. Test scalar va object payload tren cung field.
3. Test syntax probes + operator probes + true/false probes.
4. Thu doi `Content-Type` va method (GET/POST).
5. Kiem tra signal qua content/status/redirect/error/timing.
6. Xac nhan tai cho hay second-order.
