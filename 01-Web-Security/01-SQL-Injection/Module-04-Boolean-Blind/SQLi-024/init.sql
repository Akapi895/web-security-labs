-- =====================================================
-- SQLi-024: Boolean Blind SQLi (Oracle)
-- Kỹ thuật: SUBSTR() + ROWNUM pagination
-- =====================================================

ALTER SESSION SET CONTAINER = XEPDB1;

-- Session tokens table
CREATE TABLE app_user.sessions (
    id NUMBER PRIMARY KEY,
    session_token VARCHAR2(64) NOT NULL,
    user_id NUMBER,
    is_valid NUMBER(1) DEFAULT 1
);

-- Users table
CREATE TABLE app_user.users (
    id NUMBER PRIMARY KEY,
    username VARCHAR2(50) NOT NULL,
    email VARCHAR2(100)
);

-- Admin credentials - Target
CREATE TABLE app_user.admin_creds (
    id NUMBER PRIMARY KEY,
    username VARCHAR2(50) NOT NULL,
    password VARCHAR2(100) NOT NULL,
    role VARCHAR2(20)
);

-- Flags
CREATE TABLE app_user.secrets (
    id NUMBER PRIMARY KEY,
    name VARCHAR2(50) NOT NULL,
    value VARCHAR2(100) NOT NULL
);

-- =====================================================
-- INSERT DATA
-- =====================================================

INSERT INTO app_user.sessions VALUES (1, 'sess_valid_abc123', 1, 1);
INSERT INTO app_user.sessions VALUES (2, 'sess_valid_def456', 2, 1);
INSERT INTO app_user.sessions VALUES (3, 'sess_expired_xyz', 3, 0);

INSERT INTO app_user.users VALUES (1, 'alice', 'alice@corp.com');
INSERT INTO app_user.users VALUES (2, 'bob', 'bob@corp.com');
INSERT INTO app_user.users VALUES (3, 'charlie', 'charlie@corp.com');

INSERT INTO app_user.admin_creds VALUES (1, 'oracle_boss', 'Or4cl3_B0ss_P@ss!', 'superadmin');
INSERT INTO app_user.admin_creds VALUES (2, 'db_master', 'DB_M4st3r_2024', 'admin');

INSERT INTO app_user.secrets VALUES (1, 'sqli_024', 'FLAG{0r4cl3_substr_bl1nd}');

COMMIT;

GRANT SELECT ON app_user.sessions TO app_user;
GRANT SELECT ON app_user.users TO app_user;
GRANT SELECT ON app_user.admin_creds TO app_user;
GRANT SELECT ON app_user.secrets TO app_user;
