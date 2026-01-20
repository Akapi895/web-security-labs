-- =====================================================
-- SQLi-043: Space Filter Bypass (MySQL)
-- Kỹ thuật: Bypass space bằng /**/, %09, %0a
-- =====================================================

-- Bảng products
CREATE TABLE products (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price DECIMAL(10,2),
    category VARCHAR(50)
);

-- Bảng users
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL,
    password VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    role VARCHAR(20) DEFAULT 'user'
);

-- Bảng flags
CREATE TABLE flags (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL,
    value VARCHAR(100) NOT NULL
);

-- =====================================================
-- INSERT DATA
-- =====================================================

INSERT INTO products (name, description, price, category) VALUES
('Gaming Laptop', 'High-performance gaming laptop with RTX 4080', 1999.99, 'Laptops'),
('Wireless Mouse', 'Ergonomic wireless mouse with RGB', 49.99, 'Accessories'),
('Mechanical Keyboard', 'Cherry MX Blue switches', 129.99, 'Accessories'),
('4K Monitor', '27-inch 4K IPS display', 399.99, 'Monitors'),
('USB-C Hub', '7-in-1 USB-C docking station', 79.99, 'Accessories'),
('Webcam HD', '1080p webcam with microphone', 89.99, 'Accessories');

INSERT INTO users (username, password, email, role) VALUES
('admin', 'Sp4c3_Byp4ss_Adm1n!', 'admin@shop.local', 'admin'),
('manager', 'M4n4g3r_P@ss', 'manager@shop.local', 'manager'),
('john', 'john123', 'john@example.com', 'user');

INSERT INTO flags (name, value) VALUES
('sqli_043', 'FLAG{sp4c3_byp4ss_c0mm3nt_1nj3ct10n}');

-- Grants
GRANT SELECT ON shopdb.* TO 'appuser'@'%';
