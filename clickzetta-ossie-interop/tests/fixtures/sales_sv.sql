-- Reference semantic view covering TABLES, RELATIONSHIPS, VARIABLES, FACTS, DIMENSIONS, METRICS,
-- PRIVATE, WITH SYNONYMS, is_unique, is_time, enum_values and COMMENT
CREATE OR REPLACE SEMANTIC VIEW ossie_skill_test.sales_sv
TABLES (
    customers AS ossie_skill_test.customers
        PRIMARY KEY (customer_id)
        WITH SYNONYMS ('client', 'buyer')
        COMMENT = 'Customer master',
    products AS ossie_skill_test.products
        PRIMARY KEY (product_id)
        COMMENT = 'Product catalog',
    orders AS ossie_skill_test.orders
        PRIMARY KEY (order_id)
        COMMENT = 'Order header',
    order_items AS ossie_skill_test.order_items
        PRIMARY KEY (order_id, line_no)
        COMMENT = 'Order lines'
)
RELATIONSHIPS (
    orders (customer_id) REFERENCES customers (customer_id),
    order_items (order_id) REFERENCES orders (order_id),
    order_items (product_id) REFERENCES products (product_id)
)
VARIABLES (
    min_amount DECIMAL(12,2) DEFAULT 100.00 COMMENT 'Threshold for BIG order lines'
)
FACTS (
    order_items.line_amount AS order_items.quantity * order_items.unit_price,
    PRIVATE order_items.raw_qty AS order_items.quantity
)
DIMENSIONS (
    customers.customer_name AS customers.customer_name
        WITH SYNONYMS = ('client name')
        is_unique = true
        COMMENT = 'Customer display name',
    customers.region AS customers.region
        enum_values = ['EAST', 'WEST', 'NORTH', 'SOUTH']
        COMMENT = 'Sales region',
    customers.signup_year AS YEAR(customers.signup_date)
        is_time = true
        COMMENT = 'Signup year',
    orders.order_date AS orders.order_date
        is_time = true
        COMMENT = 'Order date',
    orders.status AS orders.status
        COMMENT = 'Order status',
    products.category AS products.category
        COMMENT = 'Product category',
    order_items.size_band AS CASE WHEN order_items.quantity * order_items.unit_price >= min_amount THEN 'BIG' ELSE 'SMALL' END
        COMMENT = 'Order line size band'
)
METRICS (
    order_items.revenue AS SUM(order_items.quantity * order_items.unit_price)
        COMMENT = 'Total revenue',
    order_items.units AS SUM(order_items.quantity),
    order_items.avg_price AS order_items.revenue / order_items.units
        COMMENT = 'Revenue per unit',
    orders.order_count AS COUNT(DISTINCT orders.order_id)
        COMMENT = 'Number of orders',
    PRIVATE orders.raw_orders AS COUNT(orders.order_id),
    orders.completed_orders AS COUNT(orders.order_id) FILTER (WHERE orders.status = 'COMPLETED')
        COMMENT = 'Completed orders'
)
COMMENT = 'Ossie skill live test';
