USE shopdb;

CREATE TABLE products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255),
    description TEXT,
    price DECIMAL(10,2),
    category VARCHAR(100),
    stock INT DEFAULT 0
);

INSERT INTO products (name, description, price, category, stock) VALUES
('Gaming Laptop Pro', 'High-end gaming laptop with RTX 4080', 2499.99, 'Electronics', 15),
('Wireless Keyboard', 'Mechanical RGB wireless keyboard', 149.99, 'Accessories', 50),
('4K Monitor 32"', 'Ultra HD IPS display', 599.99, 'Electronics', 20),
('USB-C Hub', 'Multi-port docking station', 79.99, 'Accessories', 100),
('Gaming Mouse', 'High DPI gaming mouse', 89.99, 'Accessories', 75);

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50),
    password VARCHAR(255),
    email VARCHAR(100)
);

INSERT INTO users (username, password, email) VALUES
('admin', 'SuperSecretAdminPass123!', 'admin@shop.local'),
('user1', 'userpassword', 'user1@shop.local');

CREATE TABLE flags (
    id INT AUTO_INCREMENT PRIMARY KEY,
    flag_name VARCHAR(100),
    flag_value VARCHAR(255)
);

INSERT INTO flags (flag_name, flag_value) VALUES
('sqli_009', 'FLAG{3xtr4ctv4lu3_mysql_3rr0r_b4s3d}');
