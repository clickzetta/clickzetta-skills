# GROUP BY

## Overview

The `GROUP BY` clause is a core component in SQL queries used for data grouping and aggregation analysis. With `GROUP BY`, you can group a dataset by specified columns or expressions and apply aggregate functions (such as `SUM()`, `COUNT()`, `AVG()`, `MAX()`, `MIN()`, etc.) to each group to compute summary values.

Singdata Lakehouse fully supports standard SQL GROUP BY syntax and provides advanced aggregation capabilities:

| Feature                | Description                          | Use Case                                   |
| ----------------- | ---------------------------------------- | --------------------------------------- |
| **Standard GROUP BY**   | Basic grouping and aggregation               | Daily statistics, basic reports              |
| **GROUPING SETS** | Custom multiple grouping sets                  | Multi-dimensional business analysis               |
| **ROLLUP**        | Hierarchical rollup (from detail to total)          | Financial reports, sales hierarchy analysis           |
| **CUBE**          | Full dimensional cross analysis                 | BI multi-dimensional data pivot, cross analysis        |

***

## Syntax Structure

```sql
SELECT 
    column1,
    column2,
    aggregate_function(column3) AS alias
FROM table_name
WHERE condition
GROUP BY 
    [ group_expression [, group_expression, ...] |
      GROUPING SETS (grouping_set [, grouping_set, ...]) |
      ROLLUP(expression [, expression, ...]) |
      CUBE(expression [, expression, ...]) ]
HAVING aggregate_condition
ORDER BY column
LIMIT n;
```

### Key Points

1. **SELECT clause constraint**: Non-aggregate columns in the SELECT list must appear in the GROUP BY clause
2. **Execution order**: FROM → WHERE → GROUP BY → HAVING → SELECT → ORDER BY → LIMIT
3. **HAVING filter**: Used to filter aggregation results, while WHERE filters original rows
4. **NULL value handling**: NULL is treated as a separate group

***

## Prepare Test Data

This document uses car dealership sales data as an example. Create the test view:

```sql
CREATE OR REPLACE VIEW dealer (id, city, car_model, quantity) AS
VALUES 
    (100, 'Fremont', 'Honda Civic', 10),
    (100, 'Fremont', 'Honda Accord', 15),
    (100, 'Fremont', 'Honda CRV', 7),
    (200, 'Dublin', 'Honda Civic', 20),
    (200, 'Dublin', 'Honda Accord', 10),
    (200, 'Dublin', 'Honda CRV', 3),
    (300, 'San Jose', 'Honda Civic', 5),
    (300, 'San Jose', 'Honda Accord', 8);
```

View the original data:

```sql
SELECT * FROM dealer ORDER BY id, car_model LIMIT 50;
```

**Query result**:

| id  | city     | car\_model   | quantity |
| --- | -------- | ------------ | -------- |
| 100 | Fremont  | Honda Accord | 15       |
| 100 | Fremont  | Honda CRV    | 7        |
| 100 | Fremont  | Honda Civic  | 10       |
| 200 | Dublin   | Honda Accord | 10       |
| 200 | Dublin   | Honda CRV    | 3        |
| 200 | Dublin   | Honda Civic  | 20       |
| 300 | San Jose | Honda Accord | 8        |
| 300 | San Jose | Honda Civic  | 5        |

***

## 1. Standard GROUP BY

### 1.1 Single-Column Grouping

Group by dealer ID and calculate the total quantity for each dealer:

```sql
SELECT 
    id, 
    SUM(quantity) AS total_quantity
FROM dealer
GROUP BY id
ORDER BY id
LIMIT 50;
```

**Query result**:

| id  | total\_quantity |
| --- | --------------- |
| 100 | 32              |
| 200 | 33              |
| 300 | 13              |

**Business interpretation**:

*   Dealer 100 (Fremont) sold 32 cars
*   Dealer 200 (Dublin) sold 33 cars
*   Dealer 300 (San Jose) sold 13 cars

***

### 1.2 Multi-Column Grouping

Group by the combination of city and car model:

```sql
SELECT 
    id, 
    city, 
    SUM(quantity) AS total_quantity
FROM dealer
GROUP BY id, city
ORDER BY total_quantity DESC
LIMIT 50;
```

**Query result**:

| id  | city     | total\_quantity |
| --- | -------- | --------------- |
| 200 | Dublin   | 33              |
| 100 | Fremont  | 32              |
| 300 | San Jose | 13              |

In this example, each dealer ID corresponds to a unique city, so the result is the same as single-column grouping.

***

### 1.3 Grouping with Expressions

Use a `CASE` expression to segment sales volumes:

```sql
SELECT 
    CASE 
        WHEN quantity < 10 THEN 'Low (< 10)'
        WHEN quantity < 15 THEN 'Medium (10-14)'
        ELSE 'High (>= 15)'
    END AS sales_level,
    COUNT(*) AS record_count,
    SUM(quantity) AS total_quantity
FROM dealer
GROUP BY 
    CASE 
        WHEN quantity < 10 THEN 'Low (< 10)'
        WHEN quantity < 15 THEN 'Medium (10-14)'
        ELSE 'High (>= 15)'
    END
ORDER BY sales_level
LIMIT 50;
```

