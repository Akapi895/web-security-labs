-- =====================================================
-- SQLi-045: UNION Keyword Filter Bypass (MySQL)
-- Kỹ thuật: Case variation Un/**/IoN
-- =====================================================

CREATE TABLE articles (
    id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(200) NOT NULL,
    content TEXT,
    author VARCHAR(50),
    published_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL,
    password VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    role VARCHAR(20) DEFAULT 'user'
);

CREATE TABLE flags (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL,
    value VARCHAR(100) NOT NULL
);

-- =====================================================
-- INSERT DATA
-- =====================================================

INSERT INTO articles (title, content, author) VALUES
('Introduction to Web Security', 'Web security is crucial for modern applications...', 'john_doe'),
('SQL Injection Prevention', 'Learn how to prevent SQL injection attacks...', 'jane_smith'),
('XSS Protection Guide', 'Cross-site scripting can be prevented by...', 'bob_wilson'),
('CSRF Token Implementation', 'CSRF tokens help protect against...', 'alice_brown');

INSERT INTO users (username, password, email, role) VALUES
('admin', 'Un10n_Byp4ss_Adm1n!', 'admin@blog.local', 'admin'),
('editor', 'Ed1t0r_P@ss', 'editor@blog.local', 'editor'),
('writer', 'Wr1t3r_P@ss', 'writer@blog.local', 'writer');

INSERT INTO flags (name, value) VALUES
('sqli_045', 'FLAG{un10n_c4s3_v4r14t10n_byp4ss}');

GRANT SELECT ON blogdb.* TO 'appuser'@'%';
