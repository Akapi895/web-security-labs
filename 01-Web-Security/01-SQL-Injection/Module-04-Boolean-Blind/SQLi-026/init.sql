-- =====================================================
-- SQLi-026: Boolean Blind via JSON body (PostgreSQL)
-- =====================================================

CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    price DECIMAL(10,2),
    stock INT DEFAULT 0
);

CREATE TABLE admin_credentials (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    password VARCHAR(100) NOT NULL
);

CREATE TABLE flags (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    value VARCHAR(100) NOT NULL
);

INSERT INTO products (name, price, stock) VALUES
('Laptop Pro', 1299.99, 50),
('Wireless Mouse', 29.99, 200),
('USB-C Hub', 49.99, 150);

INSERT INTO admin_credentials (username, password) VALUES
('json_admin', 'JS0N_Adm1n_S3cr3t!'),
('api_user', 'AP1_Us3r_2024');

INSERT INTO flags (name, value) VALUES
('sqli_026', 'FLAG{js0n_b0dy_1nj3ct10n}');