**Query result**:

| sales\_level   | record\_count | total\_quantity |
| -------------- | ------------- | --------------- |
| High (>= 15)   | 2             | 35              |
| Low (< 10)     | 4             | 23              |
| Medium (10-14) | 2             | 20              |

**Business interpretation**:

* High-volume records (>= 15 cars): 2 records, 35 cars total
* Low-volume records (< 10 cars): 4 records, 23 cars total
* Medium-volume records (10-14 cars): 2 records, 20 cars total

***

### 1.4 Global Aggregation (No Grouping)

When GROUP BY is not used, a global aggregation is performed on the entire table:

```sql
SELECT SUM(quantity) AS total_quantity 
FROM dealer
LIMIT 50;
```

**Query result**:

| total\_quantity |
| --------------- |
| 78              |

The total quantity across all 8 records is 78 cars.

***

## 2. Combining Multiple Aggregate Functions

### 2.1 Common Aggregate Functions Summary

Use multiple aggregate functions in a single query:

```sql
SELECT 
    city,
    COUNT(*) AS model_count,
    SUM(quantity) AS total_quantity,
    AVG(quantity) AS avg_quantity,
    MAX(quantity) AS max_quantity,
    MIN(quantity) AS min_quantity
FROM dealer
GROUP BY city
ORDER BY total_quantity DESC
LIMIT 50;
```

**Query result**:

| city     | model\_count | total\_quantity | avg\_quantity      | max\_quantity | min\_quantity |
| -------- | ------------ | --------------- | ------------------ | ------------- | ------------- |
| Dublin   | 3            | 33              | 11.0               | 20            | 3             |
| Fremont  | 3            | 32              | 10.666666666666666 | 15            | 7             |
| San Jose | 2            | 13              | 6.5                | 8             | 5             |

**Business insights**:

* **Dublin**: 3 car models, average 11 cars per model, highest single item 20 (Honda Civic)
* **Fremont**: 3 car models, average 10.67 cars, relatively balanced distribution
* **San Jose**: Only 2 car models, average 6.5 cars, the smallest market

***

### 2.2 Statistics by Car Model Covering Number of Cities

Count how many cities each car model is sold in:

```sql
SELECT 
    car_model,
    SUM(quantity) AS total_sales,
    COUNT(DISTINCT city) AS city_count,
    ROUND(AVG(quantity), 2) AS avg_per_dealer
FROM dealer
GROUP BY car_model
ORDER BY total_sales DESC
LIMIT 50;
```

**Query result**:

| car\_model   | total\_sales | city\_count | avg\_per\_dealer |
| ------------ | ------------ | ----------- | ---------------- |
| Honda Civic  | 35           | 3           | 11.67            |
| Honda Accord | 33           | 3           | 11.00            |
| Honda CRV    | 10           | 2           | 5.00             |

**Business insights**:

* **Honda Civic**: Best-selling model, total sales 35 cars, covering 3 cities, average 11.67 per location
* **Honda Accord**: Total sales 33 cars, covering 3 cities
* **Honda CRV**: Lowest total sales, sold in only 2 cities (not present in San Jose market)

***

## 3. GROUPING SETS (Custom Grouping Sets)

### 3.1 Basic Concepts

`GROUPING SETS` allows generating multiple grouping results at different dimensions in a single query. It is essentially a shorthand for combining multiple `GROUP BY` queries via `UNION ALL`.

**Syntax**:

```sql
GROUP BY GROUPING SETS (
    (column1, column2),  -- Grouping set 1: group by column1 and column2
    (column1),           -- Grouping set 2: group by column1 only
    ()                   -- Grouping set 3: global aggregation (no grouping)
)
```

***

### 3.2 Multi-Dimensional Aggregation Analysis

Generate four-dimensional statistical results in a single query:

```sql
SELECT 
    city, 
    car_model, 
    SUM(quantity) AS total_quantity
FROM dealer
GROUP BY GROUPING SETS (
    (city, car_model),  -- City + model detail
    (city),             -- City subtotal
    (car_model),        -- Model subtotal
    ()                  -- Grand total
)
ORDER BY city, car_model
LIMIT 50;
```

**Query result**:

| city     | car\_model   | total\_quantity |
| -------- | ------------ | --------------- |
| NULL     | NULL         | 78              |
| NULL     | Honda Accord | 33              |
| NULL     | Honda CRV    | 10              |
| NULL     | Honda Civic  | 35              |
| Dublin   | NULL         | 33              |
| Dublin   | Honda Accord | 10              |
| Dublin   | Honda CRV    | 3               |
| Dublin   | Honda Civic  | 20              |
| Fremont  | NULL         | 32              |
| Fremont  | Honda Accord | 15              |
| Fremont  | Honda CRV    | 7               |
| Fremont  | Honda Civic  | 10              |
| San Jose | NULL         | 13              |
| San Jose | Honda Accord | 8               |
| San Jose | Honda Civic  | 5               |

