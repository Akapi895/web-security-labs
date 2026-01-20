-- SQLi-039: Oracle OOB DNS via UTL_INADDR
ALTER SESSION SET CONTAINER = XEPDB1;

CREATE USER order_user IDENTIFIED BY OrderPass123;
GRANT CONNECT, RESOURCE, CREATE SESSION, UNLIMITED TABLESPACE TO order_user;
GRANT EXECUTE ON UTL_INADDR TO order_user;

-- ACL for DNS only
BEGIN
  DBMS_NETWORK_ACL_ADMIN.CREATE_ACL(
    acl => 'dns_resolve.xml',
    description => 'Allow DNS resolution only',
    principal => 'ORDER_USER',
    is_grant => TRUE,
    privilege => 'resolve'
  );
  DBMS_NETWORK_ACL_ADMIN.ASSIGN_ACL(acl => 'dns_resolve.xml', host => '*');
  COMMIT;
END;
/

ALTER SESSION SET CURRENT_SCHEMA = order_user;

CREATE TABLE orders (id NUMBER PRIMARY KEY, product VARCHAR2(100), quantity NUMBER);
CREATE TABLE flags (id NUMBER PRIMARY KEY, name VARCHAR2(50), value VARCHAR2(100));

INSERT INTO orders VALUES (1, 'Laptop Pro', 2);
INSERT INTO orders VALUES (2, 'Mouse Wireless', 5);
INSERT INTO flags VALUES (1, 'sqli_039', 'FLAG{oracle_utl_inaddr_dns}');
COMMIT;
/
