CREATE TABLE metrics (id SERIAL PRIMARY KEY, name VARCHAR(100), value DECIMAL(10,2), recorded_at TIMESTAMP DEFAULT NOW());
INSERT INTO metrics (name, value) VALUES ('PageViews', 15420.00), ('Visitors', 3240.00), ('Conversions', 145.50);
CREATE TABLE secrets (id SERIAL PRIMARY KEY, name VARCHAR(100), value VARCHAR(255));
INSERT INTO secrets (name, value) VALUES ('sqli_018', 'FLAG{chr_c0nc4t_p0stgr3sql}');
