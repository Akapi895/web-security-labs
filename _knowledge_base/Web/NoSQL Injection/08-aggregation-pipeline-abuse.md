# Aggregation Pipeline Abuse

## Tong quan

`Aggregation pipeline` tao mot attack surface khac voi `find()`/`findOne()`.

Neu client control duoc pipeline, attacker co the can thiep:

- stage nao duoc chay
- thu tu stage
- collection nao duoc join
- output duoc reshape ra sao

## Vi sao nguy hiem

`find()` thuong chi tra loi "doc nao match?".

`aggregate()` co the:

- loc
- bien doi
- join collection khac
- gom nhieu sub-query

Do do, endpoint aggregate de bi tro thanh primitive exfiltration manh.

## Pattern code de bi loi

```js
// VULNERABLE
db.orders.aggregate(req.body.pipeline);
```

hoac:

```js
// VULNERABLE
const pipeline = [{ $match: safeFilter }, ...req.body.extraStages];
db.orders.aggregate(pipeline);
```

Ngay ca khi co `$match` ban dau, stage tiep theo van co the doi huong query.

## Stage thuong bi abuse

| Stage | Kieu abuse |
|-------|------------|
| `$match` | mo rong selector |
| `$lookup` | pivot sang collection khac |
| `$project` | lo field an/reshape output |
| `$facet` | chay nhieu nhanh query song song |
| `$skip` / `$limit` | dieu khien extraction order |

## Vi du `$lookup` pivot

```json
[
  {
    "$lookup": {
      "from": "users",
      "as": "resultado",
      "pipeline": [
        {
          "$match": {
            "password": { "$regex": "^.*" }
          }
        }
      ]
    }
  }
]
```

Neu endpoint chap nhan pipeline nay, attacker co the doc data collection `users` du endpoint goc khong query truc tiep collection do.

## Detection hint

Dau hieu endpoint co nguy co:

- chap nhan body la mang stage
- parameter ten `pipeline`, `stages`, `aggregate`
- response nested/reshaped theo kieu aggregate output

## Workflow khai thac

1. Confirm endpoint dung `aggregate()`.
2. Xac dinh muc do control (toan bo pipeline hay mot phan stage).
3. Mo rong pham vi qua `$match`.
4. Pivot collection qua `$lookup` neu co quyen.
5. Dung `$project` de hien thi field can lay ro rang.

## Khac gi voi operator injection

| Kha nang | Operator injection | Pipeline abuse |
|----------|--------------------|----------------|
| mo rong filter | Co | Co |
| join collection khac | Han che | Manh (`$lookup`) |
| reshape output | Han che | Manh |
| chain nhieu bien doi | Han che | Co |

## Gioi han

Pipeline abuse can:

- endpoint su dung `aggregate()`
- input co the chen/sua stage
- output tra ve du thong tin de attacker su dung

Neu app chi dung `find()`, payload pipeline thuong khong co tac dung.

## Gia tri voi lab

Dang bai nay rat hop de day ky nang "query-program reasoning":

- khong chi "match nhieu doc hon"
- ma la "dieu khien toan bo chuong trinh query"
