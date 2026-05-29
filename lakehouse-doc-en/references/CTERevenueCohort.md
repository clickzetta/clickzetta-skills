# Customer Cohort Analysis Using CTE

## CTE

[CTE(Common Table Expression) ](WITH.md), Common Table Expression, is a temporary result set defined within the scope of a single statement execution, only valid during the query. It can be self-referencing and can be referenced multiple times within the same query, achieving code reuse.

## Cohort (Revenue Cohort)

Cohort (Revenue Cohort) analysis is the analysis of several different cohorts (i.e., customer groups) to better understand behaviors, patterns, and trends.
One of the most common types of cohort analysis focuses on time-based cohorts, which group users/customers by a specific time range. For example, a company might want to understand how customers who started using the product or started paying in January compare to those in February.
Segment-based cohorts represent customer groups that use or purchase a specific product or service. For example, you can segment users based on the time they log into your app each week.
Another type of cohort is value-based cohorts, which segment customers by monetary value. This is common practice in the gaming industry (free users vs. whale users) or the SaaS world, segmenting customers by their LTV or plan.
For the rest of this article, we will focus only on implementing time-based revenue cohort analysis.
Data required for cohort analysis, before starting cohort analysis, the following data is needed:
\*     Revenue data associated with purchase data
\*     A unique identifier for users, such as customer ID or account ID
\*     The initial start date for each user, whether it is the registration date or the first payment date.

## Data Description

The data used in this article comes from the shared sample data of Singdata Lakehouse, which can be used directly as follows:

```
select * from clickzetta_sample_data.ecommerce_events_history.ecommerce_events_multicategorystore;
```

![](.topwrite/assets/image_1718761578596.png)

## Analysis Steps

1. Temporary result set user\_cohorts: First, we want to group users—in this case, we want to group them by their Order Week.
2. Temporary result set order\_Week: Next, we need to create an order\_month variable. For example, the value of order\_month2 is the payment made by the customer one month after the first payment. Create an order\_Week variable. For example, the value of order\_Week is 2 for the payment made by the customer one week after the first payment.
3. Temporary result set cohort\_size: Furthermore, we can now aggregate the revenue created in the first step of cohortMonth. This will allow us to create our retention\_table. Aggregate the revenue created in the first step of cohortMonth. This will allow us to create our retention\_table.
   The analysis model is constructed as follows:

```
WITH 
eCommerce_LifeCycle_Order_Sequence AS (
SELECT event_date,
       user_id,
       ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY event_date ASC) AS customer_order_sequence,
       LAG(event_date) OVER (PARTITION BY user_id ORDER BY user_id ASC) AS previous_order_date,
       MIN(event_date) AS first_order_date,
       MAX(event_date) AS last_order_date
FROM clickzetta_sample_data.ecommerce_events_history.ecommerce_events_multicategorystore
WHERE event_type = 'purchase'
GROUP BY event_date,
         user_id)
,
eCommerce_LifeCycle_Time_Between_Orders AS (
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
FROM eCommerce_LifeCycle_Order_Sequence)
,
eCommerce_LifeCycle AS(
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
FROM eCommerce_LifeCycle_Time_Between_Orders)
select * from eCommerce_LifeCycle;
```

Run the above SQL code, the result is as follows:
![](.topwrite/assets/image_1718761957078.png)

You can also directly write the result into the target table in the following way:

