-- SQLi-040: Oracle OOB HTTP via HTTPURITYPE
ALTER SESSION SET CONTAINER = XEPDB1;

CREATE USER invoice_user IDENTIFIED BY InvoicePass123;
GRANT CONNECT, RESOURCE, CREATE SESSION, UNLIMITED TABLESPACE TO invoice_user;
GRANT EXECUTE ON HTTPURITYPE TO invoice_user;
GRANT EXECUTE ON UTL_HTTP TO invoice_user;

BEGIN
  DBMS_NETWORK_ACL_ADMIN.CREATE_ACL(acl => 'http_acl.xml', description => 'HTTP Access',
    principal => 'INVOICE_USER', is_grant => TRUE, privilege => 'connect');
  DBMS_NETWORK_ACL_ADMIN.ADD_PRIVILEGE(acl => 'http_acl.xml', principal => 'INVOICE_USER',
    is_grant => TRUE, privilege => 'resolve');
  DBMS_NETWORK_ACL_ADMIN.ASSIGN_ACL(acl => 'http_acl.xml', host => '*', lower_port => 80, upper_port => 443);
  COMMIT;
END;
/

ALTER SESSION SET CURRENT_SCHEMA = invoice_user;

CREATE TABLE invoices (id NUMBER PRIMARY KEY, customer VARCHAR2(100), amount NUMBER);
CREATE TABLE flags (id NUMBER PRIMARY KEY, name VARCHAR2(50), value VARCHAR2(100));

INSERT INTO invoices VALUES (1, 'ABC Corp', 15000);
INSERT INTO invoices VALUES (2, 'XYZ Ltd', 8500);
INSERT INTO flags VALUES (1, 'sqli_040', 'FLAG{oracle_httpuritype_oob}');
COMMIT;
/
