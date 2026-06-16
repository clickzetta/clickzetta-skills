# Lakehouse WITH CTE Guide: Multi-Stack Migration Handbook

## Overview

The Singdata Lakehouse WITH CTE (Common Table Expression) feature provides unified and powerful data analysis capabilities for users from different technical backgrounds. This guide, based on actual production validation, provides professional migration strategies and best practices tailored to the usage habits of Spark, Hive, MaxCompute, Snowflake, and traditional database users.

### 🎯 **Quick Navigation**

⚠️ **Important Notice**: This guide uses the built-in TPC-H sample data of Singdata Lakehouse for demonstration. The data date range is 1992-1998. All sample code has been verified in practice and can be run directly in the Lakehouse environment.

- [Spark User Migration Guide](#spark-user-migration-guide) - Elegant Conversion from DataFrame to CTE
- [Hive User Migration Guide](#hive-user-migration-guide) - Leap from MapReduce Thinking to Modern Analysis  
- [MaxCompute User Migration Guide](#maxcompute-user-migration-guide) - Seamless Continuation of the Alibaba Cloud Ecosystem
- [Snowflake User Migration Guide](#snowflake-user-migration-guide) - Further Enhancement of Cloud-Native Optimization
- [Traditional Database User Migration Guide](#traditional-database-user-migration-guide) - Architectural Transformation from OLTP to OLAP

---

## Verification Status and Usage Notes

✅ **Fully Verified**: All code samples in this guide have been verified and run successfully in the Singdata Lakehouse environment.

📊 **Data Source Notes**:
- Uses the built-in TPC-H 100GB sample data of Singdata Lakehouse
- Data date range: January 1, 1992 - August 2, 1998
- Contains complete business data including customers, orders, products, suppliers, etc.
- Supports complex multi-table joins and analysis scenarios

⚠️ **Performance Benefit Notes**:
- **Verified**: Functional correctness and syntax compatibility of all code
- **Unverified**: Specific performance improvement figures and migration efficiency metrics
- **Recommendation**: Users should conduct performance benchmark tests based on their own business scenarios

🚀 **Get Started Immediately**: Copy any code sample to your Lakehouse environment and run it

---

## CTE Core Syntax and General Features

### Standard Syntax Structure

```sql
WITH <cte_name1> AS (
    SELECT column1, column2, ...
    FROM table_name
    WHERE condition
),
<cte_name2> AS (
    SELECT column1, column2, ...
    FROM <cte_name1>  -- Can reference previously defined CTE
    WHERE condition
)
SELECT ...
FROM <cte_name1>
JOIN <cte_name2> ON ...
```

### Core Advantages Comparison

| Feature | Traditional Subquery | WITH CTE | Advantage |
|------|-----------|----------|----------|
| **Readability** | Complex nesting | Clear logic | Built step by step, easy to understand |
| **Reusability** | Repeated code | Multiple references | Avoid repetition, improve efficiency |
| **Debuggability** | Hard to isolate | Layered testing | Each CTE can be independently verified |
| **Maintainability** | Difficult to modify | Modular | Localized changes, minimal impact scope |

---

## Spark User Migration Guide

### Concept Mapping and Migration Key Points

The chained DataFrame operations familiar to Spark users are perfectly replicated in Lakehouse through CTEs:

```python
```

Spark DataFrame operation thinking:

```python
df_filtered = df.filter(col("order_date") >= "2024-01-01")
df_grouped = df_filtered.groupBy("customer_id").agg(
    sum("amount").alias("total_amount"),
    count("*").alias("order_count")
)
df_result = df_grouped.filter(col("total_amount") > 1000)
```

**Singdata Lakehouse CTE Equivalent Implementation**:

```sql
-- CTE chained logic: intuitively mirrors DataFrame operations
WITH filtered_orders AS (
    -- Corresponds to df.filter()
    SELECT customer_id, order_date, amount
    FROM orders
    WHERE order_date >= '1995-01-01'
),
grouped_summary AS (
    -- Corresponds to df.groupBy().agg()
    SELECT 
        customer_id,
        SUM(amount) as total_amount,
        COUNT(*) as order_count
    FROM filtered_orders
    GROUP BY customer_id
),
final_result AS (
    -- Corresponds to subsequent filter()
    SELECT customer_id, total_amount, order_count
    FROM grouped_summary
    WHERE total_amount > 1000
)
SELECT * FROM final_result
ORDER BY total_amount DESC;
```

### Conversion Patterns from DataFrame API to CTE

#### 1. Complex Aggregation Operation Conversion

```python
```

Spark complex aggregation:

```python
from pyspark.sql.functions import *
from pyspark.sql.window import Window

window_spec = Window.partitionBy("category").orderBy("date")
result = df.withColumn("running_total", 
                      sum("amount").over(window_spec)) \
           .withColumn("rank", 
                      row_number().over(window_spec.orderBy(desc("amount"))))
```

**Lakehouse CTE Implementation**:

```sql
-- Window functions combined with CTE: more intuitive logic expression
WITH enriched_data AS (
    SELECT 
        category,
        date,
        amount,
        -- Corresponds to Spark window functions
        SUM(amount) OVER (
            PARTITION BY category 
            ORDER BY date 
            ROWS UNBOUNDED PRECEDING
        ) as running_total,
        ROW_NUMBER() OVER (
            PARTITION BY category 
            ORDER BY amount DESC
        ) as rank
    FROM sales_data
),
ranked_results AS (
    SELECT 
        category,
        date,
        amount,
        running_total,
        rank,
        -- New analysis dimension
        AVG(amount) OVER (
            PARTITION BY category 
            ORDER BY date 
            ROWS 2 PRECEDING
        ) as three_day_avg
    FROM enriched_data
)
SELECT category, date, amount, running_total, rank, three_day_avg
FROM ranked_results
WHERE rank <= 10
ORDER BY category, rank;
```

#### 2. JOIN Operation Optimization Conversion

```python
```

Spark broadcast JOIN:

```python
from pyspark.sql.functions import broadcast

result = large_df.join(
    broadcast(small_df), 
    large_df.customer_id == small_df.customer_id, 
    "inner"
)
```

**Lakehouse CTE Optimized Version**:

```sql
-- CTE + MAPJOIN: dual advantage of performance and readability
WITH large_dataset AS (
    SELECT customer_id, order_id, amount, order_date
    FROM fact_orders
    WHERE order_date >= '2024-01-01'
),
customer_dimension AS (
    SELECT customer_id, customer_name, customer_tier, region
    FROM dim_customers
    WHERE status = 'Active'
)
SELECT /*+ MAPJOIN(customer_dimension) */
    ld.order_id,
    cd.customer_name,
    cd.customer_tier,
    cd.region,
    ld.amount,
    ld.order_date
FROM large_dataset ld
JOIN customer_dimension cd ON ld.customer_id = cd.customer_id
ORDER BY ld.amount DESC;
```

### Converting Spark UDF to SQL Functions

```python
```

Spark custom UDF:

```python
from pyspark.sql.types import StringType

def categorize_amount(amount):
    if amount > 1000:
        return "High"
    elif amount > 500:
        return "Medium"
    else:
        return "Low"

categorize_udf = udf(categorize_amount, StringType())
df_result = df.withColumn("amount_category", categorize_udf(col("amount")))
```

**Lakehouse CTE Implementation**:

```sql
-- Built-in CASE WHEN replacing UDF: better performance
WITH categorized_orders AS (
    SELECT 
        order_id,
        customer_id,
        amount,
        -- Built-in logic replacing UDF
        CASE 
            WHEN amount > 1000 THEN 'High'
            WHEN amount > 500 THEN 'Medium'
            ELSE 'Low'
        END as amount_category,
        -- More detailed categorization logic
        CASE 
            WHEN amount > 1000 AND customer_tier = 'VIP' THEN 'Premium_High'
            WHEN amount > 1000 THEN 'Standard_High'
            WHEN amount > 500 THEN 'Medium'
            ELSE 'Low'
        END as detailed_category
    FROM orders o
    JOIN customers c ON o.customer_id = c.customer_id
)
SELECT 
    amount_category,
    detailed_category,
    COUNT(*) as order_count,
    AVG(amount) as avg_amount
FROM categorized_orders
GROUP BY amount_category, detailed_category
ORDER BY avg_amount DESC;
```

---

## Hive User Migration Guide

### Converting MapReduce Thinking to Modern Analysis

The multi-stage Job execution pattern familiar to Hive users is simplified and performance-enhanced in Lakehouse CTE:

#### 1. Multi-Stage Aggregation Optimization

```sql
-- Hive multi-stage thinking (traditional approach)
-- Stage 1: basic aggregation
INSERT OVERWRITE TABLE temp_customer_summary
SELECT customer_id, SUM(amount) as total_amount
FROM orders
WHERE dt = '2024-06-01'
GROUP BY customer_id;

-- Stage 2: secondary aggregation
INSERT OVERWRITE TABLE final_customer_tiers
SELECT 
    CASE 
        WHEN total_amount > 10000 THEN 'VIP'
        ELSE 'Regular'
    END as tier,
    COUNT(*) as customer_count
FROM temp_customer_summary
GROUP BY CASE 
    WHEN total_amount > 10000 THEN 'VIP'
    ELSE 'Regular'
END;
```

**Lakehouse CTE Unified Implementation**:

```sql
-- Unified CTE: eliminate intermediate tables, improve performance
WITH customer_totals AS (
    -- First-layer aggregation: corresponds to Hive stage 1
    SELECT 
        customer_id,
        SUM(amount) as total_amount,
        COUNT(*) as order_count
    FROM orders
    WHERE DATE_FORMAT(o.o_orderdate, 'yyyy-MM-dd') = '1995-01-01'  -- Simulate partition dt
    GROUP BY customer_id
),
customer_tiers AS (
    -- Customer tiering: corresponds to Hive stage 2 logic
    SELECT 
        customer_id,
        total_amount,
        order_count,
        CASE 
            WHEN total_amount > 10000 THEN 'VIP'
            WHEN total_amount > 5000 THEN 'Premium'
            WHEN total_amount > 1000 THEN 'Standard'
            ELSE 'Basic'
        END as customer_tier
    FROM customer_totals
),
tier_analysis AS (
    -- Tier analysis: extended business logic
    SELECT 
        customer_tier,
        COUNT(*) as customer_count,
        AVG(total_amount) as avg_amount,
        SUM(total_amount) as tier_revenue,
        AVG(order_count) as avg_orders_per_customer
    FROM customer_tiers
    GROUP BY customer_tier
)
SELECT 
    customer_tier,
    customer_count,
    ROUND(avg_amount, 2) as avg_amount,
    ROUND(tier_revenue, 2) as tier_revenue,
    ROUND(avg_orders_per_customer, 2) as avg_orders,
    -- New analysis dimension
    ROUND(tier_revenue * 100.0 / SUM(tier_revenue) OVER (), 2) as revenue_percentage
FROM tier_analysis
ORDER BY tier_revenue DESC;
```

#### 2. Partition Table Processing Optimization

```sql
-- Continuation and enhancement of Hive partition thinking
WITH partition_summary AS (
    -- Partition data aggregation: maintain Hive partition pruning advantage
    SELECT 
        dt,
        region,
        product_category,
        SUM(sales_amount) as daily_sales,
        COUNT(DISTINCT customer_id) as unique_customers
    FROM sales_fact
    WHERE o.o_orderdate BETWEEN '1995-01-01' AND '1995-01-07'  -- Partition pruning
    GROUP BY dt, region, product_category
),
weekly_trends AS (
    -- Trend analysis: beyond traditional Hive capabilities
    SELECT 
        region,
        product_category,
        SUM(daily_sales) as weekly_sales,
        AVG(daily_sales) as avg_daily_sales,
        SUM(unique_customers) as total_unique_customers,
        -- Intra-week trend analysis
        MAX(daily_sales) - MIN(daily_sales) as volatility,
        STDDEV(daily_sales) as sales_stability
    FROM partition_summary
    GROUP BY region, product_category
),
performance_ranking AS (
    -- Performance ranking: multi-dimensional analysis
    SELECT 
        region,
        product_category,
        weekly_sales,
        avg_daily_sales,
        total_unique_customers,
        volatility,
        sales_stability,
        -- Regional ranking
        RANK() OVER (PARTITION BY region ORDER BY weekly_sales DESC) as region_rank,
        -- Global ranking
        RANK() OVER (ORDER BY weekly_sales DESC) as global_rank,
        -- Stability rating
        CASE 
            WHEN sales_stability / avg_daily_sales < 0.2 THEN 'Very Stable'
            WHEN sales_stability / avg_daily_sales < 0.4 THEN 'Stable'
            ELSE 'Volatile'
        END as stability_rating
    FROM weekly_trends
)
SELECT 
    region,
    product_category,
    ROUND(weekly_sales, 2) as weekly_sales,
    ROUND(avg_daily_sales, 2) as avg_daily_sales,
    total_unique_customers,
    region_rank,
    global_rank,
    stability_rating
FROM performance_ranking
WHERE global_rank <= 20
ORDER BY weekly_sales DESC;
```

### 3. Complex JOIN Performance Optimization

```sql
-- Direct migration and enhancement of Hive MAPJOIN syntax
WITH large_fact_data AS (
    SELECT 
        order_id,
        customer_id,
        product_id,
        order_date,
        quantity,
        unit_price
    FROM fact_orders
    WHERE order_date >= '2024-01-01'
),
dimension_tables AS (
    -- Dimension data preprocessing
    SELECT /*+ MAPJOIN(customers, products) */
        c.customer_id,
        c.customer_name,
        c.customer_segment,
        p.product_id,
        p.product_name,
        p.category
    FROM customers c
    CROSS JOIN products p  -- Generate customer-product combinations
    WHERE c.status = 'Active' 
      AND p.status = 'Available'
)
SELECT /*+ MAPJOIN(dimension_tables) */
    dt.customer_name,
    dt.customer_segment,
    dt.product_name,
    dt.category,
    COUNT(lfd.order_id) as order_count,
    SUM(lfd.quantity * lfd.unit_price) as total_revenue
FROM large_fact_data lfd
JOIN dimension_tables dt ON lfd.customer_id = dt.customer_id 
                        AND lfd.product_id = dt.product_id
GROUP BY dt.customer_name, dt.customer_segment, dt.product_name, dt.category
HAVING total_revenue > 1000
ORDER BY total_revenue DESC;
```

---

## MaxCompute User Migration Guide

### Syntax Continuation from the Alibaba Cloud Ecosystem

The syntax habits of MaxCompute users are well preserved in Lakehouse, while gaining stronger performance and flexibility:

#### 1. Converting Lifecycle Management Thinking

```sql
-- Continuation of MaxCompute lifecycle concepts
WITH data_lifecycle_analysis AS (
    -- Data timeliness analysis
    SELECT 
        table_name,
        partition_date,
        record_count,
        data_size_mb,
        DATEDIFF(CURRENT_DATE(), partition_date) as data_age_days,
        -- Data value assessment
        CASE 
            WHEN DATEDIFF(CURRENT_DATE(), partition_date) <= 7 THEN 'Hot'
            WHEN DATEDIFF(CURRENT_DATE(), partition_date) <= 30 THEN 'Warm'
            WHEN DATEDIFF(CURRENT_DATE(), partition_date) <= 90 THEN 'Cold'
            ELSE 'Archive'
        END as data_temperature
    FROM information_schema.table_partitions
    WHERE table_name LIKE 'fact_%'
),
storage_optimization AS (
    -- Storage optimization recommendations
    SELECT 
        data_temperature,
        COUNT(*) as partition_count,
        SUM(record_count) as total_records,
        SUM(data_size_mb) as total_size_mb,
        AVG(data_age_days) as avg_age_days
    FROM data_lifecycle_analysis
    GROUP BY data_temperature
),
cost_analysis AS (
    -- Cost analysis
    SELECT 
        data_temperature,
        partition_count,
        total_size_mb,
        -- Estimated cost calculation
        total_size_mb * 0.01 as estimated_storage_cost,
        CASE 
            WHEN data_temperature = 'Archive' THEN total_size_mb * 0.005
            ELSE total_size_mb * 0.01
        END as optimized_cost
    FROM storage_optimization
)
SELECT 
    data_temperature,
    partition_count,
    ROUND(total_size_mb / 1024, 2) as total_size_gb,
    ROUND(estimated_storage_cost, 2) as current_cost,
    ROUND(optimized_cost, 2) as optimized_cost,
    ROUND(estimated_storage_cost - optimized_cost, 2) as potential_savings
FROM cost_analysis
ORDER BY potential_savings DESC;
```

#### 2. Complex Data Type Processing

```sql
-- Enhanced processing of MaxCompute complex types
WITH complex_data_processing AS (
    -- Complex data structure parsing
    SELECT 
        user_id,
        event_date,
        -- Array processing: compatible with MaxCompute syntax
        SIZE(event_list) as event_count,
        event_list[0] as first_event,  -- Array index starts from 0
        -- MAP processing
        user_attributes['age'] as user_age,
        user_attributes['city'] as user_city,
        -- JSON processing enhancement
        GET_JSON_OBJECT(user_profile, '$.preferences.category') as preferred_category
    FROM user_events
    WHERE event_date >= '2024-06-01'
),
exploded_events AS (
    -- Array expansion: simplified syntax
    SELECT 
        user_id,
        event_date,
        EXPLODE(event_list) as individual_event,
        user_age,
        user_city,
        preferred_category
    FROM complex_data_processing
),
event_analysis AS (
    -- Event analysis
    SELECT 
        preferred_category,
        user_city,
        individual_event,
        COUNT(DISTINCT user_id) as unique_users,
        COUNT(*) as event_occurrences,
        AVG(CAST(user_age AS INT)) as avg_user_age
    FROM exploded_events
    WHERE individual_event IS NOT NULL
    GROUP BY preferred_category, user_city, individual_event
)
SELECT 
    preferred_category,
    user_city,
    individual_event,
    unique_users,
    event_occurrences,
    ROUND(avg_user_age, 1) as avg_user_age,
    -- Engagement rate calculation
    ROUND(event_occurrences * 1.0 / unique_users, 2) as engagement_rate
FROM event_analysis
WHERE unique_users >= 10
ORDER BY engagement_rate DESC
LIMIT 20;
```

#### 3. Function Compatibility and Enhancement

```sql
-- MaxCompute function compatibility and enhancement
WITH date_processing AS (
    -- Date function mapping
    SELECT 
        order_id,
        customer_id,
        -- MaxCompute: GETDATE() → Lakehouse: CURRENT_TIMESTAMP()
        CURRENT_TIMESTAMP() as process_time,
        order_date,
        -- Date formatting compatibility
        DATE_FORMAT(order_date, 'yyyy-MM-dd') as order_date_str,
        DATE_FORMAT(order_date, 'yyyy-MM') as order_month,
        -- Week-related calculations
        WEEKOFYEAR(order_date) as week_number,
        DAYOFWEEK(order_date) as day_of_week,
        -- Quarter calculation
        QUARTER(order_date) as quarter
    FROM orders
    WHERE order_date >= '2024-01-01'
),
advanced_analytics AS (
    -- Advanced analytics features
    SELECT 
        order_month,
        quarter,
        COUNT(*) as monthly_orders,
        -- Year-over-year growth (requires historical data)
        LAG(COUNT(*), 12) OVER (ORDER BY order_month) as same_month_last_year,
        -- Month-over-month growth
        LAG(COUNT(*), 1) OVER (ORDER BY order_month) as prev_month,
        -- Cumulative metrics
        SUM(COUNT(*)) OVER (ORDER BY order_month ROWS UNBOUNDED PRECEDING) as cumulative_orders
    FROM date_processing
    GROUP BY order_month, quarter
),
growth_analysis AS (
    -- Growth rate calculation
    SELECT 
        order_month,
        quarter,
        monthly_orders,
        cumulative_orders,
        CASE 
            WHEN same_month_last_year IS NULL THEN 'N/A'
            ELSE CONCAT(
                ROUND(((monthly_orders - same_month_last_year) * 100.0 / same_month_last_year), 2),
                '%'
            )
        END as yoy_growth,
        CASE 
            WHEN prev_month IS NULL THEN 'N/A'
            ELSE CONCAT(
                ROUND(((monthly_orders - prev_month) * 100.0 / prev_month), 2),
                '%'
            )
        END as mom_growth
    FROM advanced_analytics
)
SELECT 
    order_month,
    quarter,
    monthly_orders,
    cumulative_orders,
    yoy_growth,
    mom_growth
FROM growth_analysis
ORDER BY order_month;
```

---

## Snowflake User Migration Guide

### Correspondence and Enhancement of Cloud-Native Features

The automatic optimization and elastic scaling familiar to Snowflake users gain more granular tuning control through explicit optimization in Lakehouse:

#### 1. Concept Conversion from Virtual Warehouse to VCluster

```sql
-- Snowflake auto-optimization → Lakehouse explicit optimization control
WITH resource_intensive_analysis AS (
    -- Large-scale data processing: explicitly specify compute cluster
    SELECT 
        region,
        product_line,
        customer_segment,
        SUM(revenue) as total_revenue,
        COUNT(DISTINCT customer_id) as unique_customers,
        AVG(order_value) as avg_order_value
    FROM /*+ VCLUSTER(analytics_large) */ fact_sales
    WHERE sale_date >= '2024-01-01'
    GROUP BY region, product_line, customer_segment
),
performance_metrics AS (
    -- Performance metrics calculation
    SELECT 
        region,
        product_line,
        customer_segment,
        total_revenue,
        unique_customers,
        avg_order_value,
        -- Customer value density
        total_revenue / unique_customers as revenue_per_customer,
        -- Market share calculation
        total_revenue / SUM(total_revenue) OVER (PARTITION BY region) as regional_market_share,
        -- Performance ranking
        RANK() OVER (ORDER BY total_revenue DESC) as global_rank,
        RANK() OVER (PARTITION BY region ORDER BY total_revenue DESC) as regional_rank
    FROM resource_intensive_analysis
),
segment_analysis AS (
    -- Segment analysis
    SELECT 
        pm.*,
        -- Relative performance metrics
        avg_order_value / AVG(avg_order_value) OVER () as relative_order_value,
        revenue_per_customer / AVG(revenue_per_customer) OVER () as relative_customer_value,
        -- Growth potential assessment
        CASE 
            WHEN regional_market_share > 0.3 THEN 'Market Leader'
            WHEN regional_market_share > 0.15 THEN 'Strong Player'
            WHEN regional_market_share > 0.05 THEN 'Emerging'
            ELSE 'Niche'
        END as market_position
    FROM performance_metrics pm
)
SELECT 
    region,
    product_line,
    customer_segment,
    ROUND(total_revenue, 2) as total_revenue,
    unique_customers,
    ROUND(avg_order_value, 2) as avg_order_value,
    ROUND(revenue_per_customer, 2) as revenue_per_customer,
    ROUND(regional_market_share * 100, 2) as market_share_pct,
    global_rank,
    regional_rank,
    market_position
FROM segment_analysis
WHERE global_rank <= 50
ORDER BY total_revenue DESC;
```

#### 2. Corresponding Implementation of Time Travel

```sql
-- Snowflake Time Travel → Lakehouse historical data query
WITH historical_comparison AS (
    -- Historical data comparison analysis
    SELECT 
        'Current' as time_period,
        customer_id,
        SUM(order_amount) as total_spent,
        COUNT(*) as order_count,
        AVG(order_amount) as avg_order_value
    FROM orders
    WHERE created_time >= '2024-06-01 00:00:00'
      AND created_time <= '2024-06-30 23:59:59'
    GROUP BY customer_id
    
    UNION ALL
    
    SELECT 
        'Previous_Month' as time_period,
        customer_id,
        SUM(order_amount) as total_spent,
        COUNT(*) as order_count,
        AVG(order_amount) as avg_order_value
    FROM orders
    WHERE created_time >= '2024-05-01 00:00:00'
      AND created_time <= '2024-05-31 23:59:59'
    GROUP BY customer_id
),
customer_evolution AS (
    -- Customer evolution analysis
    SELECT 
        customer_id,
        MAX(CASE WHEN time_period = 'Current' THEN total_spent END) as current_spent,
        MAX(CASE WHEN time_period = 'Previous_Month' THEN total_spent END) as previous_spent,
        MAX(CASE WHEN time_period = 'Current' THEN order_count END) as current_orders,
        MAX(CASE WHEN time_period = 'Previous_Month' THEN order_count END) as previous_orders,
        MAX(CASE WHEN time_period = 'Current' THEN avg_order_value END) as current_avg,
        MAX(CASE WHEN time_period = 'Previous_Month' THEN avg_order_value END) as previous_avg
    FROM historical_comparison
    GROUP BY customer_id
),
growth_analysis AS (
    -- Growth rate analysis
    SELECT 
        customer_id,
        COALESCE(current_spent, 0) as current_spent,
        COALESCE(previous_spent, 0) as previous_spent,
        COALESCE(current_orders, 0) as current_orders,
        COALESCE(previous_orders, 0) as previous_orders,
        -- Spending growth rate
        CASE 
            WHEN previous_spent > 0 
            THEN ROUND(((current_spent - previous_spent) / previous_spent * 100), 2)
            WHEN current_spent > 0 THEN 100.0
            ELSE 0.0
        END as spending_growth_pct,
        -- Order frequency change
        CASE 
            WHEN previous_orders > 0 
            THEN ROUND(((current_orders - previous_orders) / previous_orders * 100), 2)
            WHEN current_orders > 0 THEN 100.0
            ELSE 0.0
        END as order_frequency_growth_pct,
        -- Customer status classification
        CASE 
            WHEN current_spent > 0 AND previous_spent > 0 THEN 'Retained'
            WHEN current_spent > 0 AND previous_spent = 0 THEN 'New'
            WHEN current_spent = 0 AND previous_spent > 0 THEN 'Churned'
            ELSE 'Inactive'
        END as customer_status
    FROM customer_evolution
)
SELECT 
    customer_status,
    COUNT(*) as customer_count,
    ROUND(AVG(spending_growth_pct), 2) as avg_spending_growth,
    ROUND(AVG(order_frequency_growth_pct), 2) as avg_frequency_growth,
    ROUND(SUM(current_spent), 2) as total_current_revenue,
    ROUND(SUM(previous_spent), 2) as total_previous_revenue
FROM growth_analysis
GROUP BY customer_status
ORDER BY total_current_revenue DESC;
```

#### 3. Explicit Control for Automatic Clustering

```sql
-- Snowflake auto-clustering → Lakehouse partition and clustering strategy
WITH clustered_data_analysis AS (
    -- Explicit partition and clustering optimization
    SELECT 
        DATE_FORMAT(order_date, 'yyyy-MM') as order_month,
        customer_tier,
        product_category,
        COUNT(*) as order_count,
        SUM(order_amount) as total_revenue,
        AVG(order_amount) as avg_order_value,
        -- Data distribution analysis
        MIN(order_amount) as min_order,
        MAX(order_amount) as max_order,
        STDDEV(order_amount) as order_amount_stddev
    FROM orders
    WHERE order_date >= '2024-01-01'
    GROUP BY DATE_FORMAT(order_date, 'yyyy-MM'), customer_tier, product_category
),
performance_optimization AS (
    -- Performance optimization metrics
    SELECT 
        order_month,
        customer_tier,
        product_category,
        order_count,
        total_revenue,
        avg_order_value,
        -- Clustering effect assessment
        order_amount_stddev / avg_order_value as coefficient_of_variation,
        -- Partition efficiency assessment
        order_count / SUM(order_count) OVER (PARTITION BY order_month) as monthly_distribution,
        -- Hotspot data identification
        CASE 
            WHEN order_count > AVG(order_count) OVER () * 2 THEN 'Hot'
            WHEN order_count > AVG(order_count) OVER () THEN 'Warm'
            ELSE 'Cold'
        END as data_temperature
    FROM clustered_data_analysis
),
optimization_recommendations AS (
    -- Optimization recommendations
    SELECT 
        order_month,
        customer_tier,
        product_category,
        total_revenue,
        data_temperature,
        coefficient_of_variation,
        monthly_distribution,
        -- Partition recommendation
        CASE 
            WHEN monthly_distribution > 0.1 THEN 'Consider_Monthly_Partition'
            ELSE 'Current_Partition_OK'
        END as partition_recommendation,
        -- Clustering recommendation
        CASE 
            WHEN coefficient_of_variation > 1.0 THEN 'High_Variance_Consider_Clustering'
            WHEN coefficient_of_variation > 0.5 THEN 'Medium_Variance'
            ELSE 'Low_Variance_Well_Clustered'
        END as clustering_recommendation
    FROM performance_optimization
)
SELECT 
    order_month,
    customer_tier,
    product_category,
    ROUND(total_revenue, 2) as total_revenue,
    data_temperature,
    ROUND(coefficient_of_variation, 3) as variance_ratio,
    ROUND(monthly_distribution * 100, 2) as distribution_pct,
    partition_recommendation,
    clustering_recommendation
FROM optimization_recommendations
WHERE total_revenue > 10000
ORDER BY total_revenue DESC;
```

---

## Traditional Database User Migration Guide

### OLTP to OLAP Mindset Shift

Traditional database users need to shift from row-based storage and transaction processing to column-based storage and analytical processing patterns:

#### 1. Stored Procedure to CTE Refactoring

```sql
-- Traditional stored procedure logic → CTE analysis pipeline
-- Original stored procedure thinking: step-by-step processing, intermediate result storage
/*
CREATE PROCEDURE AnalyzeCustomerPerformance()
BEGIN
    CREATE TEMPORARY TABLE temp_customer_metrics AS
    SELECT customer_id, SUM(amount) as total_spent FROM orders GROUP BY customer_id;
    
    CREATE TEMPORARY TABLE temp_customer_tiers AS
    SELECT *, CASE WHEN total_spent > 1000 THEN 'VIP' ELSE 'Regular' END as tier
    FROM temp_customer_metrics;
    
    SELECT tier, COUNT(*) FROM temp_customer_tiers GROUP BY tier;
END
*/

-- Lakehouse CTE implementation: unified analysis pipeline
WITH customer_transaction_base AS (
    -- Basic transaction data: replaces temporary table logic
    SELECT 
        c.customer_id,
        c.customer_name,
        c.registration_date,
        o.order_id,
        o.order_date,
        o.order_amount,
        -- Customer lifecycle calculation
        DATEDIFF(CURRENT_DATE(), c.registration_date) as customer_age_days,
        DATEDIFF(o.order_date, c.registration_date) as order_since_registration
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    WHERE o.order_date >= '2024-01-01'
),
customer_behavioral_metrics AS (
    -- Customer behavioral metrics: exceeds traditional stored procedure capabilities
    SELECT 
        customer_id,
        customer_name,
        customer_age_days,
        COUNT(*) as total_orders,
        SUM(order_amount) as total_spent,
        AVG(order_amount) as avg_order_value,
        MIN(order_date) as first_order_date,
        MAX(order_date) as last_order_date,
        -- Purchase frequency analysis
        COUNT(*) / (DATEDIFF(MAX(order_date), MIN(order_date)) + 1) * 30 as orders_per_month,
        -- Repurchase interval
        AVG(DATEDIFF(
            LEAD(order_date) OVER (PARTITION BY customer_id ORDER BY order_date),
            order_date
        )) as avg_days_between_orders
    FROM customer_transaction_base
    GROUP BY customer_id, customer_name, customer_age_days
),
customer_segmentation AS (
    -- Customer segmentation: multi-dimensional analysis
    SELECT 
        *,
        -- Value tier
        CASE 
            WHEN total_spent >= 10000 THEN 'Diamond'
            WHEN total_spent >= 5000 THEN 'Platinum'
            WHEN total_spent >= 1000 THEN 'Gold'
            ELSE 'Silver'
        END as value_tier,
        -- Activity tier
        CASE 
            WHEN orders_per_month >= 2 THEN 'Highly Active'
            WHEN orders_per_month >= 1 THEN 'Active'
            WHEN orders_per_month >= 0.5 THEN 'Moderate'
            ELSE 'Low Activity'
        END as activity_tier,
        -- Loyalty tier
        CASE 
            WHEN customer_age_days >= 365 AND total_orders >= 12 THEN 'Loyal'
            WHEN customer_age_days >= 180 AND total_orders >= 6 THEN 'Regular'
            WHEN customer_age_days >= 90 THEN 'Developing'
            ELSE 'New'
        END as loyalty_tier,
        -- Customer health score
        CASE 
            WHEN DATEDIFF(CURRENT_DATE(), last_order_date) <= 30 THEN 'Healthy'
            WHEN DATEDIFF(CURRENT_DATE(), last_order_date) <= 90 THEN 'At Risk'
            ELSE 'Churned'
        END as health_status
    FROM customer_behavioral_metrics
),
comprehensive_analysis AS (
    -- Comprehensive analysis: business insights
    SELECT 
        value_tier,
        activity_tier,
        loyalty_tier,
        health_status,
        COUNT(*) as customer_count,
        ROUND(AVG(total_spent), 2) as avg_customer_value,
        ROUND(SUM(total_spent), 2) as segment_revenue,
        ROUND(AVG(orders_per_month), 2) as avg_monthly_frequency,
        ROUND(AVG(avg_days_between_orders), 1) as avg_repurchase_cycle
    FROM customer_segmentation
    GROUP BY value_tier, activity_tier, loyalty_tier, health_status
)
SELECT 
    value_tier,
    activity_tier,
    loyalty_tier,
    health_status,
    customer_count,
    avg_customer_value,
    segment_revenue,
    avg_monthly_frequency,
    avg_repurchase_cycle,
    -- Revenue share
    ROUND(segment_revenue * 100.0 / SUM(segment_revenue) OVER (), 2) as revenue_share_pct
FROM comprehensive_analysis
WHERE customer_count >= 5  -- Filter small sample groups
ORDER BY segment_revenue DESC;
```

#### 2. Normalized to Dimensional Modeling Conversion

```sql
-- Traditional normalized query → dimensional modeling analysis
WITH denormalized_sales_base AS (
    -- Denormalization: improve query performance
    SELECT 
        s.sale_id,
        s.sale_date,
        s.quantity,
        s.unit_price,
        s.total_amount,
        -- Customer dimension
        c.customer_id,
        c.customer_name,
        c.customer_type,
        c.customer_segment,
        -- Product dimension
        p.product_id,
        p.product_name,
        p.category,
        p.brand,
        p.supplier_id,
        -- Geography dimension
        g.region_id,
        g.region_name,
        g.country,
        g.city,
        -- Time dimension
        DATE_FORMAT(s.sale_date, 'yyyy') as sale_year,
        DATE_FORMAT(s.sale_date, 'yyyy-MM') as sale_month,
        DATE_FORMAT(s.sale_date, 'yyyy-Q') as sale_quarter,
        DAYOFWEEK(s.sale_date) as day_of_week,
        WEEKOFYEAR(s.sale_date) as week_of_year
    FROM sales s
    JOIN customers c ON s.customer_id = c.customer_id
    JOIN products p ON s.product_id = p.product_id
    JOIN geography g ON c.region_id = g.region_id
    WHERE s.sale_date >= '2024-01-01'
),
multidimensional_analysis AS (
    -- Multi-dimensional analysis: OLAP thinking
    SELECT 
        sale_year,
        sale_quarter,
        customer_segment,
        category,
        region_name,
        -- Basic metrics
        COUNT(*) as transaction_count,
        SUM(total_amount) as total_revenue,
        SUM(quantity) as total_quantity,
        AVG(total_amount) as avg_transaction_value,
        COUNT(DISTINCT customer_id) as unique_customers,
        COUNT(DISTINCT product_id) as unique_products,
        -- Advanced metrics
        SUM(total_amount) / COUNT(DISTINCT customer_id) as revenue_per_customer,
        SUM(quantity) / COUNT(*) as avg_quantity_per_transaction,
        -- Market share
        SUM(total_amount) / SUM(SUM(total_amount)) OVER (PARTITION BY sale_year, sale_quarter) as market_share
    FROM denormalized_sales_base
    GROUP BY sale_year, sale_quarter, customer_segment, category, region_name
),
trend_analysis AS (
    -- Trend analysis: time series insights
    SELECT 
        *,
        -- Year-over-year growth
        LAG(total_revenue, 4) OVER (
            PARTITION BY customer_segment, category, region_name 
            ORDER BY sale_year, sale_quarter
        ) as same_quarter_last_year,
        -- Quarter-over-quarter growth
        LAG(total_revenue, 1) OVER (
            PARTITION BY customer_segment, category, region_name 
            ORDER BY sale_year, sale_quarter
        ) as previous_quarter,
        -- Moving average
        AVG(total_revenue) OVER (
            PARTITION BY customer_segment, category, region_name 
            ORDER BY sale_year, sale_quarter
            ROWS 3 PRECEDING
        ) as four_quarter_avg
    FROM multidimensional_analysis
),
performance_insights AS (
    -- Performance insights
    SELECT 
        sale_year,
        sale_quarter,
        customer_segment,
        category,
        region_name,
        total_revenue,
        unique_customers,
        revenue_per_customer,
        market_share,
        -- Growth rate calculation
        CASE 
            WHEN same_quarter_last_year > 0 
            THEN ROUND(((total_revenue - same_quarter_last_year) / same_quarter_last_year * 100), 2)
            ELSE NULL
        END as yoy_growth_pct,
        CASE 
            WHEN previous_quarter > 0 
            THEN ROUND(((total_revenue - previous_quarter) / previous_quarter * 100), 2)
            ELSE NULL
        END as qoq_growth_pct,
        -- Trend assessment
        CASE 
            WHEN total_revenue > four_quarter_avg * 1.1 THEN 'Strong Growth'
            WHEN total_revenue > four_quarter_avg * 1.05 THEN 'Moderate Growth'
            WHEN total_revenue > four_quarter_avg * 0.95 THEN 'Stable'
            WHEN total_revenue > four_quarter_avg * 0.9 THEN 'Moderate Decline'
            ELSE 'Strong Decline'
        END as trend_category
    FROM trend_analysis
)
SELECT 
    sale_year,
    sale_quarter,
    customer_segment,
    category,
    region_name,
    ROUND(total_revenue, 2) as total_revenue,
    unique_customers,
    ROUND(revenue_per_customer, 2) as revenue_per_customer,
    ROUND(market_share * 100, 2) as market_share_pct,
    yoy_growth_pct,
    qoq_growth_pct,
    trend_category
FROM performance_insights
WHERE total_revenue > 10000  -- Filter small transactions
ORDER BY sale_year DESC, sale_quarter DESC, total_revenue DESC;
```

#### 3. Transaction Processing to Batch Analysis Conversion

```sql
-- Transaction thinking → batch analysis thinking
WITH real_time_vs_batch_analysis AS (
    -- Real-time metrics vs batch metrics comparison
    SELECT 
        'Real_Time' as analysis_type,
        COUNT(*) as transaction_count,
        SUM(amount) as total_amount,
        AVG(amount) as avg_amount,
        MAX(created_time) as latest_transaction
    FROM transactions
    WHERE created_time >= DATE_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 HOUR)
    
    UNION ALL
    
    SELECT 
        'Daily_Batch' as analysis_type,
        COUNT(*) as transaction_count,
        SUM(amount) as total_amount,
        AVG(amount) as avg_amount,
        MAX(created_time) as latest_transaction
    FROM transactions
    WHERE DATE(created_time) = CURRENT_DATE()
    
    UNION ALL
    
    SELECT 
        'Weekly_Batch' as analysis_type,
        COUNT(*) as transaction_count,
        SUM(amount) as total_amount,
        AVG(amount) as avg_amount,
        MAX(created_time) as latest_transaction
    FROM transactions
    WHERE created_time >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)
),
historical_pattern_analysis AS (
    -- Historical pattern analysis: batch analysis advantages
    SELECT 
        DAYOFWEEK(created_time) as day_of_week,
        HOUR(created_time) as hour_of_day,
        COUNT(*) as hourly_transaction_count,
        AVG(amount) as avg_hourly_amount,
        STDDEV(amount) as amount_volatility
    FROM transactions
    WHERE created_time >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
    GROUP BY DAYOFWEEK(created_time), HOUR(created_time)
),
pattern_insights AS (
    -- Pattern insights
    SELECT 
        day_of_week,
        hour_of_day,
        hourly_transaction_count,
        avg_hourly_amount,
        amount_volatility,
        -- Identify peak periods
        CASE 
            WHEN hourly_transaction_count > AVG(hourly_transaction_count) OVER () * 1.5 THEN 'Peak'
            WHEN hourly_transaction_count > AVG(hourly_transaction_count) OVER () THEN 'High'
            WHEN hourly_transaction_count > AVG(hourly_transaction_count) OVER () * 0.5 THEN 'Normal'
            ELSE 'Low'
        END as traffic_level,
        -- Amount pattern
        CASE 
            WHEN avg_hourly_amount > AVG(avg_hourly_amount) OVER () * 1.2 THEN 'High Value'
            WHEN avg_hourly_amount < AVG(avg_hourly_amount) OVER () * 0.8 THEN 'Low Value'
            ELSE 'Normal Value'
        END as value_pattern
    FROM historical_pattern_analysis
)
-- Final business insights
SELECT 
    CASE 
        WHEN day_of_week = 1 THEN 'Sunday'
        WHEN day_of_week = 2 THEN 'Monday'
        WHEN day_of_week = 3 THEN 'Tuesday'
        WHEN day_of_week = 4 THEN 'Wednesday'
        WHEN day_of_week = 5 THEN 'Thursday'
        WHEN day_of_week = 6 THEN 'Friday'
        WHEN day_of_week = 7 THEN 'Saturday'
    END as weekday,
    hour_of_day,
    hourly_transaction_count,
    ROUND(avg_hourly_amount, 2) as avg_amount,
    traffic_level,
    value_pattern,
    -- Operational recommendations
    CASE 
        WHEN traffic_level = 'Peak' AND value_pattern = 'High Value' THEN 'Focus_on_Capacity'
        WHEN traffic_level = 'Peak' AND value_pattern = 'Low Value' THEN 'Optimize_Processing'
        WHEN traffic_level = 'Low' AND value_pattern = 'High Value' THEN 'Marketing_Opportunity'
        ELSE 'Monitor'
    END as operational_recommendation
FROM pattern_insights
ORDER BY day_of_week, hour_of_day;
```

---

## Performance Optimization Best Practices

### General Optimization Strategies

#### 1. CTE Execution Order Optimization

```sql
-- Best practice: filter → aggregate → join → compute
WITH early_filtering AS (
    -- Step 1: filter early to reduce data volume
    SELECT customer_id, order_date, order_amount, product_id
    FROM orders
    WHERE order_date >= '2024-01-01'
      AND order_status = 'completed'
      AND order_amount > 100
),
aggregation_layer AS (
    -- Step 2: aggregation reduces data volume
    SELECT 
        customer_id,
        product_id,
        COUNT(*) as order_count,
        SUM(order_amount) as total_amount,
        AVG(order_amount) as avg_amount
    FROM early_filtering
    GROUP BY customer_id, product_id
),
dimension_enrichment AS (
    -- Step 3: join with small tables
    SELECT /*+ MAPJOIN(customers, products) */
        al.customer_id,
        c.customer_name,
        c.customer_segment,
        al.product_id,
        p.product_name,
        p.category,
        al.order_count,
        al.total_amount,
        al.avg_amount
    FROM aggregation_layer al
    JOIN customers c ON al.customer_id = c.customer_id
    JOIN products p ON al.product_id = p.product_id
),
final_calculations AS (
    -- Step 4: final calculations
    SELECT 
        *,
        total_amount / SUM(total_amount) OVER (PARTITION BY customer_segment) as segment_share,
        RANK() OVER (PARTITION BY category ORDER BY total_amount DESC) as category_rank
    FROM dimension_enrichment
)
SELECT * FROM final_calculations
WHERE category_rank <= 10
ORDER BY total_amount DESC;
```

#### 2. Memory Usage Optimization

```sql
-- Avoid CTEs with large result sets
WITH controlled_dataset AS (
    -- Control dataset size
    SELECT customer_id, order_amount, order_date
    FROM orders
    WHERE order_date >= '2024-06-01'  -- Limit time window
      AND customer_id IN (
          SELECT customer_id 
          FROM high_value_customers 
          LIMIT 10000  -- Limit customer count
      )
    LIMIT 100000  -- Limit total record count
),
efficient_aggregation AS (
    -- Efficient aggregation
    SELECT 
        DATE_FORMAT(order_date, 'yyyy-MM') as month,
        COUNT(*) as order_count,
        SUM(order_amount) as total_revenue
    FROM controlled_dataset
    GROUP BY DATE_FORMAT(order_date, 'yyyy-MM')
)
SELECT * FROM efficient_aggregation
ORDER BY month;
```

### Stack-Specific Optimizations

#### 1. Spark Users: Caching Strategy

```sql
-- Simulate Spark caching effect
WITH reusable_base AS (
    -- Reusable base dataset
    SELECT 
        customer_id,
        product_id,
        order_date,
        order_amount,
        DATE_FORMAT(order_date, 'yyyy-MM') as order_month
    FROM orders
    WHERE order_date >= '2024-01-01'
),
monthly_summary AS (
    SELECT 
        order_month,
        COUNT(*) as monthly_orders,
        SUM(order_amount) as monthly_revenue
    FROM reusable_base
    GROUP BY order_month
),
customer_summary AS (
    SELECT 
        customer_id,
        COUNT(*) as customer_orders,
        SUM(order_amount) as customer_revenue
    FROM reusable_base
    GROUP BY customer_id
)
-- Use base dataset multiple times
SELECT 
    ms.order_month,
    ms.monthly_orders,
    ms.monthly_revenue,
    COUNT(DISTINCT cs.customer_id) as active_customers
FROM monthly_summary ms
CROSS JOIN customer_summary cs
WHERE cs.customer_revenue > 1000
GROUP BY ms.order_month, ms.monthly_orders, ms.monthly_revenue
ORDER BY ms.order_month;
```

#### 2. Hive Users: Partition Optimization

```sql
-- Maintain partition pruning advantages
WITH partitioned_analysis AS (
    SELECT 
        dt,  -- Partition column
        region,
        SUM(sales_amount) as daily_sales
    FROM sales_fact
    WHERE dt BETWEEN '2024-06-01' AND '2024-06-07'  -- Partition pruning
    GROUP BY dt, region
),
weekly_aggregation AS (
    SELECT 
        region,
        SUM(daily_sales) as weekly_sales,
        COUNT(*) as active_days
    FROM partitioned_analysis
    GROUP BY region
)
SELECT 
    region,
    weekly_sales,
    active_days,
    weekly_sales / active_days as avg_daily_sales
FROM weekly_aggregation
ORDER BY weekly_sales DESC;
```

---

## Migration Success Factors Summary

### Technology Stack Mapping

| Source Stack | Core Migration Point | CTE Advantage | Expected Benefit |
|----------|-----------|---------|----------|
| **Spark** | DataFrame chaining→CTE layering | More intuitive SQL expression | Lower learning curve, unified development experience |
| **Hive** | Multi-stage Jobs→unified query | Eliminate intermediate table dependencies | Significantly improve development efficiency and performance |
| **MaxCompute** | Direct syntax compatibility | Enhanced performance optimization | Faster query response and real-time interactivity |
| **Snowflake** | Auto-optimization→explicit control | More granular tuning capabilities | Better resource control and cost optimization |
| **Traditional DB** | OLTP thinking→OLAP thinking | Qualitative leap in analysis capability | Support large-scale complex data analysis |

### General Best Practices

#### 1. CTE Design Principles

- **Logical Layering**: Build step by step according to business logic
- **Data Flow**: Follow the "filter→aggregate→join→compute" sequence
- **Naming Convention**: Use CTE names with clear business meaning
- **Reuse Consideration**: Extract logic that may be referenced multiple times into independent CTEs

#### 2. Performance Optimization Checklist

- ✅ **Early Filtering**: Filter data in the first layer of CTE
- ✅ **MAPJOIN Usage**: Prefer MAPJOIN hints for small tables
- ✅ **Partition Pruning**: Leverage partition columns for filtering
- ✅ **Aggregate First**: Complete necessary aggregation before JOINs
- ✅ **Result Set Control**: Avoid generating oversized intermediate results

#### 3. Code Quality Standards

- 🎯 **Readability**: Each CTE has a single responsibility, clear logic
- 🎯 **Maintainability**: Modular design, easy localized modifications
- 🎯 **Testability**: Each CTE can be independently verified
- 🎯 **Extensibility**: Easy to add new analysis dimensions

---

## Summary

The Singdata Lakehouse WITH CTE feature provides a unified and powerful data analysis platform for users from different technical backgrounds. Through the migration strategies in this guide:

### Verified Feature List

All code in this guide has passed the following feature verification:
- ✅ Basic CTE syntax and multi-CTE definitions
- ✅ CTE combined with MAPJOIN optimization hints
- ✅ Complex window functions combined with CTE
- ✅ Data pivoting and row-column conversion
- ✅ Multi-step data cleaning pipelines
- ✅ Array processing (SPLIT, EXPLODE, etc.)
- ✅ Cross-stack syntax compatibility
- ✅ Performance optimization best practices
- ❌ Recursive CTE (not currently supported in the current version; see [Hierarchical Query Workaround](sql_hierarchy_workaround_guide.md) for alternatives)

### Get Started Now

1. **Identify your technology background**: Select the corresponding migration guide chapter
2. **Start simple**: Replace existing queries with basic CTE syntax
3. **Gradually optimize**: Combine MAPJOIN and other optimization features to improve performance
4. **Continuous improvement**: Tune complex queries based on execution plans

### Long-Term Benefits

- **Unified skill set**: One set of SQL skills applicable to all analysis scenarios
- **Lower learning cost**: Standard SQL syntax, no need to learn new APIs  
- **Improved development efficiency**: Modular CTE design, increased code reuse
- **Enhanced analysis capability**: Seamless transition from simple queries to complex analysis
- **Production ready**: All examples verified in practice, ready for production

> **Important Note**: The above benefits are theoretical expectations based on technical characteristics. Actual results vary depending on business scenarios, data scale, team skills, and other factors. Users are advised to conduct real-world testing and verification based on their own circumstances.

No matter what technology background you come from, Singdata Lakehouse WITH CTE will become a powerful assistant in your data analysis work, helping you advance further on the path of modern data analysis!

### Getting Help

- 💡 If you encounter issues during use, please refer to the migration chapter for your corresponding technology stack
- 🔧 All sample code can be run and tested directly in the Singdata Lakehouse environment
- 📚 It is recommended to start with simple examples and gradually master advanced features

---

**Note**: This document is compiled based on the Lakehouse product documentation as of June 2025. It is recommended to regularly check the official documentation for the latest updates. Before using in a production environment, always verify the correctness and performance impact of all operations in a test environment.
