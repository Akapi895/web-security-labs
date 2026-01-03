# SQL Injection Lab Roadmap

## 📋 Tổng Quan

Lab Roadmap này được thiết kế dựa trên kiến thức từ Knowledge Base, bao gồm tất cả các kỹ thuật SQLi từ cơ bản đến nâng cao với đa dạng kịch bản và DBMS.

### Thống kê Lab

| Category                   | Số lượng Lab |
| -------------------------- | ------------ |
| Detection & Fingerprinting | 8            |
| Error-based SQLi           | 10           |
| Union-based SQLi           | 4            |
| Boolean Blind SQLi         | 6            |
| Time-based Blind SQLi      | 6            |
| Out-of-Band (OOB) SQLi     | 8            |
| Filter Bypass              | 10           |
| DBMS-Specific Exploitation | 12           |
| Second-Order SQLi          | 4            |
| Data Targeting             | 5            |
| **Tổng cộng**              | **73 Labs**  |

### DBMS Coverage

Các lab sẽ luân phiên sử dụng 5 loại DBMS:

- 🐬 **MySQL/MariaDB** - DBMS phổ biến nhất
- 🐘 **PostgreSQL** - Advanced features
- 🔷 **MSSQL** - Stacked queries, xp_cmdshell
- 🏛️ **Oracle** - FROM dual, ROWNUM
- 📦 **SQLite** - File-based, embedded

---

## 🔍 Module 1: Detection & Fingerprinting

> **Mục tiêu**: Học cách phát hiện lỗ hổng SQLi và xác định loại DBMS

| Lab ID   | Sub-Topic      | DBMS       | Scenario/Context                   | Learning Objective                                                  | Complexity      |
| -------- | -------------- | ---------- | ---------------------------------- | ------------------------------------------------------------------- | --------------- | ----------------- | --------------- |
| SQLi-001 | Detection      | MySQL      | Chức năng Search sản phẩm          | Phát hiện SQLi bằng quote-based test (`'`, `"`)                     | ⭐ Dễ           |
| SQLi-002 | Detection      | PostgreSQL | Chức năng Filter theo Category     | Phát hiện SQLi bằng logic test (`OR 1=1`, `AND 1=2`)                | ⭐ Dễ           |
| SQLi-003 | Detection      | MSSQL      | Trang View Profile                 | Phát hiện SQLi bằng arithmetic test (`1/0`, `1/1`)                  | ⭐ Dễ           |
| SQLi-004 | Detection      | Oracle     | API lấy thông tin sản phẩm theo ID | Phát hiện SQLi bằng comment test (`--`, `#`, `/**/`)                | ⭐ Dễ           |
| SQLi-005 | Fingerprinting | MySQL      | Search box với error messages      | Xác định DBMS qua error message patterns                            | ⭐⭐ Trung bình |
| SQLi-006 | Fingerprinting | PostgreSQL | Login form với verbose errors      | Xác định DBMS qua version queries (`@@version`, `version()`)        | ⭐⭐ Trung bình |
| SQLi-007 | Fingerprinting | MSSQL      | REST API endpoint                  | Xác định DBMS qua time-based (`SLEEP`, `WAITFOR DELAY`, `pg_sleep`) | ⭐⭐ Trung bình |
| SQLi-008 | Fingerprinting | Oracle     | Web service với XML input          | Xác định DBMS qua string concatenation (`                           |                 | `, `+`, `CONCAT`) | ⭐⭐ Trung bình |

---

## 💥 Module 2: Error-based SQL Injection

> **Mục tiêu**: Khai thác thông tin qua error messages của database

