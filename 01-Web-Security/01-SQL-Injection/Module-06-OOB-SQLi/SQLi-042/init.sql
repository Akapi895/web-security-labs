-- SQLi-042: PostgreSQL OOB HTTP via dblink

-- Enable dblink extension
CREATE EXTENSION IF NOT EXISTS dblink;

CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    price DECIMAL(10,2),
    category VARCHAR(50)
);

CREATE TABLE admin_users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    password VARCHAR(100) NOT NULL
);

CREATE TABLE flags (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    value VARCHAR(100) NOT NULL
);

INSERT INTO products (name, price, category) VALUES
('Laptop Pro', 1299.99, 'Electronics'),
('Wireless Mouse', 29.99, 'Accessories'),
('USB Hub', 19.99, 'Accessories'),
('Monitor 27"', 399.99, 'Electronics');

INSERT INTO admin_users (username, password) VALUES
('dblink_admin', 'DBL1nk_Adm1n!'),
('pg_operator', 'PG_0p3r@t0r');

INSERT INTO flags (name, value) VALUES
('sqli_042', 'FLAG{postgres_dblink_oob_exfil}');
