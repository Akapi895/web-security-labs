CREATE TABLE items (id SERIAL PRIMARY KEY, name VARCHAR(100), description TEXT);
INSERT INTO items (name, description) VALUES ('Laptop', 'High-performance laptop'), ('Mouse', 'Wireless mouse'), ('Keyboard', 'Mechanical keyboard');
CREATE TABLE secrets (id SERIAL PRIMARY KEY, name VARCHAR(100), value VARCHAR(255));
INSERT INTO secrets (name, value) VALUES ('sqli_017', 'FLAG{p0stgr3sql_c4st_3rr0r}');
