-- =====================================================
-- SQLi-029: Time-based Blind SQLi (MySQL)
-- Kỹ thuật: SLEEP() và BENCHMARK() alternative
-- =====================================================

CREATE DATABASE IF NOT EXISTS webshop;
USE webshop;

CREATE TABLE products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    price DECIMAL(10,2),
    in_stock BOOLEAN DEFAULT true
);

CREATE TABLE admin_users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    password VARCHAR(100) NOT NULL
);

CREATE TABLE flags (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    value VARCHAR(100) NOT NULL
);

INSERT INTO products (name, price, in_stock) VALUES
('Laptop Pro', 1299.99, true),
('Wireless Mouse', 49.99, true),
('USB Cable', 9.99, false),
('Monitor 27"', 399.99, true);

INSERT INTO admin_users (username, password) VALUES
('time_admin', 'T1m3_Adm1n_P@ss!'),
('sleep_user', 'Sl33p_Us3r_2024');

INSERT INTO flags (name, value) VALUES
('sqli_029', 'FLAG{t1m3_b4s3d_sl33p_1nj3ct10n}');