**Result interpretation**:

* **Grand total row** (city=NULL, car\_model=NULL): Total sales 78 cars
* **Model subtotal rows** (city=NULL, car\_model has value): Cross-city totals for each car model
* **City subtotal rows** (city has value, car\_model=NULL): Cross-model totals for each city
* **Detail rows** (both city and car\_model have values): Specific city + model combination sales

**Equivalent query**:

```sql
-- GROUPING SETS is equivalent to the following UNION ALL query
SELECT city, car_model, SUM(quantity) FROM dealer GROUP BY city, car_model
UNION ALL
SELECT city, NULL, SUM(quantity) FROM dealer GROUP BY city
UNION ALL
SELECT NULL, car_model, SUM(quantity) FROM dealer GROUP BY car_model
UNION ALL
SELECT NULL, NULL, SUM(quantity) FROM dealer;
```

**Performance advantage**: `GROUPING SETS` only scans the data once internally, making it more efficient than `UNION ALL`.

***

### 3.3 Identifying Aggregation Levels

Use the `COALESCE` function to replace NULL values, making aggregation rows more readable:

```sql
SELECT 
    COALESCE(city, 'All Cities') AS city,
    COALESCE(car_model, 'All Models') AS car_model,
    SUM(quantity) AS total_quantity
FROM dealer
GROUP BY ROLLUP(city, car_model)
ORDER BY city, car_model
LIMIT 50;
```

**Query result**:

| city       | car\_model   | total\_quantity |
| ---------- | ------------ | --------------- |
| All Cities | All Models   | 78              |
| Dublin     | All Models   | 33              |
| Dublin     | Honda Accord | 10              |
| Dublin     | Honda CRV    | 3               |
| Dublin     | Honda Civic  | 20              |
| Fremont    | All Models   | 32              |
| Fremont    | Honda Accord | 15              |
| Fremont    | Honda CRV    | 7               |
| Fremont    | Honda Civic  | 10              |
| San Jose   | All Models   | 13              |
| San Jose   | Honda Accord | 8               |
| San Jose   | Honda Civic  | 5               |

***

## 4. ROLLUP (Hierarchical Rollup)

### 4.1 Basic Concepts

`ROLLUP` generates hierarchical rollups from fine granularity to global. For `ROLLUP(a, b, c)`, the following grouping sets are generated:

* `(a, b, c)` - Finest granularity
* `(a, b)` - Intermediate level
* `(a)` - Higher level
* `()` - Global aggregation

**Equivalence relationship**:

```sql
ROLLUP(city, car_model) 
-- Is equivalent to
GROUPING SETS (
    (city, car_model),
    (city),
    ()
)
```

***

### 4.2 Sales Hierarchy Rollup

Generate "city → car model" two-level rollup:

```sql
SELECT 
    city, 
    car_model, 
    SUM(quantity) AS total_quantity 
FROM dealer
GROUP BY ROLLUP(city, car_model)
LIMIT 50;
```

**Query result**:

| city     | car\_model   | total\_quantity |
| -------- | ------------ | --------------- |
| Fremont  | Honda Civic  | 10              |
| Fremont  | Honda Accord | 15              |
| Fremont  | Honda CRV    | 7               |
| Dublin   | Honda Civic  | 20              |
| Dublin   | Honda Accord | 10              |
| Dublin   | Honda CRV    | 3               |
| San Jose | Honda Civic  | 5               |
| San Jose | Honda Accord | 8               |
| Fremont  | NULL         | 32              |
| Dublin   | NULL         | 33              |
| San Jose | NULL         | 13              |
| NULL     | NULL         | 78              |

**Data hierarchy**:

1. **Detail layer** (first 8 rows): Sales of each car model in each city
2. **City subtotals** (car\_model=NULL): Total sales for each city
3. **Grand total** (city=NULL, car\_model=NULL): Total sales across all cities

***

### 4.3 Using the GROUPING() Function to Identify Levels

The `GROUPING()` function returns 0 or 1, used to distinguish real NULLs from aggregation markers:

* **Returns 0**: The column participates in grouping, the value is actual data
* **Returns 1**: The column does not participate in grouping, NULL indicates aggregation

```sql
SELECT 
    city,
    car_model,
    SUM(quantity) AS total_quantity,
    GROUPING(city) AS city_grouping,
    GROUPING(car_model) AS model_grouping
FROM dealer
GROUP BY ROLLUP(city, car_model)
ORDER BY city_grouping, city, model_grouping, car_model
LIMIT 50;
```

**Query result**:

