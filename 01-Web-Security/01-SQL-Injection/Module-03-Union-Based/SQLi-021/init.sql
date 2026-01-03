-- =====================================================
-- SQLi-021: Union-based SQLi - Multi Row (MySQL)
-- Kỹ thuật: GROUP_CONCAT() để aggregate nhiều rows
-- =====================================================

-- Tạo database
CREATE DATABASE IF NOT EXISTS blogdb;

USE blogdb;

-- Bảng posts - Blog articles
CREATE TABLE posts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    content TEXT,
    author VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Bảng comments - Hiển thị nhiều rows
CREATE TABLE comments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    post_id INT NOT NULL,
    username VARCHAR(50) NOT NULL,
    comment_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES posts (id)
);

-- Bảng admin_users - Mục tiêu extraction
CREATE TABLE admin_users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    password VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    role VARCHAR(20) DEFAULT 'admin',
    api_key VARCHAR(64)
);

-- Bảng secrets - Chứa flag
CREATE TABLE secrets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    value VARCHAR(100) NOT NULL
);

-- =====================================================
-- INSERT DATA
-- =====================================================

-- Posts
INSERT INTO
    posts (title, content, author)
VALUES (
        'Welcome to Our Blog',
        'This is our first blog post. Stay tuned for more updates!',
        'admin'
    ),
    (
        'Security Best Practices',
        'Here are some tips to keep your applications secure...',
        'john'
    ),
    (
        'MySQL Performance Tips',
        'Optimize your database with these proven techniques.',
        'jane'
    ),
    (
        'Docker for Beginners',
        'Getting started with containerization made easy.',
        'admin'
    );

-- Comments - Multiple rows per post
INSERT INTO
    comments (
        post_id,
        username,
        comment_text
    )
VALUES (
        1,
        'reader1',
        'Great first post! Looking forward to more content.'
    ),
    (
        1,
        'techfan',
        'Very informative, thanks for sharing!'
    ),
    (
        1,
        'dev_user',
        'Nice work on the blog setup.'
    ),
    (
        2,
        'security_guy',
        'Very important topic. Everyone should read this.'
    ),
    (
        2,
        'hacker101',
        'What about SQL injection prevention?'
    ),
    (
        2,
        'pentester',
        'Good overview of security practices.'
    ),
    (
        3,
        'dba_expert',
        'Great tips! I use most of these daily.'
    ),
    (
        3,
        'coder123',
        'The indexing advice saved my project.'
    ),
    (
        4,
        'newbie_dev',
        'Finally understand Docker! Thanks!'
    ),
    (
        4,
        'sysadmin',
        'Good intro for beginners.'
    );

-- Admin users - Target for extraction
INSERT INTO
    admin_users (
        username,
        password,
        email,
        role,
        api_key
    )
VALUES (
        'superadmin',
        'Sup3r_Adm1n_P@ss!',
        'superadmin@blog.local',
        'superadmin',
        'demo_key_4eC39HqLyjWDarjtT1zdp7dc'
    ),
    (
        'admin',
        'Adm1n_2024_S3cure',
        'admin@blog.local',
        'admin',
        'demo_key_7fG82KmNopQRstuV2wxyZ3ab'
    ),
    (
        'editor',
        'Ed1t0r_P@ssw0rd',
        'editor@blog.local',
        'editor',
        'demo_key_9hI04LnOpQrStUvW4xyzA5cd'
    ),
    (
        'moderator',
        'M0d_S3cur3_2024',
        'mod@blog.local',
        'moderator',
        'demo_key_2jK16MnPqRsTuVwX5yzaB6ef'
    );

-- Flag
INSERT INTO
    secrets (name, value)
VALUES (
        'sqli_021',
        'FLAG{gr0up_c0nc4t_4ggr3g4t3}'
    );

-- =====================================================
-- GRANTS
-- =====================================================
-- Default root user có đủ quyền