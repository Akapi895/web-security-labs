-- =====================================================
-- SQLi-028: Boolean Blind via Dynamic Column (MSSQL)
-- Kỹ thuật: Column name parameter injection
-- =====================================================

CREATE DATABASE exportdb;
GO
USE exportdb;
GO

CREATE TABLE reports (
    id INT PRIMARY KEY IDENTITY(1,1),
    report_name NVARCHAR(100) NOT NULL,
    created_by NVARCHAR(50),
    created_date DATE DEFAULT GETDATE(),
    status NVARCHAR(20) DEFAULT 'draft'
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

INSERT INTO reports (report_name, created_by, status) VALUES
('Q1 Sales Report', 'alice', 'published'),
('Q2 Marketing Analysis', 'bob', 'draft'),
('Annual Summary', 'charlie', 'published'),
('Budget Forecast', 'david', 'review');
GO

INSERT INTO admin_users (username, password) VALUES
('mssql_admin', 'MSSQL_Adm1n_P@ss!'),
('export_user', 'Exp0rt_Us3r_2024');
GO

INSERT INTO flags (name, value) VALUES
('sqli_028', 'FLAG{dyn4m1c_c0lumn_bl1nd}');
GO
