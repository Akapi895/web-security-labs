-- =====================================================
-- SQLi-025: Boolean Blind SQLi via Cookie (MySQL)
-- Kỹ thuật: Injection qua tracking_id cookie
-- =====================================================

CREATE DATABASE IF NOT EXISTS analyticsdb;
USE analyticsdb;

-- Tracking table
CREATE TABLE tracking (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tracking_id VARCHAR(64) NOT NULL,
    page_views INT DEFAULT 1,
    last_visit TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Admin users
CREATE TABLE admin_users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    password VARCHAR(100) NOT NULL,
    role VARCHAR(20) DEFAULT 'admin'
);

-- Flags
CREATE TABLE flags (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    value VARCHAR(100) NOT NULL
);

-- Data
INSERT INTO tracking (tracking_id, page_views) VALUES
('abc123xyz', 15),
('def456uvw', 23),
('ghi789rst', 8);

INSERT INTO admin_users (username, password, role) VALUES
('cookie_admin', 'C00k13_Adm1n_P@ss!', 'superadmin'),
('analytics_mgr', 'An4lyt1cs_2024', 'admin');

INSERT INTO flags (name, value) VALUES
('sqli_025', 'FLAG{c00k13_1nj3ct10n_bl1nd}');
