USE userdb;
CREATE TABLE users (id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(50), email VARCHAR(100), bio TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
INSERT INTO users (username, email, bio) VALUES ('alice', 'alice@example.com', 'Security researcher'), ('bob', 'bob@example.com', 'Developer'), ('admin', 'admin@corp.local', 'System Administrator');
CREATE TABLE secrets (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(100), value VARCHAR(255));
INSERT INTO secrets (name, value) VALUES ('sqli_010', 'FLAG{upd4t3xml_t4bl3_3num3r4t10n}');
