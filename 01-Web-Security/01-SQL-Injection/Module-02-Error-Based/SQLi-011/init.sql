USE blogdb;
CREATE TABLE articles (id INT AUTO_INCREMENT PRIMARY KEY, title VARCHAR(255), content TEXT, author VARCHAR(100), created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE flags (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(100), value VARCHAR(255));

-- Insert Flag chuẩn
INSERT INTO flags (name, value) VALUES ('sqli_011', 'FLAG{d0ubl3_qu3ry_fl00r_r4nd_m4st3r}');

-- Insert dữ liệu mồi (Seed Data)
INSERT INTO articles (title, content, author) VALUES ('A', 'B', 'C');
INSERT INTO articles (title, content, author) VALUES ('A', 'B', 'C');
INSERT INTO articles (title, content, author) VALUES ('A', 'B', 'C');

-- Nhân bản dữ liệu lên gấp nhiều lần (Exponential growth)
INSERT INTO articles (title, content, author) SELECT title, content, author FROM articles; -- 3 -> 6
INSERT INTO articles (title, content, author) SELECT title, content, author FROM articles; -- 6 -> 12
INSERT INTO articles (title, content, author) SELECT title, content, author FROM articles; -- 12 -> 24
INSERT INTO articles (title, content, author) SELECT title, content, author FROM articles; -- 24 -> 48
INSERT INTO articles (title, content, author) SELECT title, content, author FROM articles; -- 48 -> 96
-- Lúc này bảng articles đã có gần 100 dòng, ĐỦ ĐỂ CRASH.