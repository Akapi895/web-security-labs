-- =====================================================
-- SQLi-019: Union-based SQLi - Single Column (MySQL)
-- Kỹ thuật: CONCAT/CONCAT_WS để ghép nhiều giá trị
-- =====================================================

-- Tạo database
CREATE DATABASE IF NOT EXISTS ecommerce;
USE ecommerce;

-- Bảng products - Chỉ hiển thị tên sản phẩm trong search results
CREATE TABLE products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    description TEXT,
    category VARCHAR(50)
);

-- Bảng users - Mục tiêu extraction
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    password VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    role VARCHAR(20) DEFAULT 'user'
);

-- Bảng flags - Chứa flag bí mật
CREATE TABLE flags (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    value VARCHAR(100) NOT NULL
);

-- =====================================================
-- INSERT DATA
-- =====================================================

-- Products data
INSERT INTO products (name, price, description, category) VALUES
('iPhone 15 Pro', 999.99, 'Latest Apple smartphone with A17 chip', 'Electronics'),
('Samsung Galaxy S24', 899.99, 'Android flagship with AI features', 'Electronics'),
('MacBook Pro M3', 1999.99, 'Professional laptop with M3 chip', 'Computers'),
('Dell XPS 15', 1499.99, 'Premium Windows laptop', 'Computers'),
('Sony WH-1000XM5', 349.99, 'Noise cancelling headphones', 'Audio'),
('AirPods Pro 2', 249.99, 'Apple wireless earbuds', 'Audio'),
('iPad Air', 599.99, 'Versatile tablet for work and play', 'Tablets'),
('Nintendo Switch', 299.99, 'Hybrid gaming console', 'Gaming');

-- Users data - Target cho extraction
INSERT INTO users (username, password, email, role) VALUES
('admin', 'Sup3rS3cr3tP@ss!', 'admin@ecommerce.local', 'admin'),
('john_doe', 'john123456', 'john@example.com', 'user'),
('jane_smith', 'janepass789', 'jane@example.com', 'user'),
('bob_wilson', 'bobwilson2024', 'bob@example.com', 'user'),
('manager', 'M@nag3r_2024', 'manager@ecommerce.local', 'manager');

-- Flag data
INSERT INTO flags (name, value) VALUES
('sqli_019', 'FLAG{un10n_c0nc4t_m4st3r}');

-- =====================================================
-- GRANTS
-- =====================================================
-- MySQL default user có đủ quyền trong container
