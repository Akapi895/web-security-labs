CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'user'
);

INSERT INTO users (username, password, role) VALUES
('admin', 'admin123', 'admin'),
('user1', 'password1', 'user');

CREATE TABLE secrets (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    value VARCHAR(255)
);

INSERT INTO secrets (name, value) VALUES
('sqli_006', 'FLAG{v3rs10n_qu3ry_p0stgr3sql_1d3nt1f13d}');