| city     | car\_model   | total\_quantity | city\_grouping | model\_grouping |
| -------- | ------------ | --------------- | -------------- | --------------- |
| Dublin   | Honda Accord | 10              | 0              | 0               |
| Dublin   | Honda CRV    | 3               | 0              | 0               |
| Dublin   | Honda Civic  | 20              | 0              | 0               |
| Dublin   | NULL         | 33              | 0              | 1               |
| Fremont  | Honda Accord | 15              | 0              | 0               |
| Fremont  | Honda CRV    | 7               | 0              | 0               |
| Fremont  | Honda Civic  | 10              | 0              | 0               |
| Fremont  | NULL         | 32              | 0              | 1               |
| San Jose | Honda Accord | 8               | 0              | 0               |
| San Jose | Honda Civic  | 5               | 0              | 0               |
| San Jose | NULL         | 13              | 0              | 1               |
| NULL     | NULL         | 78              | 1              | 1               |

**GROUPING() value interpretation**:

* (**0, 0**): Detail data, both columns participate in grouping
* (**0, 1**): City subtotal, only city participates in grouping
* (**1, 1**): Grand total, neither column participates in grouping

***

## 5. CUBE (Full Dimensional Cross Analysis)

### 5.1 Basic Concepts

`CUBE` generates grouping sets for all possible combinations of the specified columns. For `CUBE(a, b)`, it generates 2^2 = 4 grouping sets:

* `(a, b)` - Detail
* `(a)` - Aggregated by a
* `(b)` - Aggregated by b
* `()` - Global aggregation

**Equivalence relationship**:

```sql
CUBE(city, car_model)
-- Is equivalent to
GROUPING SETS (
    (city, car_model),
    (city),
    (car_model),
    ()
)
```

***

### 5.2 Multi-Dimensional Cross Analysis

Generate all dimension combinations for city and car model:

```sql
SELECT 
    city, 
    car_model, 
    SUM(quantity) AS total_quantity 
FROM dealer
GROUP BY city, car_model WITH CUBE
LIMIT 50;
```

**Query result**:

| city     | car\_model   | total\_quantity |
| -------- | ------------ | --------------- |
| Fremont  | Honda Civic  | 10              |
| Fremont  | Honda Accord | 15              |
| Fremont  | Honda CRV    | 7               |
| Dublin   | Honda Civic  | 20              |
| Dublin   | Honda Accord | 10              |
| Dublin   | Honda CRV    | 3               |
| San Jose | Honda Civic  | 5               |
| San Jose | Honda Accord | 8               |
| NULL     | Honda CRV    | 10              |
| NULL     | Honda Civic  | 35              |
| NULL     | Honda Accord | 33              |
| Fremont  | NULL         | 32              |
| Dublin   | NULL         | 33              |
| San Jose | NULL         | 13              |
| NULL     | NULL         | 78              |

**Result includes**:

1. **Detail rows** (first 8 rows): City + model combinations
2. **Model subtotal rows** (city=NULL): Cross-city model sales
3. **City subtotal rows** (car\_model=NULL): Cross-model city sales
4. **Grand total row** (city=NULL, car\_model=NULL): Global total

***

### 5.3 Identifying Aggregation Levels

Use a `CASE` statement with the `GROUPING()` function to identify the aggregation level of each row:

```sql
SELECT 
    city,
    car_model,
    SUM(quantity) AS total_quantity,
    CASE 
        WHEN GROUPING(city) = 1 AND GROUPING(car_model) = 1 THEN 'Total'
        WHEN GROUPING(city) = 0 AND GROUPING(car_model) = 1 THEN 'City Subtotal'
        WHEN GROUPING(city) = 1 AND GROUPING(car_model) = 0 THEN 'Model Subtotal'
        ELSE 'Detail'
    END AS aggregation_level
FROM dealer
GROUP BY CUBE(city, car_model)
ORDER BY 
    GROUPING(city),
    GROUPING(car_model),
    city,
    car_model
LIMIT 50;
```

**Query result**:

| city     | car\_model   | total\_quantity | aggregation\_level |
| -------- | ------------ | --------------- | ------------------ |
| Dublin   | Honda Accord | 10              | Detail             |
| Dublin   | Honda CRV    | 3               | Detail             |
| Dublin   | Honda Civic  | 20              | Detail             |
| Fremont  | Honda Accord | 15              | Detail             |
| Fremont  | Honda CRV    | 7               | Detail             |
| Fremont  | Honda Civic  | 10              | Detail             |
| San Jose | Honda Accord | 8               | Detail             |
| San Jose | Honda Civic  | 5               | Detail             |
| Dublin   | NULL         | 33              | City Subtotal      |
| Fremont  | NULL         | 32              | City Subtotal      |
| San Jose | NULL         | 13              | City Subtotal      |
| NULL     | Honda Accord | 33              | Model Subtotal     |
| NULL     | Honda CRV    | 10              | Model Subtotal     |
| NULL     | Honda Civic  | 35              | Model Subtotal     |
| NULL     | NULL         | 78              | Total              |

This query clearly identifies the aggregation level to which each row belongs.

***

### 5.4 ROLLUP vs CUBE

