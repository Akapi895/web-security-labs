-- =====================================================
-- SQLi-023: Boolean Blind SQLi (PostgreSQL)
-- Kỹ thuật: SUBSTRING character-by-character extraction
-- =====================================================

-- Bảng users cho username validation
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    is_active BOOLEAN DEFAULT true
);

-- Bảng admin_secrets - Mục tiêu extraction
CREATE TABLE admin_secrets (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    password VARCHAR(100) NOT NULL,
    api_key VARCHAR(64),
    role VARCHAR(20) DEFAULT 'admin'
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

-- Regular users
INSERT INTO users (username, password, email) VALUES
('john_doe', 'john123pass', 'john@example.com'),
('jane_smith', 'jane456pass', 'jane@example.com'),
('bob_wilson', 'bob789pass', 'bob@example.com'),
('alice_brown', 'alice012pass', 'alice@example.com');

-- Admin secrets - Target for blind extraction
INSERT INTO admin_secrets (username, password, api_key, role) VALUES
('superadmin', 'Bl1nd_Sup3r_S3cr3t!', 'sk_blind_abc123def456', 'superadmin'),
('dbadmin', 'DB_Bl1nd_P@ss', 'sk_blind_xyz789ghi012', 'admin');

-- Flag
INSERT INTO flags (name, value) VALUES
('sqli_023', 'FLAG{b00l34n_bl1nd_substr1ng}');

-- Grants
GRANT SELECT ON ALL TABLES IN SCHEMA public TO postgres;
