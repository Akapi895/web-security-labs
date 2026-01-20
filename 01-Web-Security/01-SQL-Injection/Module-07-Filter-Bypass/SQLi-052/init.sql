-- SQLi-052: Equals Filter Bypass (PostgreSQL)

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50),
    email VARCHAR(100)
);

CREATE TABLE flags (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50),
    value VARCHAR(100)
);

INSERT INTO users (username, email) VALUES
('admin', 'admin@example.com'),
('user', 'user@example.com');

INSERT INTO flags (name, value) VALUES
('sqli_052', 'FLAG{3qu4ls_l1k3_b3tw33n_byp4ss}');

GRANT SELECT ON ALL TABLES IN SCHEMA public TO postgres;
