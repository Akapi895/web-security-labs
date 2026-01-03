-- This script runs as SYSTEM user in FREEPDB1
-- Oracle Free includes Oracle Text by default

SET SERVEROUTPUT ON;

-- Create user if not exists
DECLARE
  user_count NUMBER;
BEGIN
  SELECT COUNT(*) INTO user_count FROM dba_users WHERE username = 'APP_USER';
  IF user_count = 0 THEN
    EXECUTE IMMEDIATE 'CREATE USER app_user IDENTIFIED BY app_password';
    EXECUTE IMMEDIATE 'GRANT CONNECT, RESOURCE TO app_user';
    EXECUTE IMMEDIATE 'GRANT UNLIMITED TABLESPACE TO app_user';
    DBMS_OUTPUT.PUT_LINE('[+] Created user app_user');
  ELSE
    DBMS_OUTPUT.PUT_LINE('[+] User app_user already exists');
  END IF;
END;
/

-- Grant SELECT on DBA views (for enumeration)
GRANT SELECT ON dba_objects TO app_user;

GRANT SELECT ON dba_users TO app_user;

-- Grant EXECUTE on CTXSYS packages for error-based exploitation
DECLARE
  obj_count NUMBER;
BEGIN
  SELECT COUNT(*) INTO obj_count 
  FROM dba_users 
  WHERE username = 'CTXSYS';
  
  IF obj_count > 0 THEN
    BEGIN
      SELECT COUNT(*) INTO obj_count
      FROM dba_objects 
      WHERE owner = 'CTXSYS' 
      AND object_name = 'DRITHSX'
      AND object_type = 'PACKAGE';
      
      IF obj_count > 0 THEN
        EXECUTE IMMEDIATE 'GRANT EXECUTE ON CTXSYS.DRITHSX TO app_user';
        DBMS_OUTPUT.PUT_LINE('[+] Granted EXECUTE on CTXSYS.DRITHSX to app_user');
      ELSE
        DBMS_OUTPUT.PUT_LINE('[!] CTXSYS.DRITHSX package not found');
      END IF;
    EXCEPTION
      WHEN OTHERS THEN
        DBMS_OUTPUT.PUT_LINE('[!] Error granting CTXSYS: ' || SQLERRM);
    END;
  ELSE
    DBMS_OUTPUT.PUT_LINE('[!] CTXSYS schema not found');
  END IF;
END;
/

-- Create tables in app_user schema
CREATE TABLE app_user.reports (
    id NUMBER PRIMARY KEY,
    title VARCHAR2 (100),
    content CLOB
);

CREATE TABLE app_user.secrets (
    id NUMBER PRIMARY KEY,
    name VARCHAR2 (100),
    value VARCHAR2 (255)
);

-- Insert sample data
INSERT INTO
    app_user.reports
VALUES (
        1,
        'Q1 Report',
        'Quarterly financial report for Q1 2024...'
    );

INSERT INTO
    app_user.reports
VALUES (
        2,
        'Q2 Report',
        'Second quarter analysis and projections...'
    );

INSERT INTO
    app_user.secrets
VALUES (
        1,
        'sqli_015',
        'FLAG{ctxsys_dr1thsx_0r4cl3}'
    );

COMMIT;

-- Display initialization summary
DECLARE
  ctx_count NUMBER;
BEGIN
  SELECT COUNT(*) INTO ctx_count
  FROM dba_tab_privs
  WHERE grantee = 'APP_USER'
  AND table_name = 'DRITHSX'
  AND owner = 'CTXSYS';
  
  DBMS_OUTPUT.PUT_LINE('');
  DBMS_OUTPUT.PUT_LINE('======================================');
  DBMS_OUTPUT.PUT_LINE('  SQLi-015 Database Initialized');
  DBMS_OUTPUT.PUT_LINE('======================================');
  DBMS_OUTPUT.PUT_LINE('User: app_user');
  DBMS_OUTPUT.PUT_LINE('Tables: reports (2 rows), secrets (1 row)');
  
  IF ctx_count > 0 THEN
    DBMS_OUTPUT.PUT_LINE('CTXSYS.DRITHSX.SN: AVAILABLE ✓');
  ELSE
    DBMS_OUTPUT.PUT_LINE('CTXSYS.DRITHSX.SN: NOT AVAILABLE ✗');
  END IF;
  
  DBMS_OUTPUT.PUT_LINE('======================================');
END;
/