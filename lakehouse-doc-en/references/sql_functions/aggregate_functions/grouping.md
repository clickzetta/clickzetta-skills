# GROUPING

#### Introduction

The `GROUPING` function is used with `GROUPING SETS`, `ROLLUP`, and `CUBE` to distinguish whether a column value in a given row is a real grouping value or a rollup subtotal. Returns `1` when the column is aggregated in the current row (the dimension did not participate in grouping, meaning the row is a subtotal), and `0` when the column is a real grouping value.

It is typically combined with `CASE` to replace the `NULL` values in subtotal rows with labels such as "All" in reports, making it easy to tell apart genuine `NULL` group values from aggregation-produced `NULL` values.

#### Syntax

```Plain
GROUPING(<expr>)
```

#### Parameters

* `expr`: A column or expression that appears in the `GROUP BY` clause. It must match a dimension referenced in `GROUPING SETS`, `ROLLUP`, or `CUBE`.

#### Return Value

* Return type is `INT` (`0` or `1`).
* Returns `0`: the dimension participates in the grouping for the current row, and the column value is a real group value.
* Returns `1`: the dimension does not participate in the grouping for the current row, and the corresponding column value is aggregation-produced `NULL` (a subtotal row).

#### Examples

Create a table and insert test data:

```sql
CREATE TABLE doc_sales (
    region   STRING,
    category STRING,
    amount   INT
);

INSERT INTO doc_sales VALUES
    ('East', 'Electronics', 100),
    ('East', 'Clothing',     80),
    ('West', 'Electronics', 120),
    ('West', 'Clothing',     60);
```

Use `GROUPING SETS` to query subtotals and grand totals across dimensions, and use `GROUPING` to flag subtotal rows:

```sql
SELECT
    CASE WHEN GROUPING(region)   = 1 THEN 'All Regions'    ELSE region   END AS region,
    CASE WHEN GROUPING(category) = 1 THEN 'All Categories' ELSE category END AS category,
    SUM(amount)        AS total_amount,
    GROUPING(region)   AS g_region,
    GROUPING(category) AS g_category
FROM doc_sales
GROUP BY GROUPING SETS ((region, category), (region), (category), ())
ORDER BY g_region, g_category, region, category;
```

Query result:

```
+---------------+----------------+--------------+----------+------------+
| region        | category       | total_amount | g_region | g_category |
+---------------+----------------+--------------+----------+------------+
| East          | Clothing       | 80           | 0        | 0          |
| East          | Electronics    | 100          | 0        | 0          |
| West          | Clothing       | 60           | 0        | 0          |
| West          | Electronics    | 120          | 0        | 0          |
| East          | All Categories | 180          | 0        | 1          |
| West          | All Categories | 180          | 0        | 1          |
| All Regions   | Clothing       | 140          | 1        | 0          |
| All Regions   | Electronics    | 220          | 1        | 0          |
| All Regions   | All Categories | 360          | 1        | 1          |
+---------------+----------------+--------------+----------+------------+
```

Result interpretation:

* `g_region = 0, g_category = 0`: detail row — both `region` and `category` are real group values.
* `g_region = 0, g_category = 1`: subtotal by region — the `category` dimension is aggregated, shown as "All Categories".
* `g_region = 1, g_category = 0`: subtotal by category — the `region` dimension is aggregated, shown as "All Regions".
* `g_region = 1, g_category = 1`: grand total row — both dimensions are aggregated, corresponding to the empty set `()` in `GROUPING SETS`.

> ⚠️ **Note**: The argument to `GROUPING` must be a column actually referenced by `GROUPING SETS`, `ROLLUP`, or `CUBE` in the `GROUP BY` clause. Calling `GROUPING` on a column not in the grouping will cause an error.
