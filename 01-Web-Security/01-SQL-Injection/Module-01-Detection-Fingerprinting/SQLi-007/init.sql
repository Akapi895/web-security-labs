IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'apidb')
BEGIN CREATE DATABASE apidb; END
GO
USE apidb;
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='users' AND xtype='U')
CREATE TABLE users (id INT IDENTITY(1,1) PRIMARY KEY, username NVARCHAR(50), email NVARCHAR(100), status NVARCHAR(20));
GO

INSERT INTO users VALUES ('john', 'john@example.com', 'active'), ('jane', 'jane@example.com', 'active'), ('admin', 'admin@example.com', 'active');
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='flags' AND xtype='U')
CREATE TABLE flags (id INT IDENTITY(1,1) PRIMARY KEY, name NVARCHAR(100), value NVARCHAR(255));
GO

INSERT INTO flags VALUES ('sqli_007', 'FLAG{t1m3_b4s3d_mssql_f1ng3rpr1nt}');
GO
