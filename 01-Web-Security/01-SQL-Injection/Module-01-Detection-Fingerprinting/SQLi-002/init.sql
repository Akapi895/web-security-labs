-- SQLi-002: News Portal Database Setup (PostgreSQL)

-- Articles table
CREATE TABLE articles (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT,
    category VARCHAR(50),
    author VARCHAR(100),
    published_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    views INT DEFAULT 0
);

-- Insert sample articles
INSERT INTO articles (title, content, category, author, views) VALUES
('New AI Breakthrough in 2024', 'Scientists have discovered a new method for training AI models...', 'technology', 'John Smith', 1520),
('PostgreSQL 16 Released', 'The latest version of PostgreSQL brings performance improvements...', 'technology', 'Jane Doe', 890),
('Stock Market Hits Record High', 'The stock market reached new heights today as investors...', 'finance', 'Mike Johnson', 2340),
('Climate Change Summit Results', 'World leaders agreed on new measures to combat climate change...', 'politics', 'Sarah Williams', 1875),
('New iPhone 16 Features Revealed', 'Apple has announced the new features coming to iPhone 16...', 'technology', 'Tech Reporter', 3200),
('Cybersecurity Threats on the Rise', 'Experts warn about increasing cybersecurity threats...', 'technology', 'Security Expert', 1100),
('Bitcoin Reaches $100K', 'Bitcoin has finally reached the $100,000 milestone...', 'finance', 'Crypto Analyst', 4500),
('SpaceX Mars Mission Update', 'SpaceX provides update on their Mars colonization plans...', 'science', 'Space Writer', 2890),
('Remote Work Statistics 2024', 'New statistics show remote work is here to stay...', 'business', 'HR Specialist', 980),
('Olympic Games 2024 Highlights', 'The best moments from the 2024 Olympic Games...', 'sports', 'Sports Editor', 5600);

-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100),
    role VARCHAR(20) DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO users (username, password, email, role) VALUES
('admin', 'supersecretpassword', 'admin@newsportal.local', 'admin'),
('editor', 'editor123', 'editor@newsportal.local', 'editor'),
('reader', 'reader456', 'reader@example.com', 'user');

-- Secrets table (for CTF)
CREATE TABLE secrets (
    id SERIAL PRIMARY KEY,
    secret_name VARCHAR(100),
    secret_value VARCHAR(255)
);

INSERT INTO secrets (secret_name, secret_value) VALUES
('sqli_002_flag', 'FLAG{l0g1c_b4s3d_d3t3ct10n_p0stgr3sql}');