| Lab ID       | Sub-Topic       | DBMS       | Scenario/Context             | Learning Objective                          | Complexity      |
| ------------ | --------------- | ---------- | ---------------------------- | ------------------------------------------- | --------------- |
| SQLi-009     | Error-based     | MySQL      | Product detail page (`?id=`) | Khai thác EXTRACTVALUE() để lấy version     | ⭐ Dễ           |
| SQLi-010     | Error-based     | MySQL      | User profile endpoint        | Khai thác UPDATEXML() để enumerate tables   | ⭐⭐ Trung bình |
| SQLi-011     | Error-based     | MySQL      | Blog article view            | Double Query technique (FLOOR + RAND)       | ⭐⭐⭐ Khó      |
| SQLi-012     | Error-based     | MSSQL      | Corporate directory search   | CONVERT/CAST error extraction               | ⭐ Dễ           |
| SQLi-013     | Error-based     | MSSQL      | Employee lookup API          | XML PATH error extraction cho multiple rows | ⭐⭐ Trung bình |
| SQLi-014     | Error-based     | Oracle     | Customer portal query        | UTL_INADDR.GET_HOST_NAME error extraction   | ⭐⭐ Trung bình |
| SQLi-015     | Error-based     | Oracle     | Report generator             | CTXSYS.DRITHSX.SN extraction                | ⭐⭐⭐ Khó      |
| ~~SQLi-016~~ | ~~Error-based~~ | ~~Oracle~~ | ~~Data export feature~~      | ~~XMLType error-based extraction~~          | ❌ **LỖI**      |
| SQLi-017     | Error-based     | PostgreSQL | Search filter                | CAST to numeric extraction                  | ⭐ Dễ           |
| SQLi-018     | Error-based     | PostgreSQL | Analytics dashboard          | CHR() concatenation error extraction        | ⭐⭐ Trung bình |

---

## 🔗 Module 3: Union-based SQL Injection

> **Mục tiêu**: Sử dụng UNION SELECT để ghép kết quả và lấy dữ liệu
>
> **Lưu ý:** Module này tập trung vào **advanced techniques** vì bạn đã nắm được basic union concepts từ Module 1 & 2.

| Lab ID   | Sub-Topic             | DBMS       | Scenario/Context                    | Learning Objective                                    | Complexity      |
| -------- | --------------------- | ---------- | ----------------------------------- | ----------------------------------------------------- | --------------- |
| SQLi-019 | Union - Single Column | MySQL      | Search results (1 column displayed) | CONCAT/CONCAT_WS để ghép nhiều giá trị trong 1 column | ⭐⭐ Trung bình |
| SQLi-020 | Union - Single Column | Oracle     | Invoice lookup                      | Concatenation với `\|\|` operator, FROM dual          | ⭐⭐ Trung bình |
| SQLi-021 | Union - Multi Row     | MySQL      | Comments section                    | GROUP_CONCAT() để aggregate nhiều rows                | ⭐⭐ Trung bình |
| SQLi-022 | Union - Multi Row     | PostgreSQL | User listing                        | STRING_AGG() aggregation technique                    | ⭐⭐⭐ Khó      |

---

## 🔮 Module 4: Boolean-based Blind SQL Injection

> **Mục tiêu**: Khai thác SQLi khi không có output trực tiếp, chỉ có true/false response
>
> **Lưu ý:** Module này tập trung vào **diverse injection points** vì basic boolean blind đã được cover ở Module 1.

### Sub-module 4.1: Core Boolean Techniques

| Lab ID   | Sub-Topic     | DBMS       | Scenario/Context    | Learning Objective                                | Complexity      |
| -------- | ------------- | ---------- | ------------------- | ------------------------------------------------- | --------------- |
| SQLi-023 | Boolean Blind | PostgreSQL | Username validation | Extract data character-by-character với SUBSTRING | ⭐⭐ Trung bình |
| SQLi-024 | Boolean Blind | Oracle     | Session validation  | SUBSTR() và ROWNUM pagination                     | ⭐⭐ Trung bình |

### Sub-module 4.2: Advanced Injection Points

| Lab ID   | Sub-Topic     | DBMS       | Scenario/Context   | Injection Point                 | Learning Objective              | Complexity      |
| -------- | ------------- | ---------- | ------------------ | ------------------------------- | ------------------------------- | --------------- |
| SQLi-025 | Boolean Blind | MySQL      | Analytics tracking | **Cookie** (`tracking_id`)      | Blind SQLi qua Cookie header    | ⭐⭐ Trung bình |
| SQLi-026 | Boolean Blind | PostgreSQL | REST API           | **JSON body** (`{"id": "..."}`) | Blind SQLi trong JSON payload   | ⭐⭐ Trung bình |
| SQLi-027 | Boolean Blind | MySQL      | Product sorting    | **ORDER BY** clause             | Blind SQLi trong ORDER BY       | ⭐⭐⭐ Khó      |
| SQLi-028 | Boolean Blind | MSSQL      | Data export        | **Column name** parameter       | Blind SQLi trong dynamic column | ⭐⭐⭐ Khó      |

