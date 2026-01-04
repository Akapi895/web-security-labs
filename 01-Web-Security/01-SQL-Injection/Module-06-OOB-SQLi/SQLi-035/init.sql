-- =====================================================
-- SQLi-035: Setup for Windows 11 Lab
-- =====================================================

DROP DATABASE IF EXISTS corpdb;
CREATE DATABASE corpdb;
USE corpdb;

CREATE TABLE products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price DECIMAL(10,2),
    in_stock BOOLEAN DEFAULT true
);

CREATE TABLE admin_users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    password VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    role VARCHAR(20) DEFAULT 'admin'
);

CREATE TABLE flags (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    value VARCHAR(100) NOT NULL
);

CREATE TABLE api_keys (
    id INT AUTO_INCREMENT PRIMARY KEY,
    service_name VARCHAR(50) NOT NULL,
    api_key VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO products (name, description, price, in_stock) VALUES
('Enterprise Server', 'High-performance server solution', 4999.99, true),
('Network Switch 48-Port', 'Managed gigabit switch', 899.99, true),
('Firewall Appliance', 'Next-gen firewall with IPS', 2499.99, true),
('Storage Array 10TB', 'Enterprise storage solution', 3999.99, false),
('Backup Solution Pro', 'Automated backup system', 1299.99, true);

INSERT INTO admin_users (username, password, email, role) VALUES
('sysadmin', 'Sys@dm1n_S3cur3!', 'sysadmin@corp.local', 'superadmin'),
('netops', 'N3tw0rk_0ps_2024', 'netops@corp.local', 'admin'),
('dbadmin', 'DB_Adm1n_P@ss!', 'dbadmin@corp.local', 'admin');

INSERT INTO flags (name, value) VALUES
('sqli_035', 'FLAG{mysql_oob_dns_unc_exfil}');

INSERT INTO api_keys (service_name, api_key) VALUES
('AWS', 'AKIAIOSFODNN7EXAMPLE'),
('Azure', 'dGhpcyBpcyBhIHNlY3JldCBrZXk='),
('Stripe', 'sk_test_DUMMY_KEY_FOR_LAB_ONLY');

-- --- QUAN TRỌNG: TẠO USER CHO WEB APP ---
-- Tạo user webapp nếu chưa có
CREATE USER IF NOT EXISTS 'webapp'@'localhost' IDENTIFIED BY 'password123';
-- Cấp quyền SELECT để chạy app
GRANT SELECT ON corpdb.* TO 'webapp'@'localhost';
-- Cấp quyền FILE để tấn công OOB (Mấu chốt)
GRANT FILE ON *.* TO 'webapp'@'localhost';

FLUSH PRIVILEGES;