-- SQLi-048: Comment Filter Bypass (MySQL)

CREATE TABLE profiles (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL,
    bio TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE secrets (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50),
    secret_key VARCHAR(100)
);

CREATE TABLE flags (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL,
    value VARCHAR(100) NOT NULL
);

INSERT INTO profiles (username, bio) VALUES
('admin', 'System Administrator'),
('john', 'Regular user'),
('jane', 'Developer');

INSERT INTO secrets (username, secret_key) VALUES
('admin', 'C0mm3nt_Byp4ss_S3cr3t!');

INSERT INTO flags (name, value) VALUES
('sqli_048', 'FLAG{c0mm3nt_h4sh_byp4ss}');

GRANT SELECT ON profiledb.* TO 'appuser'@'%';