---

## ⏱️ Module 5: Time-based Blind SQL Injection

> **Mục tiêu**: Khai thác SQLi bằng cách quan sát response time delay
>
> **Lưu ý:** Focus vào **advanced scenarios** vì basic time-based tương tự Boolean Blind.

### Sub-module 5.1: Core Time-based Techniques (Per DBMS)

| Lab ID   | Sub-Topic  | DBMS       | Scenario/Context   | Learning Objective          | Complexity |
| -------- | ---------- | ---------- | ------------------ | --------------------------- | ---------- |
| SQLi-029 | Time-based | MySQL      | Heavy traffic site | BENCHMARK() alternative     | ⭐⭐⭐ Khó |
| SQLi-030 | Time-based | MSSQL      | Email validation   | WAITFOR DELAY (no stacked)  | ⭐⭐⭐ Khó |
| SQLi-031 | Time-based | PostgreSQL | Rate limited API   | GENERATE_SERIES heavy query | ⭐⭐⭐ Khó |
| SQLi-032 | Time-based | Oracle     | Restricted env     | Heavy query join technique  | ⭐⭐⭐ Khó |

### Sub-module 5.2: Advanced Injection Points

| Lab ID   | Sub-Topic  | DBMS       | Scenario/Context   | Injection Point | Complexity      |
| -------- | ---------- | ---------- | ------------------ | --------------- | --------------- |
| SQLi-033 | Time-based | MySQL      | Session management | **Cookie**      | ⭐⭐ Trung bình |
| SQLi-034 | Time-based | PostgreSQL | Bot detection      | **User-Agent**  | ⭐⭐⭐ Khó      |

---

## 🌐 Module 6: Out-of-Band (OOB) SQL Injection

> **Mục tiêu**: Exfiltrate data qua DNS hoặc HTTP requests

| Lab ID   | Sub-Topic  | DBMS       | Scenario/Context      | Learning Objective                      | Complexity      |
| -------- | ---------- | ---------- | --------------------- | --------------------------------------- | --------------- |
| SQLi-057 | OOB - DNS  | MySQL      | Windows server app    | LOAD_FILE() với UNC path để trigger DNS | ⭐⭐⭐ Khó      |
| SQLi-058 | OOB - DNS  | MSSQL      | Corporate intranet    | xp_dirtree DNS exfiltration             | ⭐⭐ Trung bình |
| SQLi-059 | OOB - DNS  | MSSQL      | Windows domain env    | xp_fileexist/xp_subdirs DNS             | ⭐⭐ Trung bình |
| SQLi-060 | OOB - HTTP | Oracle     | Java-based webapp     | UTL_HTTP.REQUEST exfil                  | ⭐⭐⭐ Khó      |
| SQLi-061 | OOB - DNS  | Oracle     | ACL-restricted env    | UTL_INADDR DNS lookup                   | ⭐⭐⭐ Khó      |
| SQLi-062 | OOB - HTTP | Oracle     | Legacy system         | HTTPURITYPE exfiltration                | ⭐⭐⭐ Khó      |
| SQLi-063 | OOB - DNS  | PostgreSQL | Linux server          | COPY TO PROGRAM + nslookup              | ⭐⭐⭐ Khó      |
| SQLi-064 | OOB - HTTP | PostgreSQL | DbLink enabled server | dblink extension exfiltration           | ⭐⭐⭐ Khó      |

---

## 🛡️ Module 7: Filter Bypass Techniques

> **Mục tiêu**: Vượt qua WAF và input validation
>
> **Lưu ý:** Chọn lọc các **kỹ thuật bypass quan trọng nhất** để tránh lặp lại.