| Dimension          | ROLLUP         | CUBE                |
| --------------- | -------------- | ------------------- |
| **Generated grouping sets** | Hierarchical subset (left to right) | All possible combinations |
| **ROLLUP(a,b**) | (a,b), (a), () | (a,b), (a), (b), () |
| **Number of groupings** | n+1 (n = number of columns) | 2^n |
| **Use case**     | Hierarchical reports, top-down analysis | Multi-dimensional cross analysis, BI pivot tables |
| **Performance**  | Fewer grouping sets, better performance | More grouping sets, higher performance overhead |

**Selection suggestions**:

* Use `ROLLUP` when you need **hierarchical rollups** (e.g., Region → City → Store)
* Use `CUBE` when you need **multi-dimensional cross analysis** (e.g., Region x Product x Time)
* Use `GROUPING SETS` when you need **custom combinations**

***

## 6. HAVING Clause: Filtering Aggregation Results

### 6.1 WHERE vs HAVING

| Clause      | Execution Timing | Target     | Available Functions            |
| ---------- | ---- | -------- | ----------------- |
| **WHERE**  | Before grouping  | Original row data | Scalar functions, column comparisons     |
| **HAVING** | After grouping   | Aggregation results | Aggregate functions, GROUP BY columns |

**Execution order**: FROM → WHERE → GROUP BY → HAVING → SELECT → ORDER BY → LIMIT

***

### 6.2 Using HAVING to Filter Aggregation Results

Filter cities with total sales exceeding 15 cars:

```sql
SELECT 
    city,
    COUNT(*) AS record_count,
    SUM(quantity) AS total_quantity
FROM dealer
GROUP BY city
HAVING SUM(quantity) > 15
ORDER BY total_quantity DESC
LIMIT 50;
```

**Query result**:

| city    | record\_count | total\_quantity |
| ------- | ------------- | --------------- |
| Dublin  | 3             | 33              |
| Fremont | 3             | 32              |

San Jose (total sales 13 cars) is filtered out because it does not meet the `HAVING` condition.

***

### 6.3 Combining WHERE and HAVING

Filter original data with `WHERE` first, then filter aggregation results with `HAVING`:

```sql
SELECT 
    city,
    COUNT(*) AS record_count,
    SUM(quantity) AS total_quantity
FROM dealer
WHERE quantity >= 10  -- Filter first: only include records with quantity >= 10
GROUP BY city
HAVING COUNT(*) >= 2  -- Filter after: only show cities with record count >= 2
ORDER BY total_quantity DESC
LIMIT 50;
```

**Execution logic**:

1. **WHERE filter**: Exclude records where quantity < 10 (filters out 4 records)
2. **GROUP BY grouping**: Group remaining records by city
3. **HAVING filter**: Keep only groups with record count >= 2

***

## 7. Advanced Use Cases

### 7.1 Row-to-Column: Pivot Analysis

Convert car models from rows to columns to achieve a pivot table effect:

```sql
SELECT 
    city,
    SUM(CASE WHEN car_model = 'Honda Civic' THEN quantity ELSE 0 END) AS civic_sales,
    SUM(CASE WHEN car_model = 'Honda Accord' THEN quantity ELSE 0 END) AS accord_sales,
    SUM(CASE WHEN car_model = 'Honda CRV' THEN quantity ELSE 0 END) AS crv_sales,
    SUM(quantity) AS total_sales
FROM dealer
GROUP BY city
ORDER BY total_sales DESC
LIMIT 50;
```

**Query result**:

| city     | civic\_sales | accord\_sales | crv\_sales | total\_sales |
| -------- | ------------ | ------------- | ---------- | ------------ |
| Dublin   | 20           | 10            | 3          | 33           |
| Fremont  | 10           | 15            | 7          | 32           |
| San Jose | 5            | 8             | 0          | 13           |

**Business value**:

* Clearly shows the sales distribution of each car model in each city
* San Jose has no CRV sales records (shown as 0)
* Suitable for Excel reports and BI dashboards

***

### 7.2 Proportion Analysis: Window Functions and GROUP BY

Calculate the sales proportion of each car model within its city:

```sql
SELECT 
    city,
    car_model,
    quantity,
    SUM(quantity) OVER (PARTITION BY city) AS city_total,
    ROUND(quantity * 100.0 / SUM(quantity) OVER (PARTITION BY city), 2) AS percentage
FROM dealer
ORDER BY city, car_model
LIMIT 50;
```

**Query result**:

| city     | car\_model   | quantity | city\_total | percentage |
| -------- | ------------ | -------- | ----------- | ---------- |
| Dublin   | Honda Accord | 10       | 33          | 30.30      |
| Dublin   | Honda CRV    | 3        | 33          | 9.09       |
| Dublin   | Honda Civic  | 20       | 33          | 60.61      |
| Fremont  | Honda Accord | 15       | 32          | 46.88      |
| Fremont  | Honda CRV    | 7        | 32          | 21.88      |
| Fremont  | Honda Civic  | 10       | 32          | 31.25      |
| San Jose | Honda Accord | 8        | 13          | 61.54      |
| San Jose | Honda Civic  | 5        | 13          | 38.46      |

**Business insights**:

