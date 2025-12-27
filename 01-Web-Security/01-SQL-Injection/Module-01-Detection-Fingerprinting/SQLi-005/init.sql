USE shopdb;

CREATE TABLE items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10,2),
    category VARCHAR(100)
);

INSERT INTO items (name, description, price, category) VALUES
('Gaming Laptop', 'High-end gaming laptop with RTX graphics', 1599.99, 'Electronics'),
('Wireless Headphones', 'Noise-cancelling bluetooth headphones', 299.99, 'Audio'),
('Smart Watch', 'Fitness tracking smartwatch', 249.99, 'Wearables'),
('USB-C Dock', 'Universal docking station', 89.99, 'Accessories'),
('4K Monitor', 'Ultra HD display for professionals', 599.99, 'Electronics');

CREATE TABLE flags (
    id INT AUTO_INCREMENT PRIMARY KEY,
    flag_name VARCHAR(100),
    flag_value VARCHAR(255)
);

INSERT INTO flags (flag_name, flag_value) VALUES
('sqli_005', 'FLAG{3rr0r_m3ss4g3_f1ng3rpr1nt1ng}');
