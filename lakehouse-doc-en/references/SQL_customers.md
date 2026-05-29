# Use SQL Tasks to Calculate New Customers, Active Customers, and Churned Customers

In business operations, users are typically segmented based on their behavioral characteristics, and targeted operational actions are taken for different segments to drive user conversion. In most scenarios, users are divided into new customers, active customers, and churned customers.

* New customers: Refers to the number of users who have newly registered within a specific time period, usually used to measure the speed and attractiveness of user growth.
* Active customers: Refers to the number of users who have actual usage behavior within a specific time period, usually used to measure user engagement and retention.
* Churned customers: Refers to users who do not visit the product within a specific time period. Companies should minimize the proportion of churned users to reduce the cost of re-engaging users.

In this tutorial, we will analyze retention rates based on the "e-commerce dataset."

### Step 1: Create an order sequence column specific to each customer ID based on the ascending order date of each customer.

```SQL
DROP TABLE if exists eCommerce_LifeCycle_Order_Sequence;
CREATE TABLE eCommerce_LifeCycle_Order_Sequence 
AS
SELECT event_date,
       user_id,
       ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY event_date ASC) AS customer_order_sequence,
       LAG(event_date) OVER (PARTITION BY user_id ORDER BY user_id ASC) AS previous_order_date,
       MIN(event_date) AS first_order_date,
       MAX(event_date) AS last_order_date
FROM clickzetta_sample_data.ecommerce_events_history.ecommerce_events_multicategorystore_enriched
WHERE event_type = 'purchase'
GROUP BY event_date,
         user_id;
```

### Step 2: Create a new column to insert the previous order date for the customer ID, to be used in later code blocks to calculate the time period between orders

```SQL
DROP TABLE if exists eCommerce_LifeCycle_Time_Between_Orders;
CREATE TABLE eCommerce_LifeCycle_Time_Between_Orders 
AS
SELECT event_date,
       user_id,
       customer_order_sequence,
       CASE
         WHEN previous_order_date IS NULL THEN event_date
         ELSE previous_order_date
       END AS previous_order_date,
       DATEDIFF(event_date,previous_order_date) AS days_between_orders,
       first_order_date,
       last_order_date
FROM eCommerce_LifeCycle_Order_Sequence;
```

### Step 3: Use the CASE statement to create an additional customer\_life\_cycle column to indicate whether the order is from a new customer, an active customer, or a lapsed customer based on the days\_between\_orders column. In this example, if the order occurs anytime between 1 to 365 days from the previous order, the customer is considered an active customer; if the previous order exceeds 365 days, the customer is considered a lapsed customer.

```SQL
DROP TABLE if exists eCommerce_LifeCycle;
CREATE TABLE eCommerce_LifeCycle 
AS
SELECT event_date,
       user_id,
       CASE
         WHEN customer_order_sequence = 1 THEN 'New Customer'
         WHEN days_between_orders > 0 AND days_between_orders < 30 THEN 'Active Customer'
         WHEN days_between_orders > 30 THEN 'Dormant Customer'
         ELSE 'Unknown'
       END AS customer_life_cycle,
       customer_order_sequence,
       previous_order_date,
       CASE
         WHEN days_between_orders IS NULL THEN 0
         ELSE days_between_orders
       END AS days_between_orders,
       first_order_date,
       last_order_date
FROM eCommerce_LifeCycle_Time_Between_Orders;
```

^