```
DROP TABLE if exists eCommerce_User_Cohort;

CREATE TABLE if not exists eCommerce_User_Cohort

AS

-- Group users. In this example, we want to group them by their Order Date

with user_cohorts as (

SELECT user_id

, MIN(weekofyear(event_date)) as cohortWeek

FROM clickzetta_sample_data.ecommerce_events_history.ecommerce_events_multicategorystore

WHERE CAST(event\_type as string) = 'purchase'

GROUP BY 1

--LIMIT 100

),

-- Create an order_Week variable. For example, the order_Week value for a payment made by a customer one week after their first payment is 2.

order_Week as (

SELECT eed.user_id

, (weekofyear(event_date)-cohortWeek+1) as Week_number

, SUM(price) as revenue

FROM ecommerce_events_multicategorystore_enriched eed

LEFT JOIN user_cohorts u on eed.user_id=u.user_id --USING(user_id)

WHERE CAST(event_type as string) = 'purchase'

GROUP BY 1, 2

--LIMIT 100

),

-- Summarize the revenue created in the first step of cohortMonth. This will allow us to create our retention_table.

cohort_size as (

SELECT sum(price) as revenue

, cohortWeek

FROM ecommerce_events_multicategorystore_enriched eed

LEFT JOIN user_cohorts u on eed.user_id=u.user_id --USING (user_id)

WHERE CAST(event_type as string) = 'purchase'

GROUP BY 2

ORDER BY 2

--LIMIT 100

),

retention_table as (

SELECT c.cohortWeek

, o.Week_number

, sum(revenue) as revenue

FROM order_Week o

LEFT JOIN user_cohorts c on c.user_id=o.user_id 

GROUP BY 1, 2

)

SELECT r.cohortWeek

, s.revenue as totalRevenue

, r.Week_number

, r.revenue / s.revenue as percentage

FROM retention_table r

LEFT JOIN cohort_size s on r.cohortWeek=s.cohortWeek 

WHERE r.cohortWeek IS NOT NULL

ORDER BY 1, 3;

```

## Review: Physical Table Method

Without using CTE, but instead making each subquery result into a physical table, the entire process is as follows:

1. Create an order sequence column specific to each customer ID based on the ascending order date of each customer. This is what the ROW\_NUMBER analytic function does in the query below.
2. Create a new column to insert the previous order date for the customer ID, so it can be used in later code blocks to calculate the time period between orders. This is what the LAG analytic function does in the following query.
   – Note the "Group By" order\_date and customer\_id columns at the end of the statement. This is important because customers can have multiple orders with different order IDs on the same day.

```
DROP TABLE if exists eCommerce_LifeCycle_Order_Sequence;
CREATE TABLE eCommerce_LifeCycle_Order_Sequence 
AS
SELECT event_date,
       user_id,
       ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY event_date ASC) AS customer_order_sequence,
       LAG(event_date) OVER (PARTITION BY user_id ORDER BY user_id ASC) AS previous_order_date,
       MIN(event_date) AS first_order_date,
       MAX(event_date) AS last_order_date
FROM clickzetta_sample_data.ecommerce_events_history.ecommerce_events_multicategorystore
WHERE event_type = 'purchase'
GROUP BY event_date,
         user_id;
```

To calculate the number of days between the order\_date and previous\_order\_date columns by running a subquery on the above table, you will see that the DATE\_DIFF function, which creates the new column days\_between\_orders, will do this.

```
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

The next query uses a CASE statement to create an additional customer\_life\_cycle column to indicate whether the order is from a new customer, an active customer, or a lapsed customer based on the days\_between\_orders column. In this example, if the order occurs anytime between 1 to 365 days from the previous order, the customer is considered active; if the previous order exceeds 365 days, the customer is considered lapsed. This is highly business-specific, so yours may vary.

```
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

```
select * from eCommerce_LifeCycle limit 100;
```

## Congratulations, it's done.

Please enjoy and learn more!

## Appendix

### Download Zeppelin Notebook source file

The code in this article is also available in a version that runs on [Zeppelin](eco_integration/Zeppelin.md). If you want to run the code in this article directly, please follow the documentation to install [Zeppelin](eco_integration/Zeppelin.md).

[03.CTE(Common Table Expression)..ipynb](https://github.com/yunqiqiliang/clickzetta_quickstart/blob/main/zeppelin_notebook/03.CTE\(Common%20Table%20Expression\)..ipynb)
[03.CTE(Common Table Expression)\_2JHUJ5BP8.zpln](https://github.com/yunqiqiliang/clickzetta_quickstart/blob/main/zeppelin_notebook/03.CTE\(Common%20Table%20Expression\)_2JHUJ5BP8.zpln)
