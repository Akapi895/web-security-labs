-- SQLi-031: Time-based Blind (PostgreSQL) - pg_sleep

CREATE TABLE api_users (
    id SERIAL PRIMARY KEY,
    api_key VARCHAR(64) NOT NULL,
    rate_limit INT DEFAULT 100
);

CREATE TABLE admin_creds (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    password VARCHAR(100) NOT NULL
);

CREATE TABLE flags (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    value VARCHAR(100) NOT NULL
);

INSERT INTO api_users (api_key, rate_limit) VALUES
('key_abc123', 100),
('key_xyz789', 50);

INSERT INTO admin_creds (username, password) VALUES
('pg_admin', 'PG_Sl33p_Adm1n!'),
('api_user', 'AP1_Us3r_2024');

INSERT INTO flags (name, value) VALUES
('sqli_031', 'FLAG{pg_sl33p_t1m3_bl1nd}');
