-- SQLi-049: Quote Filter Bypass (MySQL)

CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL,
    password VARCHAR(100) NOT NULL
);

CREATE TABLE flags (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL,
    value VARCHAR(100) NOT NULL
);

INSERT INTO users (username, password) VALUES
('admin', 'H3x_Enc0d1ng_P@ss!'),
('user', 'userpass123');

INSERT INTO flags (name, value) VALUES
('sqli_049', 'FLAG{h3x_3nc0d1ng_qu0t3_byp4ss}');

GRANT SELECT ON logindb.* TO 'appuser'@'%';
