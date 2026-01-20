-- SQLi-041: PostgreSQL OOB DNS via COPY TO PROGRAM

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100),
    role VARCHAR(20) DEFAULT 'user'
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

INSERT INTO users (username, email, role) VALUES
('john_doe', 'john@example.com', 'user'),
('jane_smith', 'jane@example.com', 'admin'),
('bob_wilson', 'bob@example.com', 'user');

INSERT INTO admin_creds (username, password) VALUES
('pg_admin', 'PgAdm1n_S3cur3!'),
('dba_user', 'DBA_P@ssw0rd');

INSERT INTO flags (name, value) VALUES
('sqli_041', 'FLAG{postgres_copy_to_program_dns}');