| Lab ID   | Sub-Topic | DBMS       | Scenario/Context | Filter Type               | Learning Objective                        | Complexity      |
| -------- | --------- | ---------- | ---------------- | ------------------------- | ----------------------------------------- | --------------- |
| SQLi-043 | Bypass    | MySQL      | WAF-protected    | Space filtered            | Bypass bằng `/**/`, `%09`, `%0a`          | ⭐⭐ Trung bình |
| SQLi-044 | Bypass    | PostgreSQL | Protected API    | Whitespace filtered       | Bypass bằng parentheses `(SELECT(x))`     | ⭐⭐ Trung bình |
| SQLi-045 | Bypass    | MySQL      | IDS-protected    | UNION filtered            | Case variation `Un/**/IoN`                | ⭐⭐ Trung bình |
| SQLi-046 | Bypass    | MySQL      | WAF environment  | SELECT filtered           | MySQL version comments `/*!50000SELECT*/` | ⭐⭐⭐ Khó      |
| SQLi-047 | Bypass    | MSSQL      | Enterprise WAF   | UNION SELECT filtered     | Double keyword `UNunionION SEselectLECT`  | ⭐⭐⭐ Khó      |
| SQLi-048 | Bypass    | MySQL      | Custom filter    | `--` comment filtered     | Bypass bằng `#`, `/**/`                   | ⭐⭐ Trung bình |
| SQLi-049 | Bypass    | MySQL      | URL validation   | Quote filtered            | Hex encoding `0x61646D696E`               | ⭐⭐ Trung bình |
| SQLi-050 | Bypass    | MSSQL      | Double decoding  | Standard encoding blocked | Double URL encoding `%2527`               | ⭐⭐⭐ Khó      |
| SQLi-051 | Bypass    | MySQL      | Strict filter    | AND/OR filtered           | Bypass bằng `&&`, `\|\|`                  | ⭐⭐ Trung bình |
| SQLi-052 | Bypass    | PostgreSQL | Comparison block | `=` filtered              | Bypass bằng LIKE, BETWEEN, IN             | ⭐⭐ Trung bình |

---

## 🗄️ Module 8: DBMS-Specific Exploitation

> **Mục tiêu**: Khai thác tính năng đặc thù của từng loại DBMS
>
> **Lưu ý:** Giữ nguyên vì tất cả đều là advanced techniques và unique cho từng DBMS.

### MySQL Specific

| Lab ID   | Sub-Topic       | DBMS  | Scenario/Context    | Learning Objective               | Complexity      |
| -------- | --------------- | ----- | ------------------- | -------------------------------- | --------------- |
| SQLi-053 | Stacked Queries | MySQL | Multi-query enabled | MySQL dengan múltiple statements | ⭐⭐ Trung bình |
| SQLi-054 | File Read       | MySQL | FILE privilege      | LOAD_FILE() để đọc file hệ thống | ⭐⭐⭐ Khó      |
| SQLi-055 | File Write      | MySQL | Write permission    | INTO OUTFILE webshell            | ⭐⭐⭐ Khó      |

### MSSQL Specific

| Lab ID   | Sub-Topic      | DBMS  | Scenario/Context | Learning Objective                  | Complexity |
| -------- | -------------- | ----- | ---------------- | ----------------------------------- | ---------- |
| SQLi-056 | xp_cmdshell    | MSSQL | SA privileges    | Enable và sử dụng xp_cmdshell       | ⭐⭐⭐ Khó |
| SQLi-057 | Linked Server  | MSSQL | Multi-server env | Lateral movement qua linked servers | ⭐⭐⭐ Khó |
| SQLi-058 | OLE Automation | MSSQL | Restricted env   | sp_OACreate command execution       | ⭐⭐⭐ Khó |

### Oracle Specific

| Lab ID   | Sub-Topic      | DBMS   | Scenario/Context | Learning Objective                   | Complexity |
| -------- | -------------- | ------ | ---------------- | ------------------------------------ | ---------- |
| SQLi-059 | Java Procedure | Oracle | Java enabled     | OS command via Java stored procedure | ⭐⭐⭐ Khó |
| SQLi-060 | DBMS_SCHEDULER | Oracle | Scheduler access | Command execution via DBMS_SCHEDULER | ⭐⭐⭐ Khó |
| SQLi-061 | DB Links       | Oracle | Multi-database   | Exploitation qua database links      | ⭐⭐⭐ Khó |

