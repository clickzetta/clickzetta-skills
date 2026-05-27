# Using SQL for Customer RFM Analysis

## What is RFM Analysis?

**RFM report is a method** to segment customers using three key metrics: Recency (how long ago they last purchased), Frequency (how often they purchase), and Monetary value (how much they spend).

**RFM analysis is based on the assumption that customers who have purchased from you recently are more likely to purchase again**. This principle applies to various industries, with evidence showing that frequent buyers and big spenders are more likely to respond to promotions compared to infrequent buyers or those who spend less.

**RFM** was created in the 1990s to improve the efficiency of direct mail marketing campaigns, utilizing the [Pareto Principle](https://mode.com/blog/pareto-chart-101/) to answer key questions such as:

* Who are my best or most loyal customers?
* Which customers am I at risk of losing?
* Which customers should I focus my marketing efforts on?
* Which customers can I encourage to spend more?

**This customer analysis can have a significant impact on your business**. Whether you want to improve marketing ROI, build loyalty, reduce churn, or increase CLV, RFM analysis is a step in the right direction.

Once you have a table with the Recency (R), Frequency (F), and Monetary value (M) data for each customer, you can start segmenting. While you can finely segment the data as needed, using quintiles reflects the Pareto Principle, indicating which of your customers are in the top 20% across all three metrics.
To create quintiles, we will use an ntile window function, which only requires adding a few extra lines of SQL on top of the original RFM value query.

## How to Create an RFM Report for Your Data

Because it focuses on just three metrics, the RFM report seems simple. For example, when performing RFM analysis on data, all you really need are three data points:

* **Recency (R**) - Last order date
* **Frequency (F**) - Total number of orders
* **Monetary value (M**) - Total expenditure

**These metrics together reveal who your repeat customers are, which customers are the most loyal over time, and which customers spend the most in your store**. RFM reports provide important information about your customers, and while RFM is closely associated with B2C and retail, it is equally effective for B2B, service, or SaaS businesses to better understand their customers.

### Data Description

The data used in this article comes from the shared sample data of Singdata Lakehouse and can be used directly as follows:

```
select * from clickzetta_sample_data.ecommerce_events_history.ecommerce_events_multicategorystore;
```

![](.topwrite/assets/image_1718761578596.png)

### Creating Values Needed for RFM

```
DROP TABLE if exists eCommerce_RFM_Values;

CREATE TABLE eCommerce_RFM_Values

AS

SELECT user_id,

MIN(event_date) AS first_order_date,

MAX(event_date) AS last_order_date,

COUNT(1) AS count_order,

sum(price) AS sum_amount

FROM clickzetta_sample_data.ecommerce_events_history.ecommerce_events_multicategorystore

WHERE event_type = 'purchase'

GROUP BY user_id

ORDER BY user_id;
```

### Create RFM Quintiles

In this article, for simplicity, we use two quantiles (ntile(2) instead of ntile(5)). This query returns a table that includes customer emails and the respective quantiles for each customer in terms of recency, frequency, and monetary value. From a recency perspective, 2 indicates that the customer's purchase is within the most recent 50%, while 1 indicates that the customer is in the latter 50%.

```
DROP TABLE if exists eCommerce_RFM_Quintiles;

CREATE TABLE eCommerce_RFM_Quintiles

AS

SELECT user_id,

ntile(2) OVER (ORDER BY last_order_date) AS rfm_recency,

ntile(2) OVER (ORDER BY count_order) AS rfm_frequency,

ntile(2) OVER (ORDER BY sum_amount) AS rfm_monetary,

first_order_date,

last_order_date,

count_order,

sum_amount

FROM eCommerce_RFM_Values

ORDER BY user_id;
```

### Create RFM Cells

Now that you know where your customers usually belong, let's make the quintile data easier to use. The most common way is to concatenate the quintile ranks of each metric to create a 3-digit number, also known as a "cell".
When concatenating data in this way, the cell value for the best customers is 222 (quintile is 555), because they are in the top 50% in all three metrics, while the cell value for customers in the bottom 50% in all three metrics is 111.

```
DROP TABLE if exists eCommerce_RFM_Cell;
CREATE TABLE eCommerce_RFM_Cell

AS

SELECT user_id,

rfm_recency,

rfm_frequency,

rfm_monetary,

rfm_recency || rfm_frequency || rfm_monetary AS rfm_cell,

first_order_date,

last_order_date,

count_order,

sum_amount

FROM eCommerce_RFM_Quintiles

ORDER BY user_id;
```

### Create Actionable RFM Segments

Now that you have clear RFM cells, you need to create meaningful segments to help turn data into actionable insights. With three metrics and five levels for each metric, you can create up to 125 (5x5x5) customer segments. If the idea of 125 segments gives you a headache, consider using quartiles (which will give you 4x4x4 = 64 segments) or even tertiles (3x3x3 = 27 segments) to simplify things.

How you divide the segments depends on the nature of your business. If you are a hardcore fan of Pareto and want to reward your best buyers, you might want to focus on customers with an RFM cell of 555. However, if you want to be a bit more inclusive and include recent and frequent buyers who may spend a little less, you can create a segment that includes everyone with RFM cell values of 555 and 554.

The key to creating customer segments is to make the buckets large enough to be actionable—if marketers think they need to create 125 separate customer marketing campaigns, they will lose their minds—but small enough that you can handle them as a whole.

The key to creating customer segments is to make the buckets large enough to be actionable but small enough that you can handle them as a group.

```
DROP TABLE if exists eCommerce_RFM_Segment;

CREATE TABLE eCommerce_RFM_Segment

AS

SELECT user_id AS rfm_user_id,

rfm_recency,

rfm_frequency,

rfm_monetary,

rfm_recency || rfm_frequency || rfm_monetary AS rfm_cell,

CASE

WHEN rfm_cell IN ('111') THEN 'General Retention Customer 111'

WHEN rfm_cell IN ('112') THEN 'Important Retention Customer 112'

WHEN rfm_cell IN ('121') THEN 'General Maintenance Customer 121'

WHEN rfm_cell IN ('122') THEN 'Important Maintenance Customer 122'

WHEN rfm_cell IN ('211') THEN 'General Development Customer 211'

WHEN rfm_cell IN ('212') THEN 'Important Development Customer 212'

WHEN rfm_cell IN ('221') THEN 'General Value Customer 221'

WHEN rfm_cell IN ('222') THEN 'Important Value Customer 222'

ELSE 'Other'

END AS rfm_segment,

first_order_date as rfm_first_purchase_date,

last_order_date as rfm_last_purchase_date,

count_order as rfm_purchase_count,

sum_amount as rfm_purchase_amount_sum

FROM eCommerce_RFM_Cell

ORDER BY rfm_user_id;
```

^
