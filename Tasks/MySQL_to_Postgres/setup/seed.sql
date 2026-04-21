-- Initial state for the MySQL → Postgres migration task.
-- This file is mounted into the MySQL init directory and runs on first boot.

CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE products (
    id INT PRIMARY KEY AUTO_INCREMENT,
    sku VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    stock INT NOT NULL DEFAULT 0
);

CREATE TABLE orders (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    total DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE order_items (
    id INT PRIMARY KEY AUTO_INCREMENT,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

INSERT INTO users (email, name) VALUES
    ('alice@example.com', 'Alice Johnson'),
    ('bob@example.com',   'Bob Smith'),
    ('carol@example.com', 'Carol Davis'),
    ('dave@example.com',  'Dave Wilson'),
    ('eve@example.com',   'Eve Brown');

INSERT INTO products (sku, name, price, stock) VALUES
    ('SKU-001', 'Widget Pro',       29.99, 100),
    ('SKU-002', 'Gadget Plus',      49.99,  50),
    ('SKU-003', 'Thingamajig',      19.99, 200),
    ('SKU-004', 'Doohickey',         9.99, 500),
    ('SKU-005', 'Whatchamacallit', 199.99,  10),
    ('SKU-006', 'Gizmo Deluxe',     79.99,  25),
    ('SKU-007', 'Contraption',      39.99,  75),
    ('SKU-008', 'Apparatus',       129.99,  15);

INSERT INTO orders (user_id, status, total) VALUES
    (1, 'completed',  59.98),
    (1, 'completed',  19.99),
    (2, 'pending',    49.99),
    (2, 'completed', 199.99),
    (3, 'shipped',    89.98),
    (3, 'completed',   9.99),
    (4, 'cancelled',  39.99),
    (4, 'shipped',   189.96),
    (5, 'completed',  79.99),
    (5, 'pending',    29.99);

INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES
    (1,  1, 2,  29.99),
    (2,  3, 1,  19.99),
    (3,  2, 1,  49.99),
    (4,  5, 1, 199.99),
    (5,  6, 1,  79.99),
    (5,  4, 1,   9.99),
    (6,  4, 1,   9.99),
    (7,  7, 1,  39.99),
    (8,  8, 1, 129.99),
    (8,  4, 2,   9.99),
    (8,  7, 1,  39.99),
    (9,  6, 1,  79.99),
    (10, 1, 1,  29.99);
