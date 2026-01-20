-- =====================================================
-- SQLi-037: MSSQL OOB DNS via xp_fileexist/xp_subdirs
-- =====================================================

CREATE DATABASE reporting;
GO

USE reporting;
GO

CREATE TABLE reports (
    id INT IDENTITY(1,1) PRIMARY KEY,
    title NVARCHAR(100) NOT NULL,
    category NVARCHAR(50),
    created_date DATE DEFAULT GETDATE()
);
GO

CREATE TABLE users (
    id INT IDENTITY(1,1) PRIMARY KEY,
    username NVARCHAR(50) NOT NULL,
    password NVARCHAR(100) NOT NULL,
    department NVARCHAR(50)
);
GO

CREATE TABLE flags (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(50) NOT NULL,
    value NVARCHAR(100) NOT NULL
);
GO

INSERT INTO reports (title, category) VALUES
('Q4 Sales Report', 'Sales'),
('Annual Security Audit', 'Security'),
('Employee Performance', 'HR'),
('IT Infrastructure Review', 'IT'),
('Budget Analysis 2024', 'Finance');
GO

INSERT INTO users (username, password, department) VALUES
('report_admin', 'R3p0rt_Adm1n!', 'Reports'),
('analyst', 'An@lyst_2024', 'Analytics'),
('viewer', 'V13w3r_Only', 'General');
GO

INSERT INTO flags (name, value) VALUES
('sqli_037', 'FLAG{mssql_xp_fileexist_oob}');
GO
