-- SQLi-051: AND/OR Filter Bypass (MySQL)

CREATE TABLE products (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100),
    price DECIMAL(10,2)
);

CREATE TABLE flags (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50),
    value VARCHAR(100)
);

INSERT INTO products (name, price) VALUES
('Laptop', 999.99),
('Phone', 699.99);

INSERT INTO flags (name, value) VALUES
('sqli_051', 'FLAG{4nd_0r_0p3r4t0r_byp4ss}');

GRANT SELECT ON productdb.* TO 'appuser'@'%';