* **Dublin**: Honda Civic accounts for 60.61%, the absolute flagship model
* **Fremont**: Sales distribution is relatively balanced, Accord accounts for the highest (46.88%)
* **San Jose**: Accord accounts for 61.54%, clear market preference

**Technical note**: The window function `SUM() OVER (PARTITION BY city)` calculates the total sales for each city without changing the number of rows.

***

### 7.3 Year-over-Year and Month-over-Month Analysis Pattern

Although the sample data does not include a time dimension, here is a standard YoY/MoM analysis SQL pattern:

```sql
-- Example: monthly sales with month-over-month growth rate
SELECT 
    DATE_FORMAT(sale_date, 'yyyy-MM') AS month,
    SUM(quantity) AS monthly_sales,
    LAG(SUM(quantity)) OVER (ORDER BY DATE_FORMAT(sale_date, 'yyyy-MM')) AS prev_month_sales,
    ROUND(
        (SUM(quantity) - LAG(SUM(quantity)) OVER (ORDER BY DATE_FORMAT(sale_date, 'yyyy-MM'))) * 100.0 / 
        LAG(SUM(quantity)) OVER (ORDER BY DATE_FORMAT(sale_date, 'yyyy-MM')), 
        2
    ) AS mom_growth_rate
FROM sales_table
GROUP BY DATE_FORMAT(sale_date, 'yyyy-MM')
ORDER BY month;
```

**Key techniques**:

* `LAG()` window function to get the previous row's value
* MoM growth rate = (current value - previous value) / previous value x 100%

***

### 7.4 TopN Analysis: Taking Top N per Group

Use window functions combined with GROUP BY to implement grouped TopN:

```sql
-- Example: top 2 car models by sales in each city
SELECT *
FROM (
    SELECT 
        city,
        car_model,
        quantity,
        ROW_NUMBER() OVER (PARTITION BY city ORDER BY quantity DESC) AS rank
    FROM dealer
) ranked
WHERE rank <= 2
ORDER BY city, rank;
```

**Expected logic** (based on current data):

* Dublin: Honda Civic (20), Honda Accord (10)
* Fremont: Honda Accord (15), Honda Civic (10)
* San Jose: Honda Accord (8), Honda Civic (5)

***

## 8. Performance Optimization and Best Practices

### 8.1 Query Performance Optimization

#### 1. Use LIMIT Appropriately

For large datasets, always add `LIMIT` to restrict the number of returned rows:

```sql
-- Recommended
SELECT city, SUM(quantity) 
FROM large_table 
GROUP BY city
LIMIT 100;

-- Avoid: may return millions of rows
SELECT city, SUM(quantity) 
FROM large_table 
GROUP BY city;
```

#### 2. Choose the Right Aggregation Tool

| Requirement     | Recommended Solution  | Grouping Sets Generated | Performance |
| ------ | ------------------------- | ------------ | -------- |
| Simple hierarchical rollup | `ROLLUP`        | n+1          | Highest |
| Multi-dimensional cross analysis | `CUBE`          | 2^n          | Moderate |
| Custom grouping sets | `GROUPING SETS` | Custom       | High |

**Example**: For 3-column grouping

* `ROLLUP(a,b,c)` generates 4 grouping sets
* `CUBE(a,b,c)` generates 8 grouping sets
* `GROUPING SETS` can customize any combination

#### 3. Reduce Grouping Column Cardinality

Use functions to reduce granularity on high-cardinality columns (e.g., ID, timestamp):

```sql
-- Avoid: grouping by second-level timestamp
GROUP BY timestamp  -- May generate millions of groups

-- Recommended: group by hour or day
GROUP BY DATE_FORMAT(timestamp, 'yyyy-MM-dd')
GROUP BY DATE_TRUNC('hour', timestamp)
```

#### 4. WHERE Filtering is Better than HAVING Filtering

Try to filter data in `WHERE` to reduce the data volume processed by `GROUP BY`:

```sql
-- Recommended: filter first, then group
SELECT city, SUM(quantity)
FROM dealer
WHERE car_model = 'Honda Civic'  -- Filter first to reduce data volume
GROUP BY city;

-- Avoid: group first, then filter (processes unnecessary data)
SELECT city, car_model, SUM(quantity)
FROM dealer
GROUP BY city, car_model
HAVING car_model = 'Honda Civic';
```

***

### 8.2 Common Errors and Solutions

#### Error 1: SELECT Column Not in GROUP BY

```sql
-- Incorrect example
SELECT city, car_model, quantity
FROM dealer
GROUP BY city;
-- Error: car_model and quantity are not grouped or aggregated

-- Correct solution 1: Add to GROUP BY
SELECT city, car_model, SUM(quantity)
FROM dealer
GROUP BY city, car_model;

-- Correct solution 2: Use aggregate functions
SELECT city, MAX(car_model), SUM(quantity)
FROM dealer
GROUP BY city;
```

#### Error 2: Using Aggregate Functions in WHERE

```sql
-- Incorrect example
SELECT city, SUM(quantity)
FROM dealer
WHERE SUM(quantity) > 20  -- WHERE cannot use aggregate functions
GROUP BY city;

-- Correct solution: Use HAVING
SELECT city, SUM(quantity)
FROM dealer
GROUP BY city
HAVING SUM(quantity) > 20;
```

