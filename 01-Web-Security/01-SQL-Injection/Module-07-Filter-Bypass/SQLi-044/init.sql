-- =====================================================
-- SQLi-044: Whitespace Filter Bypass (PostgreSQL)
-- Kỹ thuật: Bypass whitespace bằng parentheses
-- =====================================================

-- Bảng users
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100),
    status VARCHAR(20) DEFAULT 'active'
);

-- Bảng api_keys
CREATE TABLE api_keys (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    api_key VARCHAR(64) NOT NULL,
    permissions VARCHAR(50)
);

-- Bảng flags
CREATE TABLE flags (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    value VARCHAR(100) NOT NULL
);

-- =====================================================
-- INSERT DATA
-- =====================================================

INSERT INTO users (username, email, status) VALUES
('john_doe', 'john@api.local', 'active'),
('jane_smith', 'jane@api.local', 'active'),
('admin', 'admin@api.local', 'admin'),
('bob_wilson', 'bob@api.local', 'inactive');

INSERT INTO api_keys (user_id, api_key, permissions) VALUES
(1, 'pk_user_abc123def456', 'read'),
(2, 'pk_user_xyz789ghi012', 'read'),
(3, 'pk_admin_SUPER_SECRET_KEY_2024', 'admin'),
(4, 'pk_user_disabled_key', 'none');

INSERT INTO flags (name, value) VALUES
('sqli_044', 'FLAG{wh1t3sp4c3_p4r3nth3s3s_byp4ss}');

-- Grants
GRANT SELECT ON ALL TABLES IN SCHEMA public TO postgres;
