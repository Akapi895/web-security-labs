-- =====================================================
-- SQLi-027: Boolean Blind via ORDER BY (MySQL)
-- Kỹ thuật: Conditional ordering
-- =====================================================

CREATE DATABASE IF NOT EXISTS shopdb;
USE shopdb;

CREATE TABLE products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    price DECIMAL(10,2),
    rating DECIMAL(2,1)
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

INSERT INTO products (name, price, rating) VALUES
('Gaming Laptop', 1499.99, 4.5),
('Mechanical Keyboard', 129.99, 4.8),
('Wireless Mouse', 59.99, 4.2),
('4K Monitor', 399.99, 4.6),
('USB Hub', 29.99, 3.9);

INSERT INTO admin_users (username, password) VALUES
('order_admin', 'Ord3r_By_Adm1n!'),
('sort_master', 'S0rt_M4st3r_2024');

INSERT INTO flags (name, value) VALUES
('sqli_027', 'FLAG{0rd3r_by_bl1nd_1nj3ct10n}');