#### Error 3: Confusing ROLLUP/CUBE Syntax

```sql
-- Incorrect example
GROUP BY city, ROLLUP(car_model)  -- Mixed syntax not supported

-- Correct solution
GROUP BY ROLLUP(city, car_model)
```

#### Error 4: Ignoring NULL Value Impact

```sql
-- In ROLLUP/CUBE, NULL can be either a real NULL or an aggregation marker
-- Use GROUPING() function to distinguish

SELECT 
    CASE WHEN GROUPING(city) = 1 THEN 'Total' ELSE city END AS city,
    SUM(quantity)
FROM dealer
GROUP BY ROLLUP(city);
```

***

### 8.3 Data Quality Checks

#### Verify Grouping Completeness

Verify that the sum of group subtotals equals the grand total:

```sql
-- Method 1: Use ROLLUP to automatically generate grand total row
SELECT 
    COALESCE(city, 'TOTAL') AS city,
    SUM(quantity) AS total
FROM dealer
GROUP BY ROLLUP(city);

-- Method 2: Manual verification
WITH group_totals AS (
    SELECT SUM(quantity) AS grouped_sum
    FROM dealer
    GROUP BY city
),
grand_total AS (
    SELECT SUM(quantity) AS total_sum
    FROM dealer
)
SELECT 
    (SELECT SUM(grouped_sum) FROM group_totals) AS sum_of_groups,
    (SELECT total_sum FROM grand_total) AS grand_total,
    CASE 
        WHEN (SELECT SUM(grouped_sum) FROM group_totals) = (SELECT total_sum FROM grand_total)
        THEN 'PASS'
        ELSE 'FAIL'
    END AS validation_result;
```

***

## 9. Practical Case Summary

### 9.1 Sales Analysis Report

**Requirement**: Generate a sales report with detail rows, subtotals, and grand total

```sql
SELECT 
    COALESCE(city, 'All Cities') AS city,
    COALESCE(car_model, 'All Models') AS car_model,
    SUM(quantity) AS total_quantity
FROM dealer
GROUP BY ROLLUP(city, car_model)
ORDER BY 
    GROUPING(city),
    city,
    GROUPING(car_model),
    car_model
LIMIT 50;
```

***

### 9.2 Multi-Dimensional Cross Analysis

**Requirement**: BI pivot table, needing all dimension combinations of city and car model

```sql
SELECT 
    city,
    car_model,
    SUM(quantity) AS total_quantity,
    CASE 
        WHEN GROUPING(city) = 1 AND GROUPING(car_model) = 1 THEN 'Grand Total'
        WHEN GROUPING(city) = 1 THEN 'Model Total'
        WHEN GROUPING(car_model) = 1 THEN 'City Total'
        ELSE 'Detail'
    END AS level
FROM dealer
GROUP BY CUBE(city, car_model)
ORDER BY 
    GROUPING(city),
    GROUPING(car_model),
    city,
    car_model
LIMIT 50;
```

***

### 9.3 Top/Bottom N Analysis

**Requirement**: Find the cities with the highest and lowest sales

```sql
-- Top 2 cities
SELECT city, SUM(quantity) AS total_quantity
FROM dealer
GROUP BY city
ORDER BY total_quantity DESC
LIMIT 2;

-- Bottom 2 cities
SELECT city, SUM(quantity) AS total_quantity
FROM dealer
GROUP BY city
ORDER BY total_quantity ASC
LIMIT 2;
```

***

### 9.4 Proportion and Ranking

**Requirement**: Calculate the sales proportion and ranking of each car model

```sql
SELECT 
    car_model,
    SUM(quantity) AS total_sales,
    ROUND(SUM(quantity) * 100.0 / (SELECT SUM(quantity) FROM dealer), 2) AS percentage,
    RANK() OVER (ORDER BY SUM(quantity) DESC) AS rank
FROM dealer
GROUP BY car_model
ORDER BY total_sales DESC
LIMIT 50;
```

***

## 10. Feature Comparison and Selection Guide

### 10.1 Comparison of Four Grouping Methods

| Feature      | GROUP BY | GROUPING SETS | ROLLUP | CUBE     |
| --------- | -------- | ------------- | ------ | -------- |
| **Syntax complexity** | Simple       | Moderate          | Simple     | Simple       |
| **Grouping sets generated** | 1        | Custom           | n+1    | 2^n       |
| **Flexibility**   | Low        | High             | Medium      | Medium        |
| **Performance**    | Best       | Good             | Good      | Poorer (with many columns) |
| **Applicable scenarios**  | Basic statistics     | Custom multi-dimensional analysis    | Hierarchical reports   | Full dimensional cross analysis   |

***

### 10.2 Selection Decision Tree

