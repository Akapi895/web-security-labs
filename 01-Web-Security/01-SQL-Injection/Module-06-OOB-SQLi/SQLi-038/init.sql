-- =====================================================
-- SQLi-038: Oracle OOB HTTP via UTL_HTTP
-- =====================================================

-- Connect to PDB
ALTER SESSION SET CONTAINER = XEPDB1;

-- Create user
CREATE USER app_user IDENTIFIED BY AppPass123;
GRANT CONNECT, RESOURCE TO app_user;
GRANT CREATE SESSION TO app_user;
GRANT UNLIMITED TABLESPACE TO app_user;

-- Grant UTL_HTTP access
GRANT EXECUTE ON UTL_HTTP TO app_user;
GRANT EXECUTE ON UTL_INADDR TO app_user;
GRANT EXECUTE ON HTTPURITYPE TO app_user;

-- Create ACL for outbound HTTP (Oracle 11g+)
BEGIN
  DBMS_NETWORK_ACL_ADMIN.CREATE_ACL(
    acl => 'outbound_http.xml',
    description => 'Allow outbound HTTP',
    principal => 'APP_USER',
    is_grant => TRUE,
    privilege => 'connect'
  );
  DBMS_NETWORK_ACL_ADMIN.ADD_PRIVILEGE(
    acl => 'outbound_http.xml',
    principal => 'APP_USER',
    is_grant => TRUE,
    privilege => 'resolve'
  );
  DBMS_NETWORK_ACL_ADMIN.ASSIGN_ACL(
    acl => 'outbound_http.xml',
    host => '*',
    lower_port => 80,
    upper_port => 443
  );
  COMMIT;
END;
/

-- Create tables as app_user
ALTER SESSION SET CURRENT_SCHEMA = app_user;

CREATE TABLE customers (
    id NUMBER PRIMARY KEY,
    name VARCHAR2(100),
    email VARCHAR2(100),
    tier VARCHAR2(20)
);

CREATE TABLE admin_creds (
    id NUMBER PRIMARY KEY,
    username VARCHAR2(50),
    password VARCHAR2(100)
);

CREATE TABLE flags (
    id NUMBER PRIMARY KEY,
    name VARCHAR2(50),
    value VARCHAR2(100)
);

INSERT INTO customers VALUES (1, 'Acme Corp', 'contact@acme.com', 'Enterprise');
INSERT INTO customers VALUES (2, 'TechStart Inc', 'info@techstart.io', 'Startup');
INSERT INTO customers VALUES (3, 'Global Industries', 'sales@global.com', 'Enterprise');

INSERT INTO admin_creds VALUES (1, 'ora_admin', 'Or@cl3_Adm1n!');
INSERT INTO admin_creds VALUES (2, 'dba_user', 'DBA_S3cur3_2024');

INSERT INTO flags VALUES (1, 'sqli_038', 'FLAG{oracle_utl_http_oob}');

COMMIT;
/
