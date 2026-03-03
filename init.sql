DROP TABLE IF EXISTS members;
CREATE TABLE members (
    id SERIAL PRIMARY KEY,        
    member_id INT UNIQUE NOT NULL
);
CREATE INDEX idx_member_id ON members (member_id);

DROP TABLE IF EXISTS items;
CREATE TABLE items (
    id SERIAL PRIMARY KEY,
    item_name VARCHAR(255) UNIQUE NOT NULL,
    cat_level_1 VARCHAR(255),
    cat_level_2 VARCHAR(255),
    cat_level_3 VARCHAR(255)
);
CREATE INDEX idx_items_name ON items(item_name);

DROP TABLE IF EXISTS visits;
CREATE TABLE visits (
    id SERIAL PRIMARY KEY,
    member_id INT NOT NULL REFERENCES members(member_id),
    visit_date DATE NOT NULL,
    UNIQUE(member_id, visit_date)
);
CREATE INDEX idx_visit_date ON visits(visit_date);

DROP TABLE IF EXISTS sales;
CREATE TABLE sales (
    id SERIAL PRIMARY KEY,
    visit_id INT REFERENCES visits(id),
    item_name VARCHAR(255) REFERENCES items(item_name)
);
CREATE INDEX idx_sales_visit_id ON sales(visit_id);