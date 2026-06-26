# Tong Quan NoSQL Injection

## Dinh nghia

`NoSQL Injection` (NoSQLi) xay ra khi input khong tin cay lam thay doi **cau truc**, **logic** hoac **luong thuc thi** cua truy van NoSQL.

Thay vi duoc xu ly nhu du lieu thuan, input cua attacker co the bi dien giai thanh:

- cu phap truy van
- query operator nhu `$ne`, `$gt`, `$regex`, `$in`, `$where`
- JavaScript expression hoac stage trong `aggregation pipeline`

Trong web pentest, phan lon case NoSQLi tap trung vao he document-based (dac biet la MongoDB-style query), nen bo tai lieu nay uu tien model nay.

## "NoSQL" khong phai mot ngon ngu duy nhat

NoSQL la mot nhom model CSDL khac nhau:

| Model | Cau truc du lieu thuong gap | Cach query | Muc do lien quan den NoSQLi |
|------|------------------------------|------------|-----------------------------|
| Document-based | JSON/BSON document | query object, operator, pipeline | Cao nhat |
| Key-value | key/value | lookup theo key, API rieng | Co the bi loi neu input dinh hinh command |
| Wide-column | column family | API/DSL filter | Phu thuoc implementation |
| Graph | node/edge | graph query language | Thuong tro thanh query-language injection |

## Ung dung tuong tac voi NoSQL nhu the nao

Ung dung hiem khi gui chuoi SQL thuan. Thay vao do thuong tao:

- query object
- JSON/BSON payload
- filter/selector
- aggregation pipeline
- clause co kha nang evaluate expression nhu `$where`

Luong thong thuong:

```text
HTTP request
  -> parser (query string, form, JSON, GraphQL)
  -> code ung dung build filter/selector/pipeline
  -> database driver serialize object
  -> NoSQL engine evaluate operator va dieu kien
```

NoSQLi xay ra khi input vuot ranh gioi "value" de tro thanh "query instruction".

## Khac biet cot loi giua SQLi va NoSQLi

| Khia canh | SQL Injection | NoSQL Injection |
|----------|---------------|-----------------|
| Muc tieu chinh | chuoi SQL | query object, operator key, JSON/BSON structure, expression |
| Parser boundary | SQL parser trong DBMS | parser o app/framework/driver va co the ca DB engine |
| Kieu abuse pho bien | break/noi chuoi SQL | chen operator, doi shape object, chen JS, abuse pipeline |
| Gia dinh schema | relational co dinh | thuong semi-structured |
| Vi du payload | `' OR 1=1--` | `{"password":{"$regex":"^a"}}`, `username[$ne]=x` |

## Tac dong

| Tac dong | Mo ta |
|---------|------|
| Authentication bypass | Dang nhap khong can credential hop le |
| Authorization bypass | Loai bo dieu kien nhu `role=user`, `released=1` |
| Data disclosure | Doc du lieu nhay cam |
| Data manipulation | Mo rong selector update/delete |
| Denial of service | Trigger regex nang, loop, broad scan |
| Execution path abuse | Trong context co JS evaluation, input co the tac dong manh hon selector |

## Phan loai ky thuat

| Loai | Mo ta ngan |
|------|-----------|
| Syntax injection | Pha vo stringified query/expression de chen logic |
| Operator injection | Chen query operator vao object |
| Authentication bypass | Loi dung selector de `findOne()` match sai |
| Blind extraction | Suy dien du lieu qua true/false, length, timing |
| JavaScript injection | Abuse `$where`, mapReduce() hoac query path co evaluate |
| Aggregation abuse | Chen stage nhu `$lookup` de pivot collection |
| Error/Time-based | Rut du lieu qua loi hoac do tre co dieu kien |

## Phan loai theo injection point

| Vi tri | Vi du |
|-------|------|
| URL parameter | `?username[$ne]=x` |
| Form-urlencoded | `password[$regex]=^adm` |
| JSON body | `{"password":{"$gt":""}}` |
| GraphQL filter input | `{"filter":{"$ne":{}}}` |
| Header/Cookie | gia tri JSON duoc deserialize |
| Stored input | filter da luu va duoc tai su dung |

## Operator MongoDB thuong gap

| Operator | Y nghia | Kieu abuse |
|----------|--------|------------|
| `$eq` | bang | target account cu the |
| `$ne` | khac | match rat rong |
| `$gt` / `$lt` | lon hon / nho hon | mo rong range |
| `$in` / `$nin` | nam trong / khong nam trong | target username kha nghi |
| `$exists` | ton tai field | do schema |
| `$regex` | regex match | blind extraction |
| `$where` | JS expression | boolean/timing/error-based |

## Attack workflow

```text
1. DETECT      -> tim noi input vao query construction
2. MAP         -> xac dinh parser, content-type, query shape
3. HYPOTHESIZE -> mo hinh hoa cach payload anh huong logic
4. OVERRIDE    -> doi selector bang syntax/operator injection
5. EXTRACT     -> bypass auth, enum field, lay data
6. ESCALATE    -> abuse JS/pipeline neu co
7. HARDEN      -> dua query grammar ve server ownership
```

## Mental model can nho

Voi SQLi, cau hoi thuong la:

"co break khoi SQL string duoc khong?"

Voi NoSQLi, cau hoi dung la:

"input cua minh co bi he thong hieu thanh mot phan cua query structure khong?"

Query structure o day co the la:

- object key
- operator
- regex pattern
- JS clause
- pipeline stage

## File lien quan

- [Detection](01-detection.md)
- [Query Construction and Root Causes](02-query-construction-root-causes.md)
- [Syntax Injection](03-syntax-injection.md)
- [Operator Injection](04-operator-injection.md)
- [Authentication Bypass](05-authentication-bypass.md)
- [Blind Extraction](06-blind-extraction.md)
- [JavaScript Injection](07-javascript-injection.md)
- [Aggregation Pipeline Abuse](08-aggregation-pipeline-abuse.md)
- [Filter Bypass](09-filter-bypass.md)
- [Automation Tools](10-automation-tools.md)
- [Lab Design Patterns](11-lab-design-patterns.md)
- [Defense and Mitigation](12-defense-mitigation.md)
