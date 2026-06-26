# Mau Thiet Ke Lab NoSQL Injection

## Tong quan

Lab NoSQLi tot can day duoc tu duy:

- input vao dau
- parser bien doi nhu the nao
- oracle nao xac nhan thanh cong
- exploit pattern nao dang duoc train

Muc tieu la hoc **query-shape reasoning**, khong chi hoc thuoc payload.

## Nhom lab cot loi

| Loai lab | Ky nang chinh | Oracle phu hop |
|----------|---------------|----------------|
| Basic operator bypass | scalar vs object confusion | redirect login |
| Syntax injection | break `$where` string context | content diff |
| Blind regex extraction | enum theo prefix | success/fail ro rang |
| JS timing injection | timing oracle | delay co dieu kien |
| Aggregation pivot | abuse `$lookup` | nested data xuat hien |
| Second-order NoSQLi | exploit tai lan su dung thu 2 | tac dong muon o admin flow |

## Pattern code toi thieu de dung lab

### 1) Login form (urlencoded)

```js
app.post("/login", async (req, res) => {
  const user = await db.collection("users").findOne({
    username: req.body.username,
    password: req.body.password
  });
  if (user) return res.redirect("/dashboard");
  return res.status(401).send("Invalid credentials");
});
```

Dung de train:

- operator injection
- auth bypass
- blind extraction

### 2) Search voi `$where`

```js
app.get("/search", async (req, res) => {
  const q = req.query.q;
  const items = await db.collection("products").find({
    $where: "this.category == '" + q + "'"
  }).toArray();
  res.json(items);
});
```

Dung de train syntax injection va field probing.

### 3) Aggregate endpoint

```js
app.post("/report", async (req, res) => {
  const docs = await db.collection("orders").aggregate(req.body.pipeline).toArray();
  res.json(docs);
});
```

Dung de train pipeline abuse va cross-collection pivot.

## Thiet ke oracle ro rang

| Oracle | Nen dung cho |
|--------|--------------|
| redirect | auth bypass |
| secret field xuat hien | visible extraction |
| status code doi | boolean lab |
| delay co dinh | timing lab |
| stack error | error-based lab |

Oracle cang on dinh, nguoi hoc cang de hieu luong khai thac.

## Tang do kho

### Easy

- auth bypass co signal ro
- khong rate limit
- payload ngan

### Medium

- yeu cau target account cu the
- can doi content-type hoac dung bracket notation
- blind extraction theo prefix

### Hard

- second-order flow
- timing-only oracle
- nested sanitize bypass
- aggregation pivot nhieu buoc

## Data model goi y

- `users`: username, password, role, email
- `products`: category, released, hidden, cost
- `orders`: tenantId, customerId, notes
- `adminNotes`: collection nhay cam de train pivot

Model nay giup train:

- auth bypass
- filter bypass
- tenant isolation failure
- cross-collection data leak

## Checklist cho tac gia lab

1. Xac dinh ro parser behavior dang bi loi.
2. Dam bao payload intended path chac chan reach duoc.
3. Chon oracle ro, lap lai duoc.
4. Viet query loi ngan gon de hoc vien doc hieu nhanh.
5. Mapping fix ro rang ve root cause.

## Gia tri cho huan luyen agent

NoSQLi lab rat hop de train agent vi bat buoc agent phai suy luan:

- transport format
- parser transformation
- query shape
- oracle reliability
- exploitation sequence theo workflow
