-- SQLi-047: MSSQL Double Keyword Bypass

CREATE DATABASE employeedb;
GO
USE employeedb;
GO

CREATE TABLE employees (
    id INT PRIMARY KEY IDENTITY(1,1),
    name NVARCHAR(100) NOT NULL,
    department NVARCHAR(50),
    salary DECIMAL(10,2)
);

CREATE TABLE admin_users (
    id INT PRIMARY KEY IDENTITY(1,1),
    username NVARCHAR(50),
    password NVARCHAR(100)
);

CREATE TABLE flags (
    id INT PRIMARY KEY IDENTITY(1,1),
    name NVARCHAR(50),
    value NVARCHAR(100)
);

INSERT INTO employees (name, department, salary) VALUES
('John Smith', 'Engineering', 85000.00),
('Jane Doe', 'Marketing', 72000.00),
('Bob Wilson', 'Sales', 68000.00);

INSERT INTO admin_users (username, password) VALUES
('sysadmin', 'D0ubl3_Kw_Byp4ss!'),
('dbadmin', 'Db@dm1n_P@ss');

INSERT INTO flags (name, value) VALUES
('sqli_047', 'FLAG{mssql_d0ubl3_k3yw0rd_byp4ss}');
GO