### PostgreSQL Specific

| Lab ID   | Sub-Topic       | DBMS       | Scenario/Context   | Learning Objective                      | Complexity |
| -------- | --------------- | ---------- | ------------------ | --------------------------------------- | ---------- |
| SQLi-062 | COPY TO PROGRAM | PostgreSQL | Superuser access   | OS command execution                    | ⭐⭐⭐ Khó |
| SQLi-063 | Large Objects   | PostgreSQL | File system access | File read/write via lo_import/lo_export | ⭐⭐⭐ Khó |
| SQLi-064 | Extensions      | PostgreSQL | dblink installed   | Exploitation via loaded extensions      | ⭐⭐⭐ Khó |

---

## 🔄 Module 9: Second-Order SQL Injection

> **Mục tiêu**: Khai thác khi payload được lưu và execute trong context khác
>
> **Lưu ý:** Giữ nguyên - đây là advanced technique hoàn toàn khác biệt với các module trước.

| Lab ID   | Sub-Topic    | DBMS       | Scenario/Context                    | Learning Objective                                      | Complexity |
| -------- | ------------ | ---------- | ----------------------------------- | ------------------------------------------------------- | ---------- |
| SQLi-065 | Second-Order | MySQL      | User registration → Profile display | Stored payload trong username, trigger khi view profile | ⭐⭐⭐ Khó |
| SQLi-066 | Second-Order | PostgreSQL | Password reset flow                 | Payload trong email, trigger khi reset                  | ⭐⭐⭐ Khó |
| SQLi-067 | Second-Order | MSSQL      | Order system                        | Payload trong order notes, trigger khi generate report  | ⭐⭐⭐ Khó |
| SQLi-068 | Second-Order | MySQL      | Multi-step form                     | Payload stored trong step 1, executed trong step 3      | ⭐⭐⭐ Khó |

---

## 🎯 Module 10: Data Targeting & Extraction

> **Mục tiêu**: Tối ưu hóa việc tìm kiếm và extract dữ liệu nhạy cảm
>
> **Lưu ý:** Giữ nguyên - đây là advanced optimization techniques cho real-world scenarios.

| Lab ID   | Sub-Topic            | DBMS       | Scenario/Context    | Learning Objective                                           | Complexity      |
| -------- | -------------------- | ---------- | ------------------- | ------------------------------------------------------------ | --------------- |
| SQLi-069 | Data Targeting       | MySQL      | E-commerce database | Keyword search cho sensitive columns (password, ssn, credit) | ⭐⭐ Trung bình |
| SQLi-070 | Data Targeting       | MSSQL      | Enterprise database | Non-default database discovery, encrypted DB detection       | ⭐⭐⭐ Khó      |
| SQLi-071 | Data Targeting       | Oracle     | Large database      | Owner/schema enumeration, column discovery                   | ⭐⭐ Trung bình |
| SQLi-072 | Regex Extraction     | MySQL      | Customer database   | Regex pattern matching cho credit cards, SSN                 | ⭐⭐⭐ Khó      |
| SQLi-073 | Optimized Extraction | PostgreSQL | High-value targets  | Quick wins: admin creds, API keys, session tokens            | ⭐⭐⭐ Khó      |

---

## 📊 Lab Organisation by Complexity

### ⭐ Dễ (6 Labs)

- SQLi-001 → SQLi-004: Detection basics
- SQLi-009, SQLi-012, SQLi-017: Basic Error-based

### ⭐⭐ Trung bình (30 Labs)

- SQLi-005 → SQLi-008: Fingerprinting
- SQLi-010, SQLi-013, SQLi-014, SQLi-018: Intermediate Error-based
- SQLi-019 → SQLi-021: Union techniques
- SQLi-023 → SQLi-028: Boolean/Time-based core + injection points
- SQLi-033, SQLi-043, SQLi-044, SQLi-048, SQLi-049, SQLi-051, SQLi-052: Filter Bypass
- SQLi-053: MySQL Stacked Queries
- SQLi-069, SQLi-071: Data Targeting

