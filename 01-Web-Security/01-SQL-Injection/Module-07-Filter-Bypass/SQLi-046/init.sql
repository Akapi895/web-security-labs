-- SQLi-046: SELECT Filter Bypass (MySQL)

CREATE TABLE inventory (
    id INT PRIMARY KEY AUTO_INCREMENT,
    item_name VARCHAR(100) NOT NULL,
    quantity INT,
    location VARCHAR(50)
);

CREATE TABLE admin_config (
    id INT PRIMARY KEY AUTO_INCREMENT,
    config_key VARCHAR(50),
    config_value VARCHAR(200)
);

CREATE TABLE flags (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL,
    value VARCHAR(100) NOT NULL
);

INSERT INTO inventory (item_name, quantity, location) VALUES
('Laptop Dell XPS', 50, 'Warehouse A'),
('Monitor Samsung', 120, 'Warehouse B'),
('Keyboard Logitech', 200, 'Warehouse A'),
('Mouse Wireless', 150, 'Warehouse C');

INSERT INTO admin_config (config_key, config_value) VALUES
('admin_password', 'V3rs10n_C0mm3nt_Byp4ss!'),
('api_secret', 'sk_secret_inventory_2024');

INSERT INTO flags (name, value) VALUES
('sqli_046', 'FLAG{mysql_v3rs10n_c0mm3nt_byp4ss}');

GRANT SELECT ON inventorydb.* TO 'appuser'@'%';
