-- Test tables for the clickzetta-ossie-interop live test (schema ossie_skill_test)
CREATE TABLE ossie_skill_test.customers (customer_id BIGINT, customer_name STRING, region STRING, signup_date DATE);
CREATE TABLE ossie_skill_test.products (product_id BIGINT, product_name STRING, category STRING);
CREATE TABLE ossie_skill_test.orders (order_id BIGINT, customer_id BIGINT, order_date DATE, status STRING, order_ts TIMESTAMP);
CREATE TABLE ossie_skill_test.order_items (order_id BIGINT, line_no INT, product_id BIGINT, quantity INT, unit_price DECIMAL(12,2));
INSERT INTO ossie_skill_test.customers VALUES (1, 'Acme', 'EAST', DATE '2024-01-15'), (2, 'Globex', 'WEST', DATE '2025-03-02'), (3, 'Initech', 'EAST', DATE '2025-07-20');
INSERT INTO ossie_skill_test.products VALUES (10, 'Widget', 'HARDWARE'), (11, 'Gadget', 'HARDWARE'), (12, 'Support plan', 'SERVICE');
INSERT INTO ossie_skill_test.orders VALUES (100, 1, DATE '2026-01-05', 'COMPLETED', TIMESTAMP '2026-01-05 10:00:00'), (101, 1, DATE '2026-02-11', 'COMPLETED', TIMESTAMP '2026-02-11 09:30:00'), (102, 2, DATE '2026-02-20', 'CANCELLED', TIMESTAMP '2026-02-20 16:45:00'), (103, 3, DATE '2026-03-03', 'COMPLETED', TIMESTAMP '2026-03-03 12:00:00');
INSERT INTO ossie_skill_test.order_items VALUES (100, 1, 10, 5, 20.00), (100, 2, 12, 1, 300.00), (101, 1, 11, 2, 45.50), (102, 1, 10, 1, 20.00), (103, 1, 11, 10, 45.50), (103, 2, 12, 1, 300.00);
