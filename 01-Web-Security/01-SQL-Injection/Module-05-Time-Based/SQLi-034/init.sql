-- SQLi-034: Time-based Blind via User-Agent (PostgreSQL)

CREATE TABLE visitors (
    id SERIAL PRIMARY KEY,
    user_agent VARCHAR(500),
    ip_address VARCHAR(50),
    visit_time TIMESTAMP DEFAULT NOW()
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

INSERT INTO visitors (user_agent, ip_address) VALUES
('Mozilla/5.0', '192.168.1.1');

INSERT INTO admin_creds (username, password) VALUES
('ua_admin', 'Us3r_Ag3nt_Adm1n!');

INSERT INTO flags (name, value) VALUES
('sqli_034', 'FLAG{us3r_4g3nt_t1m3_bl1nd}');
