-- Connect to XEPDB1 and create tables for app_user
ALTER SESSION SET CONTAINER = XEPDB1;

-- Create tables in app_user schema
CREATE TABLE app_user.exports (
    id NUMBER PRIMARY KEY, 
    name VARCHAR2(100), 
    data CLOB
);

INSERT INTO app_user.exports VALUES (1, 'Export 1', 'Data set 1...');
INSERT INTO app_user.exports VALUES (2, 'Export 2', 'Data set 2...');

CREATE TABLE app_user.secrets (
    id NUMBER PRIMARY KEY, 
    name VARCHAR2(100), 
    value VARCHAR2(255)
);

INSERT INTO app_user.secrets VALUES (1, 'sqli_016', 'FLAG{xmltyp3_0r4cl3_3xtr4ct}');

COMMIT;

-- Grant necessary privileges
GRANT SELECT ON app_user.exports TO app_user;
GRANT SELECT ON app_user.secrets TO app_user;
