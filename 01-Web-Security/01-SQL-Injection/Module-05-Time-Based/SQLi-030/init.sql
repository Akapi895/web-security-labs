-- =====================================================
-- SQLi-030: Time-based Blind (MSSQL)
-- Kỹ thuật: WAITFOR DELAY
-- =====================================================

CREATE DATABASE emaildb;
GO
USE emaildb;
GO

CREATE TABLE email_subscribers (
    id INT PRIMARY KEY IDENTITY(1,1),
    email NVARCHAR(100) NOT NULL,
    is_verified BIT DEFAULT 0
);
GO

CREATE TABLE admin_users (
    id INT PRIMARY KEY IDENTITY(1,1),
    username NVARCHAR(50) NOT NULL,
    password NVARCHAR(100) NOT NULL
);
GO

CREATE TABLE flags (
    id INT PRIMARY KEY IDENTITY(1,1),
    name NVARCHAR(50) NOT NULL,
    value NVARCHAR(100) NOT NULL
);
GO

INSERT INTO email_subscribers (email, is_verified) VALUES
('user1@test.com', 1),
('user2@test.com', 0),
('admin@corp.com', 1);
GO

INSERT INTO admin_users (username, password) VALUES
('mssql_admin', 'MSSQL_W41tF0r_P@ss!'),
('delay_user', 'D3l4y_Us3r_2024');
GO

INSERT INTO flags (name, value) VALUES
('sqli_030', 'FLAG{w41tf0r_d3l4y_mssql}');
GO
