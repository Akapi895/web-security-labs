# SQL Injection Defense and Mitigation

## Primary Defenses

### 1. Parameterized Queries (Prepared Statements)

The most effective defense. Separates SQL code from data.

#### Java (JDBC)

```java
// VULNERABLE
String query = "SELECT * FROM users WHERE username = '" + username + "'";
Statement stmt = connection.createStatement();
ResultSet rs = stmt.executeQuery(query);

// SAFE
String query = "SELECT * FROM users WHERE username = ?";
PreparedStatement pstmt = connection.prepareStatement(query);
pstmt.setString(1, username);
ResultSet rs = pstmt.executeQuery();
```

#### Python (psycopg2 - PostgreSQL)

```python
# VULNERABLE
cursor.execute("SELECT * FROM users WHERE username = '%s'" % username)

# SAFE
cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
```

#### Python (SQLAlchemy)

```python
# SAFE - using ORM
user = session.query(User).filter(User.username == username).first()

# SAFE - using text with bind
from sqlalchemy import text
result = connection.execute(text("SELECT * FROM users WHERE username = :name"), {"name": username})
```

#### PHP (PDO)

```php
// VULNERABLE
$query = "SELECT * FROM users WHERE username = '" . $_GET['username'] . "'";
$result = $pdo->query($query);

// SAFE
$stmt = $pdo->prepare("SELECT * FROM users WHERE username = ?");
$stmt->execute([$_GET['username']]);
```

#### PHP (MySQLi)

```php
// SAFE
$stmt = $mysqli->prepare("SELECT * FROM users WHERE username = ?");
$stmt->bind_param("s", $username);
$stmt->execute();
```

#### Node.js (mysql2)

```javascript
// VULNERABLE
connection.query(`SELECT * FROM users WHERE username = '${username}'`);

// SAFE
connection.execute('SELECT * FROM users WHERE username = ?', [username]);
```

#### C# (.NET)

```csharp
// VULNERABLE
string query = "SELECT * FROM users WHERE username = '" + username + "'";
SqlCommand cmd = new SqlCommand(query, connection);

// SAFE
string query = "SELECT * FROM users WHERE username = @username";
SqlCommand cmd = new SqlCommand(query, connection);
cmd.Parameters.AddWithValue("@username", username);
```

#### Ruby (ActiveRecord)

```ruby
# VULNERABLE
User.where("username = '#{params[:username]}'")

# SAFE
User.where(username: params[:username])
User.where("username = ?", params[:username])
```

### 2. Stored Procedures (Safe Implementation)

Must be implemented without dynamic SQL inside.

```sql
-- SAFE stored procedure
CREATE PROCEDURE GetUser(@username VARCHAR(50))
AS
BEGIN
    SELECT * FROM users WHERE username = @username
END

-- VULNERABLE stored procedure (uses dynamic SQL)
CREATE PROCEDURE GetUser(@username VARCHAR(50))
AS
BEGIN
    EXEC('SELECT * FROM users WHERE username = ''' + @username + '''')
END
```

### 3. Allow-list Input Validation

For dynamic elements that cannot be parameterized (table/column names):

```java
// Validate table name against allowlist
String tableName;
switch(userInput) {
    case "users": tableName = "users"; break;
    case "products": tableName = "products"; break;
    default: throw new IllegalArgumentException("Invalid table");
}
String query = "SELECT * FROM " + tableName;
```

## Additional Defenses

### Input Validation

- Validate data type, length, format
- Reject unexpected characters
- Use strict regex patterns

```python
import re

def validate_username(username):
    if not re.match(r'^[a-zA-Z0-9_]{3,20}$', username):
        raise ValueError("Invalid username format")
    return username
```

### Escaping (Last Resort)

Only if parameterization not possible. Database-specific:

```python
# MySQL
import mysql.connector
escaped = mysql.connector.conversion.MySQLConverter().escape(user_input)

# PostgreSQL
from psycopg2.extensions import adapt
escaped = adapt(user_input).getquoted()
```

### Least Privilege

- Use separate DB accounts per application
- Grant minimum required permissions
- No admin/DBA access for web applications

```sql
-- Create limited user
CREATE USER 'webapp'@'localhost' IDENTIFIED BY 'password';
GRANT SELECT, INSERT, UPDATE ON app_db.* TO 'webapp'@'localhost';
-- DO NOT: GRANT ALL PRIVILEGES
```

### WAF (Web Application Firewall)

Provides additional layer but not primary defense:

- ModSecurity with OWASP CRS
- AWS WAF, Cloudflare, Imperva
- Detect and block common SQLi patterns

### Error Handling

Never expose database errors to users:

```python
try:
    cursor.execute(query)
except Exception as e:
    # Log detailed error internally
    logger.error(f"Database error: {e}")
    # Show generic message to user
    return "An error occurred. Please try again."
```

## Defense Checklist

| Control | Priority | Status |
|---------|----------|--------|
| Parameterized queries everywhere | Critical | |
| Input validation | High | |
| Least privilege DB accounts | High | |
| Generic error messages | High | |
| WAF rules | Medium | |
| Regular security testing | Medium | |
| Code review for SQL queries | High | |

## ORM Considerations

ORMs help but don't guarantee safety:

```python
# SAFE - ORM handles escaping
User.objects.filter(username=username)

# VULNERABLE - raw query
User.objects.raw(f"SELECT * FROM users WHERE username = '{username}'")

# SAFE - raw query with params
User.objects.raw("SELECT * FROM users WHERE username = %s", [username])
```

## Framework-Specific Guides

| Framework | Safe Pattern |
|-----------|--------------|
| Django | Use ORM, `params` in `raw()` |
| Rails | Use ActiveRecord, parameterized `where` |
| Spring | Use JPA/Hibernate, `@Param` bindings |
| Express | Use query builders, parameterized queries |
| Laravel | Use Eloquent, query bindings |

## Testing for SQLi

Regular security testing should include:

1. Automated DAST scanning (Burp, OWASP ZAP)
2. Manual penetration testing
3. Code review for SQL queries
4. SAST tools (Semgrep, CodeQL)

## Common Mistakes

| Mistake | Problem | Solution |
|---------|---------|----------|
| String concatenation | Direct injection | Use parameterized queries |
| Escaping as primary defense | Can be bypassed | Use parameterization |
| Trust stored data | Second-order injection | Validate all data |
| Dynamic table/column | Cannot parameterize | Allow-list validation |
| Error messages exposed | Information leakage | Generic errors |

## Security Headers

While not SQLi-specific, these help overall security:

```
Content-Security-Policy: default-src 'self'
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
```

## Summary

1. **Always use parameterized queries** - primary defense
2. **Validate all input** - secondary defense
3. **Apply least privilege** - limit damage
4. **Hide error details** - prevent information leakage
5. **Test regularly** - catch regressions
