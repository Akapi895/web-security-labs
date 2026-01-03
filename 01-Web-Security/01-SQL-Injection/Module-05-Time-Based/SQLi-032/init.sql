-- SQLi-032: Time-based Blind (Oracle) - Heavy Query Join

ALTER SESSION SET CONTAINER = XEPDB1;

CREATE TABLE app_user.requests (
    id NUMBER PRIMARY KEY,
    request_id VARCHAR2(50) NOT NULL,
    status VARCHAR2(20) DEFAULT 'pending'
);

CREATE TABLE app_user.admin_creds (
    id NUMBER PRIMARY KEY,
    username VARCHAR2(50) NOT NULL,
    password VARCHAR2(100) NOT NULL
);

CREATE TABLE app_user.secrets (
    id NUMBER PRIMARY KEY,
    name VARCHAR2(50) NOT NULL,
    value VARCHAR2(100) NOT NULL
);

INSERT INTO app_user.requests VALUES (1, 'REQ001', 'completed');
INSERT INTO app_user.requests VALUES (2, 'REQ002', 'pending');

INSERT INTO app_user.admin_creds VALUES (1, 'ora_admin', 'Or4_Adm1n_H34vy!');

INSERT INTO app_user.secrets VALUES (1, 'sqli_032', 'FLAG{0r4cl3_h34vy_qu3ry}');

COMMIT;
GRANT SELECT ON app_user.requests TO app_user;
GRANT SELECT ON app_user.admin_creds TO app_user;
GRANT SELECT ON app_user.secrets TO app_user;
