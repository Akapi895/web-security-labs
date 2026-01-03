-- This script runs as SYSTEM in XEPDB1
-- Create user if not exists (the image may create it automatically)

DECLARE
  user_count NUMBER;
BEGIN
  SELECT COUNT(*) INTO user_count FROM dba_users WHERE username = 'APP_USER';
  IF user_count = 0 THEN
    EXECUTE IMMEDIATE 'CREATE USER app_user IDENTIFIED BY app_password';
    EXECUTE IMMEDIATE 'GRANT CONNECT, RESOURCE TO app_user';
    EXECUTE IMMEDIATE 'GRANT UNLIMITED TABLESPACE TO app_user';
  END IF;
END;
/

-- Create tables in app_user schema
CREATE TABLE app_user.customers (
    id NUMBER PRIMARY KEY,
    name VARCHAR2 (100),
    email VARCHAR2 (100),
    tier VARCHAR2 (20)
);

CREATE TABLE app_user.secrets (
    id NUMBER PRIMARY KEY,
    name VARCHAR2 (100),
    value VARCHAR2 (255)
);

-- Insert data
INSERT INTO
    app_user.customers
VALUES (
        1,
        'Alice Corp',
        'alice@example.com',
        'Gold'
    );

INSERT INTO
    app_user.customers
VALUES (
        2,
        'Bob Inc',
        'bob@example.com',
        'Silver'
    );

INSERT INTO
    app_user.secrets
VALUES (
        1,
        'sqli_014',
        'FLAG{0r4cl3_utl_1n4ddr_3rr0r}'
    );

COMMIT;