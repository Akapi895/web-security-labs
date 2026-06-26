# Phong Thu Va Giam Thieu NoSQL Injection

## Nguyen tac cot loi

Voi SQLi, cot loi la prepared statement.

Voi NoSQLi, cot loi tuong duong la:

**Server phai so huu query grammar, client chi duoc cung cap value da rang buoc.**

## 1) Giu query shape o phia server

Dung:

```js
const username = String(req.body.username);
const user = await db.collection("users").findOne({ username });
```

Khong dung:

```js
const user = await db.collection("users").findOne(req.body);
```

## 2) Chan key nguy hiem de quy

Can reject/strip key bat dau bang `$` va key path nguy hiem, theo kieu de quy (recursive).

Tool thuong dung (Node ecosystem):

- `express-mongo-sanitize`
- `mongo-sanitize`
- Mongoose `sanitizeFilter: true`

Luu y: sanitize top-level la chua du.

## 3) Validate schema va type ngay boundary

Can ep:

- scalar field khong duoc nhan object/array bat hop le
- field name theo allow-list
- operator theo allow-list
- regex neu cho phep thi co gioi han do dai/pattern

Library goi y:

- Joi
- Ajv
- Zod
- Pydantic

## 4) Auth flow an toan

Khong de login selector do client shape.

Pattern an toan:

```js
const username = String(req.body.username);
const password = String(req.body.password);

const user = await db.collection("users").findOne({ username });
if (!user) return deny();

if (!verifyPassword(password, user.passwordHash)) return deny();
issueSession(user);
```

## 5) Han che query feature nguy hiem

### Tranh `$where` neu khong bat buoc

Uu tien:

- field comparison ro rang
- query builder do server control

### Tranh user-controlled pipeline

Khong nhan raw `pipeline` tu client.

Neu can report/filter nang cao, map request sang stage theo allow-list.

### Giam blast radius cua JS path

Neu ha tang cho phep, tat server-side scripting feature khong can thiet.

## 6) Least privilege cho database account

Phan tach quyen:

- read/write theo collection
- bo quyen admin khong can thiet
- bo feature network/script nguy hiem neu khong dung

Neu co bug, impact van bi gioi han.

## 7) Error handling

Khong leak cho user:

- DB stack trace
- raw query object
- serialized exception co data nhay cam

Chi log noi bo voi muc do chi tiet can thiet cho incident response.

## Defense checklist

1. Chan object input o noi yeu cau scalar.
2. Reject key bat dau bang `$` theo de quy.
3. Khong spread untrusted filter vao selector.
4. Khong parse va tai su dung stored filter neu chua validate lai.
5. Tach auth verify khoi query selector do client shape.
6. Han che `$where` va user-controlled pipeline.
7. An thong tin loi nhay cam.
8. Ap least privilege cho DB user.

## Common sai lam

| Sai lam | Van de |
|--------|--------|
| Chi escape quote | operator injection van qua duoc |
| Nghi JSON "co cau truc nen an toan" | attacker can control chinh cau truc do |
| Chan mot vai operator o top-level | nested operator van lot |
| Tin stored data la trusted | second-order NoSQLi van xay ra |
| Auth query dung truc tiep request body | anti-pattern kinh dien |

## Cach verify sau khi fix

Sau khi patch, can retest:

- payload object tren scalar field bi reject
- bracket notation khong con doi query shape
- nested `$` key bi chan
- cung endpoint an toan o ca form, JSON, GraphQL
- stored filter khong the "song lai" o lan query sau

## Ket luan

NoSQLi la loi thiet ke query boundary.

Khi server so huu duoc:

- field
- operator
- expression
- pipeline

thi NoSQLi bi cat o goc, khong chi "giam nhe payload".
