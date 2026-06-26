# NoSQL Injection (NoSQLi) - Bao Cao Tong Hop

## 1. NoSQLi la gi va ban chat ky thuat

NoSQLi xay ra khi input do nguoi dung kiem soat khong con duoc xu ly nhu du lieu thuong, ma duoc dien giai thanh mot phan cua cau truy van NoSQL.

Khac voi SQLi, diem vo ranh gioi code/data trong NoSQLi thuong nam o:

- query object
- key operator nhu `$ne`, `$gt`, `$regex`, `$where`
- JSON/BSON structure
- JavaScript expression
- aggregation pipeline

Neu tom gon trong 1 cau:

- SQLi la loi de input doi nghia cau lenh SQL.
- NoSQLi la loi de input doi nghia cau truc va logic cua query object.

## 2. Ban chat cua he NoSQL va tai sao no tao ra attack surface rieng

NoSQL khong phai mot ngon ngu truy van duy nhat. Day la nhom he co so du lieu gom:

- document-based
- key-value
- wide-column
- graph

Trong thuc te web pentest, NoSQLi co y nghia ro nhat voi he document-based, dac biet la MongoDB-style query.

Ung dung thuong tuong tac voi NoSQL theo chuoi:

1. nhan input qua URL/form/JSON/GraphQL
2. parser bien input thanh object
3. code build selector/filter/pipeline
4. driver serialize object
5. database thuc thi operators va dieu kien

Loi xuat hien khi input di tu "value" thanh "query instruction".

## 3. Khac biet cot loi giua NoSQLi va SQLi

SQLi:

- tap trung vao chuoi SQL
- thuong break quote, noi them menh de, dung comment
- khai thac xoay quanh parser SQL

NoSQLi:

- tap trung vao object shape va operator semantics
- co the khong can break quote
- thuong khai thac qua nested object, parser bracket notation, regex, `$where`, pipeline
- co the xay ra tai application layer, framework layer, hoac database layer

Vi vay, khi test NoSQLi, cau hoi dung khong phai:

- "Co thoat khoi chuoi SQL duoc khong?"

Ma la:

- "Input cua minh co dang bi hieu thanh mot phan cua query structure hay khong?"

## 4. Nguyen nhan goc re

NoSQLi khong phai do ky tu dac biet don le. Nguyen nhan goc la mat quyen kiem soat query grammar.

### 4.1 Cac pattern ky thuat gay ra NoSQLi

- Noi chuoi de tao `$where` hoac raw JSON query
- Dung truc tiep `req.body`, `req.query`, `args.filter` lam selector
- Merge object do nguoi dung kiem soat vao base filter
- Parse lai JSON/YAML tu input va tin tuong ket qua
- Khong validate kieu du lieu scalar/object/array
- Cho phep key bat dau bang `$`
- Tin vao duplicate key, repeated parameter, hoac stored filter
- De authentication phu thuoc toan bo vao selector database

### 4.2 Cac dieu kien ho tro khai thac

- Parser bien input thanh nested object
- Response co oracle ro rang (redirect, content diff, error, delay)
- Ung dung lo error hoac co `$where` / `aggregate()` / regex path

## 5. Cach phan loai NoSQLi de tu duy dung

### 5.1 Syntax injection

Xay ra khi input pha vo stringified query hoac JavaScript expression.

Tu duy:

- break context
- chen them boolean logic
- truncate trailing condition bang null byte neu co

### 5.2 Operator injection

Xay ra khi input duoc parser thanh object chua operators.

Vi du:

- `password[$ne]=x`
- `{"password":{"$regex":"^a"}}`

Day la dang NoSQLi pho bien nhat.

### 5.3 Authentication bypass

Dang tac dong thuong gap nhat.

Khi login dung:

- `findOne({username:req.body.username, password:req.body.password})`

thi chi can bien password thanh operator object la co the log in ma khong can mat khau dung.

### 5.4 Blind extraction

Dung `$regex` hoac boolean behavior de rut thong tin tung ky tu.

