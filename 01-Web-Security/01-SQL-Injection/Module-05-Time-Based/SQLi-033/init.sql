-- SQLi-033: Time-based Blind via Cookie (MySQL)

CREATE DATABASE IF NOT EXISTS sessiondb;
USE sessiondb;

CREATE TABLE sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(64) NOT NULL,
    user_id INT,
    expires_at DATETIME
);

CREATE TABLE admin_users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    password VARCHAR(100) NOT NULL
);

CREATE TABLE flags (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    value VARCHAR(100) NOT NULL
);

INSERT INTO sessions (session_id, user_id, expires_at) VALUES
('sess_abc123', 1, DATE_ADD(NOW(), INTERVAL 1 DAY)),
('sess_xyz789', 2, DATE_ADD(NOW(), INTERVAL 1 DAY));

INSERT INTO admin_users (username, password) VALUES
('cookie_time', 'C00k13_T1m3_P@ss!');

INSERT INTO flags (name, value) VALUES
('sqli_033', 'FLAG{c00k13_t1m3_bl1nd}');
