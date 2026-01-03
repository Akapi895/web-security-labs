-- =====================================================
-- SQLi-022: Union-based SQLi - Multi Row (PostgreSQL)
-- Kỹ thuật: STRING_AGG() để aggregate nhiều rows
-- =====================================================

-- Bảng departments
CREATE TABLE departments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    location VARCHAR(100)
);

-- Bảng employees - Hiển thị multi-row
CREATE TABLE employees (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    department_id INT REFERENCES departments(id),
    position VARCHAR(50)
);

-- Bảng admin_credentials - Mục tiêu extraction
CREATE TABLE admin_credentials (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    password VARCHAR(100) NOT NULL,
    role VARCHAR(20) DEFAULT 'admin',
    session_token VARCHAR(64)
);

-- Bảng flags - Chứa flag
CREATE TABLE flags (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    value VARCHAR(100) NOT NULL
);

-- =====================================================
-- INSERT DATA
-- =====================================================

-- Departments
INSERT INTO departments (name, location) VALUES
('Engineering', 'Building A'),
('Marketing', 'Building B'),
('Human Resources', 'Building C'),
('Finance', 'Building D');

-- Employees - Multiple rows per department
INSERT INTO employees (name, email, department_id, position) VALUES
('Alice Johnson', 'alice@corp.local', 1, 'Senior Developer'),
('Bob Smith', 'bob@corp.local', 1, 'DevOps Engineer'),
('Carol Williams', 'carol@corp.local', 1, 'Tech Lead'),
('David Brown', 'david@corp.local', 1, 'Junior Developer'),
('Eve Davis', 'eve@corp.local', 2, 'Marketing Manager'),
('Frank Miller', 'frank@corp.local', 2, 'Content Creator'),
('Grace Wilson', 'grace@corp.local', 3, 'HR Manager'),
('Henry Taylor', 'henry@corp.local', 3, 'Recruiter'),
('Ivy Anderson', 'ivy@corp.local', 4, 'CFO'),
('Jack Thomas', 'jack@corp.local', 4, 'Accountant');

-- Admin credentials - Target cho extraction
INSERT INTO admin_credentials (username, password, role, session_token) VALUES
('sysadmin', 'P0stgr3s_Sup3r_Adm1n!', 'superadmin', 'sess_abc123def456ghi789jkl012mno345pqr678stu901'),
('dbadmin', 'DB_Adm1n_P@ssw0rd', 'admin', 'sess_xyz987wvu654tsr321qpo098nml765kji432fed109'),
('hr_admin', 'HR_Acc3ss_2024', 'admin', 'sess_qwe456rty789uio012pas345dfg678hjk901lzx234'),
('backup_user', 'B@ckup_Cr3d3nt1als!', 'backup', 'sess_mnb098vcx765zaq432wsx109edc876rfv543tgb210');

-- Flag
INSERT INTO flags (name, value) VALUES
('sqli_022', 'FLAG{str1ng_4gg_p0stgr3sql}');

-- =====================================================
-- GRANTS
-- =====================================================
GRANT SELECT ON ALL TABLES IN SCHEMA public TO postgres;
