IF NOT EXISTS (SELECT * FROM sys.databases WHERE name='corpdb') CREATE DATABASE corpdb;
GO
USE corpdb;
GO
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='employees') CREATE TABLE employees (id INT IDENTITY PRIMARY KEY, name NVARCHAR(100), department NVARCHAR(50), email NVARCHAR(100));
GO
INSERT INTO employees VALUES ('John Smith', 'IT', 'john@corp.local'), ('Jane Doe', 'HR', 'jane@corp.local'), ('Bob Wilson', 'Finance', 'bob@corp.local');
GO
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='secrets') CREATE TABLE secrets (id INT IDENTITY PRIMARY KEY, name NVARCHAR(100), value NVARCHAR(255));
GO
INSERT INTO secrets VALUES ('sqli_012', 'FLAG{mssql_c0nv3rt_c4st_3rr0r}');
GO
