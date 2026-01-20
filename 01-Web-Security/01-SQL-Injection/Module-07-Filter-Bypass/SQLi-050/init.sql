-- SQLi-050: MSSQL Double URL Encoding

CREATE DATABASE searchdb;
GO
USE searchdb;
GO

CREATE TABLE products (
    id INT PRIMARY KEY IDENTITY(1,1),
    name NVARCHAR(100),
    description NVARCHAR(500)
);

CREATE TABLE flags (
    id INT PRIMARY KEY IDENTITY(1,1),
    name NVARCHAR(50),
    value NVARCHAR(100)
);

INSERT INTO products (name, description) VALUES
('Laptop', 'High-performance laptop'),
('Phone', 'Smartphone with camera');

INSERT INTO flags (name, value) VALUES
('sqli_050', 'FLAG{d0ubl3_url_3nc0d1ng_byp4ss}');
GO