### 5.5 JavaScript-enabled injection

Khi reach duoc `$where`, `mapReduce()` hoac query path nguy hiem cua framework, input co the anh huong den execution logic thay vi chi selector logic.

### 5.6 Aggregation pipeline abuse

Neu endpoint dung `aggregate()` va nhan pipeline tu client, attacker co the chen stage nhu `$lookup` de doc collection khac.

## 6. Quy trinh khai thac theo he thong

1. Quan sat hanh vi ung dung va doan query shape.
2. Xac dinh injection point: scalar field, nested object, string expression, pipeline.
3. Test syntax probes va operator probes.
4. Xac nhan oracle true/false hoac delay.
5. Dung payload phu hop de override selector logic.
6. Bypass auth hoac mo rong result set.
7. Neu can, chuyen sang blind extraction, JS injection hoac aggregation abuse.

Ban chat cua quy trinh nay la:

- detect parser behavior
- model query transformation
- exploit theo dung execution flow

## 7. Workflow khai thac kinh dien

### 7.1 Auth bypass

Dung khi endpoint login/session tra redirect hoac cookie ro rang.

Huong di:

- broad match de confirm
- targeted match de vao admin
- regex de suy ra password neu can

### 7.2 Blind extraction

Huong di:

1. chon target user
2. test regex support
3. tim do dai bang `.{n}`
4. enumerate prefix bang `^a`, `^ad`, `^adm`

### 7.3 JS injection

Huong di:

- test `$where`
- dung `this.field` de probe schema
- dung timing neu khong co content diff
- dung error-based neu app leak error

### 7.4 Pipeline abuse

Huong di:

- prove endpoint dung `aggregate()`
- mo rong `$match`
- pivot collection bang `$lookup`
- reshape output de lo data gia tri cao

## 8. Vi sao filter thong thuong van that bai

NoSQLi thuong bypass filter khong phai bang "keyword obfuscation" kieu SQLi, ma bang:

- doi content type
- bracket notation
- nested object
- duplicate key
- repeated parameter
- null byte
- nested operator hiding

Neu code van cho input quyet dinh query shape, bypass chi la van de parser va context.

## 9. Dac thu quan trong can nho khi pentest

- Broad bypass co the log in vao sai user, nen can target bang `$eq` hoac `$in`
- Regex extraction can xu ly escaping va metacharacters
- Timing test de bi nhieu boi network, rate limit, retry
- Write paths nguy hiem hon read paths vi selector bypass co the mo rong `updateMany()` / `deleteMany()`
- GraphQL khong tu dong an toan neu resolver forward `filter` truc tiep

## 10. Tu duy dung cho lab va agent training

Lab NoSQLi tot nen day 4 lop:

1. parser behavior
2. query-shape reasoning
3. exploitation oracle
4. defensive fix map truc tiep ve root cause

Nhung pattern lab gia tri cao:

- login form urlencoded de operator injection
- search endpoint voi `$where` de syntax injection
- blind regex extraction
- timing-based JS injection
- aggregation pivot bang `$lookup`
- second-order stored filter

## 11. Khac phuc dung ban chat

Phong thu dung voi NoSQLi la:

- server phai giu quyen so huu query grammar

Co nghia:

1. Khong dung truc tiep object tu client lam filter.
2. Reject/strip recursively moi key bat dau bang `$` neu khong co allow-list ro rang.
3. Validate schema va type ngay tai boundary.
4. Khong de auth dua hoan toan vao selector do client dinh hinh.
5. Tranh `$where`, JavaScript query path, pipeline do client tu xay.
6. Giam lo error va ap least privilege.

## 12. Ket luan

NoSQLi la loi "thiet ke cach ung dung noi chuyen voi query object", khong chi la loi ky tu dac biet.

Neu can nho 2 cau:

- Khi input co the doi hinh dang query, NoSQLi xuat hien.
- Khi server giu quyen kiem soat operators, field names, expression va pipeline, NoSQLi bi cat o goc.