```
Do you need multi-dimensional rollup?
├─ No → Use standard GROUP BY
└─ Yes → Which dimension combinations are needed?
    ├─ All possible combinations → Use CUBE
    ├─ Hierarchical rollup (from detail to total) → Use ROLLUP
    └─ Custom specific combinations → Use GROUPING SETS
```

***

### 10.3 Recommended Use Cases

| Business Scenario     | Recommended Solution           | Example           |
| -------- | ------------------------------ | -------------- |
| Daily statistics and reports   | `GROUP BY`                     | Statistics by department     |
| Financial hierarchical rollup   | `ROLLUP`                       | Company → Department → Team hierarchical rollup |
| BI data pivot tables | `CUBE`                         | Product x Region x Time three-dimensional analysis |
| Custom business reports  | `GROUPING SETS`                | Generate daily, weekly, and monthly reports simultaneously |
| Proportion analysis     | `GROUP BY` + window functions  | Sales proportion of each product |
| Top N analysis | `GROUP BY` + `LIMIT`           | Top 10 products by sales |

***

## 11. Advanced Techniques

### 11.1 Dynamic Grouping

Use variables or subqueries to implement dynamic grouping conditions (example logic):

```sql
-- Dynamic grouping based on sales volume range
SELECT 
    CASE 
        WHEN SUM(quantity) >= 30 THEN 'High Volume'
        WHEN SUM(quantity) >= 15 THEN 'Medium Volume'
        ELSE 'Low Volume'
    END AS volume_tier,
    COUNT(DISTINCT city) AS city_count
FROM (
    SELECT city, SUM(quantity) AS city_total
    FROM dealer
    GROUP BY city
) city_summary
GROUP BY 
    CASE 
        WHEN city_total >= 30 THEN 'High Volume'
        WHEN city_total >= 15 THEN 'Medium Volume'
        ELSE 'Low Volume'
    END;
```

***

### 11.2 Recursive Rollup (Simulated)

Although Singdata Lakehouse does not yet directly support recursive CTE, you can simulate multi-level rollups via UNION ALL:

```sql
-- Three-level rollup: Detail, City Subtotal, Grand Total
SELECT city, car_model, quantity, 'Detail' AS level
FROM dealer
UNION ALL
SELECT city, NULL, SUM(quantity), 'City Subtotal'
FROM dealer
GROUP BY city
UNION ALL
SELECT NULL, NULL, SUM(quantity), 'Grand Total'
FROM dealer
ORDER BY 
    CASE level 
        WHEN 'Detail' THEN 1
        WHEN 'City Subtotal' THEN 2
        WHEN 'Grand Total' THEN 3
    END,
    city,
    car_model;
```

***

### 11.3 NULL Value Handling Tips

#### Tip 1: Distinguish Real NULLs from Aggregation NULLs

```sql
SELECT 
    city,
    car_model,
    SUM(quantity) AS total,
    CASE 
        WHEN GROUPING(city) = 1 THEN '[Subtotal]'
        WHEN city IS NULL THEN '[Real NULL]'
        ELSE city
    END AS city_display
FROM dealer
GROUP BY ROLLUP(city, car_model);
```

#### Tip 2: Use COALESCE to Beautify Output

```sql
SELECT 
    COALESCE(city, '📊 All Cities') AS city,
    COALESCE(car_model, '🚗 All Models') AS car_model,
    SUM(quantity) AS total
FROM dealer
GROUP BY CUBE(city, car_model);
```

***

## 12. Summary

### Key Takeaways

1. **GROUP BY** is the foundation of data aggregation analysis; mastering its usage is an essential SQL analysis skill
2. **GROUPING SETS / ROLLUP / CUBE** provide powerful multi-dimensional analysis capabilities, generating multi-level rollups in a single query
3. **HAVING** is used to filter aggregation results, working with WHERE for flexible data filtering
4. **Window functions** combined with GROUP BY enable complex proportion, ranking, and period-over-period analysis
5. **Performance optimization** requires balancing flexibility and efficiency, choosing the right grouping method

***

### Learning Path Suggestions

1. **Basic stage**: Master standard GROUP BY and common aggregate functions
2. **Advanced stage**: Learn the use cases of GROUPING SETS, ROLLUP, and CUBE
3. **Expert stage**: Combine window functions and CTE for complex business analysis
4. **Practical stage**: Apply to real business scenarios and optimize query performance

***

### Quick Reference

```sql
-- Basic grouping
SELECT column, AGG_FUNC(column) FROM table GROUP BY column;

-- Multi-dimensional grouping
SELECT col1, col2, AGG_FUNC(col3) 
FROM table 
GROUP BY GROUPING SETS ((col1, col2), (col1), ());

-- Hierarchical rollup
SELECT col1, col2, AGG_FUNC(col3) 
FROM table 
GROUP BY ROLLUP(col1, col2);

-- Cross analysis
SELECT col1, col2, AGG_FUNC(col3) 
FROM table 
GROUP BY col1, col2 WITH CUBE;

-- Conditional filtering
SELECT col1, AGG_FUNC(col2) 
FROM table 
WHERE condition
GROUP BY col1 
HAVING AGG_FUNC(col2) > value;
```
