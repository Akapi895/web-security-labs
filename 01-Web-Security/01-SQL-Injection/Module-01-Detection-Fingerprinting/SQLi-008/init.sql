-- Switch to app_user schema before creating tables
-- Init scripts run as SYS by default, so we need to explicitly set the schema
ALTER SESSION SET CURRENT_SCHEMA = app_user;

CREATE TABLE services (
    id NUMBER PRIMARY KEY,
    name VARCHAR2(100),
    description VARCHAR2(255),
    status VARCHAR2(20)
);

INSERT INTO services VALUES (1, 'Authentication', 'User authentication service', 'ACTIVE');
INSERT INTO services VALUES (2, 'Database', 'Oracle database service', 'ACTIVE');
INSERT INTO services VALUES (3, 'API Gateway', 'REST API gateway', 'ACTIVE');
COMMIT;

CREATE TABLE secrets (
    id NUMBER PRIMARY KEY,
    name VARCHAR2(100),
    value VARCHAR2(255)
);

INSERT INTO secrets VALUES (1, 'sqli_008', 'FLAG{c0nc4t_0r4cl3_p1p3_0p3r4t0r}');
COMMIT;
