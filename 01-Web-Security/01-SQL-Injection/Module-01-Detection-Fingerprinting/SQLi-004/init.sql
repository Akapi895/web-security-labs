-- SQLi-004: Product API Database Setup (Oracle)

-- Connect as app_user (or create tables as SYSTEM and grant to app_user)
-- Note: This script runs as SYSTEM user, so we need to specify schema or grant access

-- Products table (create in app_user schema)
CREATE TABLE app_user.products (
    id NUMBER PRIMARY KEY,
    name VARCHAR2 (255) NOT NULL,
    description VARCHAR2 (4000),
    price NUMBER (10, 2),
    category VARCHAR2 (100),
    sku VARCHAR2 (50),
    stock NUMBER DEFAULT 0
);

-- Insert sample products
INSERT INTO
    app_user.products
VALUES (
        1,
        'Enterprise Server',
        'High-performance server for enterprise workloads',
        4999.99,
        'Servers',
        'SRV-001',
        10
    );

INSERT INTO
    app_user.products
VALUES (
        2,
        'Database License',
        'Oracle Database Enterprise Edition license',
        47500.00,
        'Software',
        'ORA-DB-01',
        999
    );

INSERT INTO
    app_user.products
VALUES (
        3,
        'Network Switch',
        '48-port managed network switch',
        1299.99,
        'Networking',
        'NET-SW-48',
        25
    );

INSERT INTO
    app_user.products
VALUES (
        4,
        'Storage Array',
        '100TB enterprise storage array',
        15999.99,
        'Storage',
        'STO-ARR-100',
        5
    );

INSERT INTO
    app_user.products
VALUES (
        5,
        'Security Firewall',
        'Next-gen firewall appliance',
        8999.99,
        'Security',
        'SEC-FW-01',
        15
    );

INSERT INTO
    app_user.products
VALUES (
        6,
        'Backup Solution',
        'Automated backup and recovery solution',
        2499.99,
        'Software',
        'BAK-SOL-01',
        50
    );

INSERT INTO
    app_user.products
VALUES (
        7,
        'Load Balancer',
        'Application delivery controller',
        12999.99,
        'Networking',
        'NET-LB-01',
        8
    );

INSERT INTO
    app_user.products
VALUES (
        8,
        'Virtual Machine License',
        'Virtualization platform license',
        995.00,
        'Software',
        'VM-LIC-01',
        200
    );

COMMIT;

-- Secrets table (for CTF)
CREATE TABLE app_user.secrets (
    id NUMBER PRIMARY KEY,
    secret_name VARCHAR2 (100),
    secret_value VARCHAR2 (255)
);

INSERT INTO
    app_user.secrets
VALUES (
        1,
        'sqli_004',
        'FLAG{c0mm3nt_d3t3ct10n_0r4cl3_m4st3r}'
    );

COMMIT;