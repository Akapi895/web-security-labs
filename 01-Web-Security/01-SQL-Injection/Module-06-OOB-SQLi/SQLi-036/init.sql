-- =====================================================
-- SQLi-036: MSSQL OOB DNS via xp_dirtree
-- Technique: xp_dirtree với UNC path để DNS exfil
-- =====================================================

CREATE DATABASE corpintranet;
GO

USE corpintranet;
GO

CREATE TABLE employees (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(100) NOT NULL,
    department NVARCHAR(50),
    email NVARCHAR(100),
    salary DECIMAL(10,2)
);
GO

CREATE TABLE admin_accounts (
    id INT IDENTITY(1,1) PRIMARY KEY,
    username NVARCHAR(50) NOT NULL,
    password NVARCHAR(100) NOT NULL,
    role NVARCHAR(20) DEFAULT 'admin'
);
GO

CREATE TABLE secrets (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(50) NOT NULL,
    value NVARCHAR(200) NOT NULL
);
GO

CREATE TABLE audit_log (
    id INT IDENTITY(1,1) PRIMARY KEY,
    action NVARCHAR(100),
    timestamp DATETIME DEFAULT GETDATE()
);
GO

INSERT INTO employees (name, department, email, salary) VALUES
('John Smith', 'Engineering', 'john.smith@corp.local', 85000.00),
('Jane Doe', 'Marketing', 'jane.doe@corp.local', 72000.00),
('Bob Johnson', 'IT Security', 'bob.johnson@corp.local', 95000.00),
('Alice Williams', 'HR', 'alice.williams@corp.local', 68000.00),
('Charlie Brown', 'Finance', 'charlie.brown@corp.local', 78000.00);
GO

INSERT INTO admin_accounts (username, password, role) VALUES
('domain_admin', 'D0m@1n_Adm1n_2024!', 'superadmin'),
('sql_admin', 'SQL_S3rv3r_P@ss!', 'dbadmin'),
('backup_svc', 'B@ckup_Svc_Pwd', 'service');
GO

INSERT INTO secrets (name, value) VALUES
('sqli_036_flag', 'FLAG{mssql_xp_dirtree_oob}'),
('api_gateway_key', 'gw-key-a1b2c3d4e5f6'),
('encryption_key', 'AES256-key-secret-value');
GO

-- Enable xp_cmdshell for advanced exploitation (optional)
-- EXEC sp_configure 'show advanced options', 1;
-- RECONFIGURE;
-- EXEC sp_configure 'xp_cmdshell', 1;
-- RECONFIGURE;
GO
