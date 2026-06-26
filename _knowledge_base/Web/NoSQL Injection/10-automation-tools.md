# Automation Tools Cho NoSQL Injection

## Tong quan

Automation giup tang toc, nhung NoSQLi rat phu thuoc parser context.

Nguyen tac:

- lam tay de map context truoc
- chi automate khi da co oracle on dinh

## Tool thuong dung

| Tool | Muc dich |
|------|---------|
| NoSQLMap | enum va exploit case Mongo-style co cau truc ro |
| Burp Repeater | map parser, test payload co kiem soat |
| Burp Intruder | blind extraction theo ky tu/wordlist |
| Burp NoSQLiScanner | goi y pattern va issue ban dau |
| Wordlist | do username, field, operator |

## Workflow automation de dung

1. Xac dinh transport format dung (`JSON`, form, GraphQL).
2. Confirm vulnerability bang payload thu cong.
3. Chot oracle (`redirect`, `status`, `content`, `timing`).
4. Moi bat dau viet script/Intruder attack.

Neu automate qua som, thuong fuzz sai parser path.

## Burp workflow goi y

### Repeater

Dung de:

- test scalar -> object transition
- test operator acceptance
- test content-type switching

### Intruder

Hop voi:

- blind prefix extraction qua `$regex`
- dictionary attack field name
- timing confirmation nhieu lan

## Mau script blind extraction (y tuong)

```python
alphabet = "abcdefghijklmnopqrstuvwxyz0123456789-_"
prefix = ""

while True:
    found = False
    for ch in alphabet:
        payload = {"username": {"$eq": "admin"}, "password": {"$regex": "^" + prefix + ch}}
        if oracle_is_true(payload):
            prefix += ch
            found = True
            break
    if not found:
        break
```

Oracle co the la redirect, message, status hoac response-length.

## Mau timing-based (y tuong)

```python
def oracle_is_true(prefix):
    payload = {"$where": "this.username=='admin' && this.password.match(/^" + prefix + "/) && sleep(3000)"}
    # do response time va so baseline
```

Can retry nhieu lan de giam noise.

## Wordlist huu ich

- username: `admin`, `administrator`, `root`
- field: `password`, `email`, `token`, `role`, `apikey`
- operator: `$ne`, `$gt`, `$in`, `$exists`, `$regex`, `$where`

## Lab/resource de luyen

| Resource | Muc dich |
|----------|---------|
| `digininja/nosqlilab` | moi truong luyen NoSQLi |
| Root Me NoSQL auth/blind | luyen bypass va blind extraction |
| Burp NoSQLiScanner repo | tham khao logic detection |

## Pitfall khi automate

| Pitfall | He qua |
|---------|--------|
| sai content-type | payload khong vao dung parser |
| khong escape regex | false positive/false negative |
| lockout/rate limit | oracle mat tinh on dinh |
| session het han | ket qua khong lap lai duoc |
| timing noise cao | ket luan sai |

## Quy tac

Chi automate khi ban co the giai thich ro:

- input di qua parser nao
- query shape bi doi o dau
- oracle nao dang duoc su dung
