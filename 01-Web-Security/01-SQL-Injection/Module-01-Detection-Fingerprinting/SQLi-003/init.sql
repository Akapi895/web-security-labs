-- SQLi-003: Corporate Directory Database Setup (MSSQL)

-- Create database
IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'corporate')
BEGIN
    CREATE DATABASE corporate;
END
GO

USE corporate;
GO

-- Employees table
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='employees' AND xtype='U')
BEGIN
    CREATE TABLE employees (
        id INT IDENTITY(1,1) PRIMARY KEY,
        first_name NVARCHAR(50) NOT NULL,
        last_name NVARCHAR(50) NOT NULL,
        email NVARCHAR(100),
        department NVARCHAR(50),
        position NVARCHAR(100),
        phone NVARCHAR(20),
        hire_date DATE DEFAULT GETDATE()
    );
END
GO

-- Insert sample employees
INSERT INTO employees (first_name, last_name, email, department, position, phone) VALUES
('John', 'Smith', 'john.smith@corp.local', 'IT', 'Senior Developer', '555-0101'),
('Jane', 'Doe', 'jane.doe@corp.local', 'HR', 'HR Manager', '555-0102'),
('Mike', 'Johnson', 'mike.j@corp.local', 'IT', 'System Administrator', '555-0103'),
('Sarah', 'Williams', 'sarah.w@corp.local', 'Finance', 'Financial Analyst', '555-0104'),
('Robert', 'Brown', 'robert.b@corp.local', 'Marketing', 'Marketing Director', '555-0105'),
('Emily', 'Davis', 'emily.d@corp.local', 'IT', 'Security Engineer', '555-0106'),
('David', 'Wilson', 'david.w@corp.local', 'Sales', 'Sales Manager', '555-0107'),
('Lisa', 'Anderson', 'lisa.a@corp.local', 'HR', 'Recruiter', '555-0108'),
('James', 'Taylor', 'james.t@corp.local', 'IT', 'DevOps Engineer', '555-0109'),
('Amanda', 'Martinez', 'amanda.m@corp.local', 'Finance', 'CFO', '555-0110');
GO

-- Credentials table (for future labs)
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='credentials' AND xtype='U')
BEGIN
    CREATE TABLE credentials (
        id INT IDENTITY(1,1) PRIMARY KEY,
        username NVARCHAR(50) NOT NULL,
        password_hash NVARCHAR(255) NOT NULL,
        employee_id INT,
        is_admin BIT DEFAULT 0
    );
END
GO

INSERT INTO credentials (username, password_hash, employee_id, is_admin) VALUES
('admin', 'e10adc3949ba59abbe56e057f20f883e', 1, 1),
('jsmith', '5f4dcc3b5aa765d61d8327deb882cf99', 1, 0),
('jdoe', '25d55ad283aa400af464c76d713c07ad', 2, 0);
GO

-- Flags table (for CTF)
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='flags' AND xtype='U')
BEGIN
    CREATE TABLE flags (
        id INT IDENTITY(1,1) PRIMARY KEY,
        flag_name NVARCHAR(100),
        flag_value NVARCHAR(255)
    );
END
GO

INSERT INTO flags (flag_name, flag_value) VALUES
('sqli_003', 'FLAG{4r1thm3t1c_d3t3ct10n_mssql_m4st3r}');
GO
