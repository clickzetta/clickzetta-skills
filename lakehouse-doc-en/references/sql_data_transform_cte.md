# Data Transformation with CTE

Let's first understand the basic concepts, advantages, and common use cases of using [Common Table Expression (CTE)](WITH.md) with Lakehouse SQL for data transformation.

## Basic Concepts

A Common Table Expression (CTE) is an expression that defines a temporary result set that exists within the execution scope of a SQL query. It is typically used to simplify complex queries, perform recursive queries, or break down query steps. CTEs are usually introduced by the [WITH keyword](WITH.md) and can be used in subsequent `SELECT`, `INSERT`, `UPDATE`, and `DELETE` statements.

Basic syntax:
```sql
WITH cte_name AS (
    SELECT column1, column2, ...
    FROM table_name
    WHERE condition
)
SELECT * FROM cte_name;
```
## Advantages

1. **High Readability**: CTE can make complex queries more readable and maintainable. By breaking down complex query logic into multiple understandable parts, CTE enhances the structure and clarity of the query. CTE makes testing complex queries simpler.

   * CTE is a `SELECT` statement that can be reused within a single query.
   * Complex SQL queries often involve multiple subqueries. Multiple subqueries can make the code difficult to read.
   * Using Common Table Expressions (CTE) can make your queries more readable.

2. **Strong Reusability**: CTE can be referenced multiple times within the same query, thus avoiding code duplication and improving query reusability.

3. **Step-by-Step Data Transformation**: CTE allows the data transformation process to be implemented step by step, with each step defined as an independent CTE, making it easier to debug and test.

4. **Support for Recursive Queries**: CTE supports recursive queries, making it very suitable for handling recursive data structures with hierarchical relationships, such as tree-structured data.

## Usage Scenarios

Here are some common scenarios for data transformation using CTE:

### 1. Data Cleaning and Transformation

CTE can be used to clean and transform data step by step, such as removing duplicates and correcting data formats:
```sql
WITH cleaned_data AS (
    SELECT DISTINCT column1, column2
    FROM raw_table
    WHERE column1 IS NOT NULL
),
transformed_data AS (
    SELECT column1, UPPER(column2) AS transformed_column2
    FROM cleaned_data
)
SELECT * FROM transformed_data;
```
### 2. Grouping and Aggregation

CTE can be used for complex grouping and aggregation operations, and the aggregation results can be referenced in subsequent queries:
```sql
WITH total_sales AS (
    SELECT customer_id, SUM(order_amount) AS total_spent
    FROM orders
    GROUP BY customer_id
)
SELECT customer_id, total_spent
FROM total_sales
WHERE total_spent > 1000;
```

### 3. Data Merging and Joining

Using CTE can simplify multi-table joins and data merging operations:
```sql
WITH customer_orders AS (
    SELECT c.customer_id, c.customer_name, o.order_id, o.order_date
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
)
SELECT *
FROM customer_orders
WHERE order_date > '2024-01-01';
```
## Data Model

TPC-H data represents a data warehouse for an auto parts dealer, recording orders, items that make up the orders (lineitem), suppliers, customers, parts sold (part), regions, countries, and parts suppliers (partsupp).

Singdata Lakehouse has built-in shared TPC-H data, which each user can directly use by adding the data context, for example:
```sql
SELECT * FROM 
clickzetta_sample_data.tpch_100g.customer
LIMIT 10;
```
## Data Transformation Using Singdata Lakehouse SQL CTE

### How to Define CTE
```sql
-- CTE Definition
WITH
  supplier_nation_metrics AS ( -- Define CTE 1 using WITH keyword
    SELECT
      n.n_nationkey,
      SUM(l.l_QUANTITY) AS num_supplied_parts
    FROM
      clickzetta_sample_data.tpch_100g.lineitem l
      JOIN clickzetta_sample_data.tpch_100g.supplier s ON l.l_suppkey = s.s_suppkey
      JOIN clickzetta_sample_data.tpch_100g.nation n ON s.s_nationkey = n.n_nationkey
    GROUP BY
      n.n_nationkey
  ),
  buyer_nation_metrics AS ( -- Define CTE 2
    SELECT
      n.n_nationkey,
      SUM(l.l_QUANTITY) AS num_purchased_parts
    FROM
      clickzetta_sample_data.tpch_100g.lineitem l
      JOIN clickzetta_sample_data.tpch_100g.orders o ON l.l_orderkey = o.o_orderkey
      JOIN clickzetta_sample_data.tpch_100g.customer c ON o.o_custkey = c.c_custkey
      JOIN clickzetta_sample_data.tpch_100g.nation n ON c.c_nationkey = n.n_nationkey
    GROUP BY
      n.n_nationkey
  )
SELECT -- No comma needed before the final SELECT statement
  n.n_name AS nation_name,
  s.num_supplied_parts,
  b.num_purchased_parts
FROM
  clickzetta_sample_data.tpch_100g.nation n
  LEFT JOIN supplier_nation_metrics s ON n.n_nationkey = s.n_nationkey
  LEFT JOIN buyer_nation_metrics b ON n.n_nationkey = b.n_nationkey
LIMIT 10;
```
### Calculate the Amount Lost Due to Discounts

Use the `lineitem` table to get the price of items in the order (excluding discounts) and compare it with the order. First, determine the granularity of the comparison. Think step by step, first get the price of all items in the order excluding discounts, and then compare it with the order data of `totalprice` that has already calculated the discount.
```sql
WITH lineitem_agg AS (
    SELECT 
        l_orderkey,
        SUM(l_extendedprice) AS total_price_without_discount
    FROM 
        clickzetta_sample_data.tpch_100g.lineitem
    GROUP BY 
        l_orderkey
)
SELECT 
    o.o_orderkey,
    o.o_totalprice, 
    l.total_price_without_discount - o.o_totalprice AS amount_lost_to_discount
FROM 
    clickzetta_sample_data.tpch_100g.orders o
JOIN 
    lineitem_agg l ON o.o_orderkey = l.l_orderkey
ORDER BY 
    o.o_orderkey;
```
### Do not overuse CTE. Pay attention to code readability.

1. CTE can help improve the readability and reusability of queries.

2. Do not overuse CTE; pay attention to the size of the query.

   * SQL queries with multiple temporary tables are better than 1000-line SQL queries with numerous CTEs.
   * Keep the number of CTEs in each query small (depending on the size of the query, but usually < 5).

3. If you have doubts about the performance of CTE, check your query plan.

## Resources

[Common Table Expression (CTE)](WITH.md)

^