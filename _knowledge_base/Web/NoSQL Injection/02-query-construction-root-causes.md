# Query Construction Va Nguyen Nhan Goc Re

## Tong quan

Nguyen nhan that su cua NoSQLi khong phai do "ky tu nguy hiem", ma do app de input khong tin cay anh huong den **query grammar**.

Voi NoSQL, ranh gioi code/data thuong nam o:

- query object
- key operator
- JSON/BSON structure
- JavaScript expression (`$where`)
- aggregation pipeline

## Cac pattern code de bi loi

### 1. Noi chuoi de tao expression/query

```js
// VULNERABLE
const filter = { $where: "this.username == '" + username + "'" };
```

Loi o day la `username` khong con la value thuan, ma co the chen logic.

### 2. Dung truc tiep input lam query object

```js
// VULNERABLE
db.users.findOne({
  username: req.body.username,
  password: req.body.password
});
```

Neu `password` tro thanh `{ "$ne": "x" }`, check equality da bi pha.

### 3. Forward untrusted filter

```js
// VULNERABLE
db.products.find(req.body.filter);
```

Endpoint nay bi bien thanh query proxy.

### 4. Merge input vao base selector

```js
// VULNERABLE
const selector = { tenantId: req.user.tenantId, ...req.body.filter };
```

Rui ro:

- override key co san
- chen nested operator
- mat kiem soat selector shape

### 5. Loi serialization/deserialization

Pattern nguy hiem:

- `JSON.parse()` input roi dung ngay de query
- parser form/query string tao nested object ngoai y muon
- tai lai stored JSON va merge truc tiep

```js
// VULNERABLE
const filter = JSON.parse(req.body.filter);
db.items.find(filter);
```

### 6. Type confusion (scalar vs object/array)

App mong:

```json
{"password":"secret"}
```

Nhung lai chap nhan:

```json
{"password":{"$regex":"^a"}}
```

Hoac:

```text
username[$nin][]=admin&username[$nin][]=test
```

### 7. Chap nhan key bat dau bang `$`

Trong Mongo-style query, key bat dau bang `$` la instruction, khong phai data key.

Neu client control duoc cac key nay, query grammar da bi lo.

### 8. Duplicate key overwrite

```json
{"id":"10","id":"100"}
```

Neu parser giu key cuoi, pre/post-condition co the bi vo hieu.

### 9. Authentication logic flaw

```js
// VULNERABLE
const user = await db.users.findOne({
  username: req.body.username,
  password: req.body.password
});
if (user) issueSession(user);
```

Van de:

- auth bi giao toan bo cho selector do client shape
- `findOne()` tra ve doc dau tien match

### 10. Second-order NoSQLi

Flow thuong gap:

1. input duoc luu
2. luc luu khong thay tac dong
3. lan sau input duoc tai su dung trong query construction
4. injection xay ra muon

## Mapping "data nao duoc control"

| Duoc client control | Phai do server control |
|---------------------|------------------------|
| gia tri tim kiem | operator key |
| pagination value | field name nhay cam |
| sort direction co allow-list | query shape |
| regex text (neu cho phep) | JS clause, pipeline stage |

## Vi sao filtering thong thuong khong du

NoSQLi thuong dung:

- `{ }`, `[ ]`, `$`, `:`
- `%00`
- toan tu `||`, `&&`

Filter kieu HTML (`<`, `>`) thuong khong giai quyet duoc.

## Anti-pattern can tranh

| Anti-pattern | Van de |
|--------------|--------|
| "JSON la an toan hon SQL" | attacker van doi duoc query structure |
| "ORM se tu bao ve" | sai neu query shape van tu client |
| "chi can escape quote" | operator injection nhieu luc khong can quote |
| "sanitize top-level la du" | nested object van lot |
| "stored filter la trusted" | second-order van xay ra |

## Mental model phong thu

Server phai giu quyen quyet dinh:

- field nao duoc query
- operator nao duoc phep
- co cho regex hay khong
- co cho JS/pipeline feature hay khong

Client chi duoc gui value trong pham vi da rang buoc.
