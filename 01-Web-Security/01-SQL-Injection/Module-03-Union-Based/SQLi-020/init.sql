-- =====================================================
-- SQLi-020: Union-based SQLi - Single Column (Oracle)
-- Kỹ thuật: || operator để concatenate, FROM dual
-- =====================================================

-- Connect to XEPDB1
ALTER SESSION SET CONTAINER = XEPDB1;

-- Bảng invoices - Chỉ hiển thị invoice_number
CREATE TABLE app_user.invoices (
    id NUMBER PRIMARY KEY,
    invoice_number VARCHAR2(20) NOT NULL,
    amount NUMBER(10,2) NOT NULL,
    customer VARCHAR2(100),
    status VARCHAR2(20) DEFAULT 'PENDING',
    created_date DATE DEFAULT SYSDATE
);

-- Bảng customers - Thông tin khách hàng
CREATE TABLE app_user.customers (
    id NUMBER PRIMARY KEY,
    name VARCHAR2(100) NOT NULL,
    email VARCHAR2(100),
    phone VARCHAR2(20),
    address VARCHAR2(200)
);

-- Bảng admin_users - Mục tiêu extraction
CREATE TABLE app_user.admin_users (
    id NUMBER PRIMARY KEY,
    username VARCHAR2(50) NOT NULL,
    password VARCHAR2(100) NOT NULL,
    role VARCHAR2(20) DEFAULT 'admin'
);

-- Bảng secrets - Chứa flag
CREATE TABLE app_user.secrets (
    id NUMBER PRIMARY KEY,
    name VARCHAR2(50) NOT NULL,
    value VARCHAR2(100) NOT NULL
);

-- =====================================================
-- INSERT DATA
-- =====================================================

-- Invoices data
INSERT INTO app_user.invoices (id, invoice_number, amount, customer, status) VALUES
(1, 'INV-2024-001', 1500.00, 'Acme Corporation', 'PAID');
INSERT INTO app_user.invoices (id, invoice_number, amount, customer, status) VALUES
(2, 'INV-2024-002', 2300.50, 'TechStart Inc', 'PENDING');
INSERT INTO app_user.invoices (id, invoice_number, amount, customer, status) VALUES
(3, 'INV-2024-003', 890.00, 'Global Services', 'PAID');
INSERT INTO app_user.invoices (id, invoice_number, amount, customer, status) VALUES
(4, 'INV-2024-004', 4500.00, 'Digital Solutions', 'OVERDUE');
INSERT INTO app_user.invoices (id, invoice_number, amount, customer, status) VALUES
(5, 'INV-2024-005', 1200.75, 'Cloud Systems', 'PENDING');

-- Customers data
INSERT INTO app_user.customers (id, name, email, phone, address) VALUES
(1, 'Acme Corporation', 'billing@acme.com', '555-0101', '123 Business Ave');
INSERT INTO app_user.customers (id, name, email, phone, address) VALUES
(2, 'TechStart Inc', 'finance@techstart.io', '555-0102', '456 Tech Park');
INSERT INTO app_user.customers (id, name, email, phone, address) VALUES
(3, 'Global Services', 'accounts@globalsvcs.com', '555-0103', '789 Global Plaza');

-- Admin users - Target cho extraction
INSERT INTO app_user.admin_users (id, username, password, role) VALUES
(1, 'oracle_admin', 'Ora_Sup3r_S3cure!', 'superadmin');
INSERT INTO app_user.admin_users (id, username, password, role) VALUES
(2, 'db_manager', 'DB_M@nager_2024', 'admin');
INSERT INTO app_user.admin_users (id, username, password, role) VALUES
(3, 'billing_user', 'B1ll1ng_Us3r', 'user');

-- Flag
INSERT INTO app_user.secrets (id, name, value) VALUES
(1, 'sqli_020', 'FLAG{0r4cl3_p1p3_c0nc4t}');

COMMIT;

-- Grants
GRANT SELECT ON app_user.invoices TO app_user;
GRANT SELECT ON app_user.customers TO app_user;
GRANT SELECT ON app_user.admin_users TO app_user;
GRANT SELECT ON app_user.secrets TO app_user;