### ⭐⭐⭐ Khó (37 Labs)

- SQLi-011, SQLi-015: Advanced Error-based
- SQLi-022: Advanced Union (PostgreSQL STRING_AGG)
- SQLi-027, SQLi-028: Complex Boolean/Time-based injection points
- SQLi-029 → SQLi-034: Advanced Time-based per DBMS + injection points
- SQLi-035 → SQLi-042: OOB techniques (all)
- SQLi-045 → SQLi-047, SQLi-050: Advanced Filter Bypass
- SQLi-054 → SQLi-064: All DBMS-Specific exploitation
- SQLi-065 → SQLi-068: All Second-Order
- SQLi-070, SQLi-072, SQLi-073: Advanced Data Targeting

---

## 🗂️ DBMS Distribution

| DBMS       | Lab Count | Percentage |
| ---------- | --------- | ---------- |
| MySQL      | 24        | 33%        |
| PostgreSQL | 18        | 25%        |
| MSSQL      | 15        | 20%        |
| Oracle     | 16        | 22%        |

**Total: 73 Labs** (optimized từ 100 labs, loại bỏ basic repetitive exercises)

---

## 📚 Learning Path Đề Xuất

### Path 1: Beginner (1-2 tuần)

```
Week 1: Module 1 (Detection) → Module 2 (Error-based)
Week 2: Module 3 (Union advanced) → Review & Practice
```

### Path 2: Intermediate (2-3 tuần)

```
Week 1: Module 4 (Boolean Blind advanced injection points)
Week 2: Module 5 (Time-based advanced per DBMS)
Week 3: Module 6 (OOB) → Module 7 (Filter Bypass selection)
```

### Path 3: Advanced (2-3 tuần)

```
Week 1: Complete Module 7 (All Filter Bypass)
Week 2: Module 8 (DBMS-Specific exploitation)
Week 3: Module 9 (Second-Order) + Module 10 (Data Targeting)
```

**Total Timeline: 5-8 tuần** (tùy thuộc vào tốc độ học)

---

## 🛠️ Lab Structure (Suggested)

Mỗi lab folder nên có cấu trúc:

```
Module X
└── SQLi-XXX/
    ├── README.md           # Mô tả challenge, hints
    ├── docker-compose.yml  # Lab environment
    ├── src/                # Vulnerable application source
    │   ├── app.py         # (hoặc ngôn ngữ khác)
    │   └── ...
    ├── init.sql            # Database initialization
    ├── solution/           # (private)
    │   ├── writeup.md     # Solution walkthrough
    │   └── exploit.py     # Exploit script
    └── flag.txt            # Flag format: FLAG{...}
```

---

## 📋 Checklist Trước Khi Bắt Đầu

- [ ] Docker và Docker Compose đã cài đặt
- [ ] Burp Suite Community/Pro
- [ ] SQLMap
- [ ] Python 3.x với requests library
- [ ] Text editor (VSCode recommended)
- [ ] Kiến thức cơ bản về SQL và HTTP

---

## ⚠️ Lưu Ý Quan Trọng

> [!WARNING]
> Các lab này chỉ được sử dụng cho mục đích học tập trong môi trường **controlled và isolated**. Không được sử dụng các kỹ thuật này trên hệ thống thực mà không có sự cho phép rõ ràng.

> [!NOTE]
> Mỗi lab được thiết kế để dạy một kỹ thuật cụ thể. Hãy đảm bảo hiểu rõ kỹ thuật trước khi chuyển sang lab tiếp theo.

---

## 🔗 Tài Liệu Tham Khảo

- [Knowledge Base - SQL Injection](../../_knowledge_base/Web/SQLi/)
- [OWASP SQL Injection](https://owasp.org/www-community/attacks/SQL_Injection)
- [PortSwigger Web Security Academy](https://portswigger.net/web-security/sql-injection)
- [PayloadsAllTheThings - SQLi](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/SQL%20Injection)

---

_Last Updated: December 2025_
_Version: 1.0_
