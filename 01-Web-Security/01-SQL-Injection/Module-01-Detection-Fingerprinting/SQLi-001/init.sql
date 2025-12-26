-- SQLi-001: E-commerce Database Setup

USE ecommerce;

-- Products table
CREATE TABLE products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    category VARCHAR(100),
    stock INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample products
INSERT INTO products (name, description, price, category, stock) VALUES
('Laptop Gaming ASUS ROG', 'High-performance gaming laptop with RTX 4060', 1299.99, 'Electronics', 15),
('Laptop Dell XPS 15', 'Premium ultrabook for professionals', 1499.99, 'Electronics', 10),
('Laptop MacBook Pro M3', 'Apple Silicon powered laptop', 1999.99, 'Electronics', 8),
('Wireless Mouse Logitech', 'Ergonomic wireless mouse', 49.99, 'Accessories', 50),
('Mechanical Keyboard', 'RGB mechanical keyboard with Cherry MX switches', 129.99, 'Accessories', 30),
('USB-C Hub', '7-in-1 USB-C Hub for laptops', 39.99, 'Accessories', 45),
('Monitor 27 inch 4K', 'Ultra HD monitor for productivity', 399.99, 'Electronics', 20),
('Laptop Stand', 'Aluminum laptop stand adjustable', 29.99, 'Accessories', 60),
('Webcam HD 1080p', 'Full HD webcam for video calls', 79.99, 'Electronics', 35),
('Laptop Bag 15.6 inch', 'Water-resistant laptop bag', 59.99, 'Accessories', 40);

-- Users table (for future labs)
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100),
    role VARCHAR(20) DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample users
INSERT INTO users (username, password, email, role) VALUES
('admin', 'admin123', 'admin@ecommerce.local', 'admin'),
('john_doe', 'password123', 'john@example.com', 'user'),
('jane_smith', 'securepass', 'jane@example.com', 'user');

-- Flags table (for CTF)
CREATE TABLE flags (
    id INT AUTO_INCREMENT PRIMARY KEY,
    flag_name VARCHAR(100),
    flag_value VARCHAR(255)
);

INSERT INTO flags (flag_name, flag_value) VALUES
('sqli_001', 'FLAG{qu0t3_b4s3d_d3t3ct10n_m4st3r3d}');
