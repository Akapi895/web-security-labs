IF NOT EXISTS (SELECT * FROM sys.databases WHERE name='empdb') CREATE DATABASE empdb;
GO
USE empdb;
GO
CREATE TABLE employees (id INT IDENTITY PRIMARY KEY, name NVARCHAR(100), salary DECIMAL(10,2));
INSERT INTO employees VALUES ('Alice',75000),('Bob',80000),('Charlie',90000);
GO
CREATE TABLE flags (id INT IDENTITY PRIMARY KEY, name NVARCHAR(100), value NVARCHAR(255));
INSERT INTO flags VALUES ('sqli_013', 'FLAG{xml_p4th_mult1pl3_r0ws}');
GO
