# GROUPING_ID

#### Introduction

The `GROUPING_ID` function identifies, as an integer bitmask, which aggregation level a row belongs to in a multi-dimension grouping query (`GROUPING SETS`, `ROLLUP`, `CUBE`). The difference from `GROUPING`: for a single dimension, the two functions return the same result; for multiple dimensions, `GROUPING_ID` combines the `GROUPING` values of each dimension into a single integer, with the first argument occupying the most significant bit, eliminating the need to call `GROUPING` individually for each dimension.

#### Syntax

```Plain
GROUPING_ID(expr1 [, expr2, ...])
```

#### Parameters

* `exprN`: Columns or expressions that appear in the `GROUP BY` clause. The order corresponds to the bit-weight of the bitmask — the first argument maps to the most significant bit, and the last argument maps to the least significant bit.

#### Return Value

* Return type is `BIGINT`.
* The return value is the integer formed by combining the `GROUPING` values of each dimension as bits. When a dimension is aggregated (rolled up to a subtotal or grand total in the current row), the corresponding bit is `1`; when the dimension participates in grouping, the bit is `0`.
* For a single dimension: returns `1` when aggregated and `0` when grouped — identical to `GROUPING(expr)`.
* For multiple dimensions: `GROUPING_ID(a, b)` is equivalent to `GROUPING(a) * 2 + GROUPING(b)`.

#### Examples

**Single-dimension verification**

```sql
SELECT GROUPING_ID(v)
FROM (SELECT 1 AS v) t
GROUP BY GROUPING SETS ((v), ());
```

```
+----------------+
| grouping_id(v) |
+----------------+
| 0              |
| 1              |
+----------------+
```

`0` means the current row is grouped by `v` (a detail row); `1` means the current row is the grand total over all values of `v`.

**Multi-dimension GROUPING SETS scenario**

The following example aggregates sales by region, product, and various rollup levels, using `GROUPING_ID` to identify which level each row belongs to:

```sql
-- Prepare test data
CREATE TABLE doc_sales (
  region  STRING,
  product STRING,
  amount  DECIMAL(10, 2)
);

INSERT INTO doc_sales VALUES
  ('North', 'A', 100),
  ('North', 'B', 200),
  ('South', 'A', 150),
  ('South', 'B', 300);
```

```sql
SELECT
  region,
  product,
  SUM(amount)                  AS total_amount,
  GROUPING_ID(region, product) AS gid,
  GROUPING(region)             AS g_region,
  GROUPING(product)            AS g_product
FROM doc_sales
GROUP BY GROUPING SETS (
  (region, product),  -- detail: by region + product
  (region),           -- subtotal: by region
  (product),          -- subtotal: by product
  ()                  -- grand total
)
ORDER BY gid, region, product;
```

```
+--------+---------+--------------+-----+----------+-----------+
| region | product | total_amount | gid | g_region | g_product |
+--------+---------+--------------+-----+----------+-----------+
| North  | A       | 100.00       | 0   | 0        | 0         |
| North  | B       | 200.00       | 0   | 0        | 0         |
| South  | A       | 150.00       | 0   | 0        | 0         |
| South  | B       | 300.00       | 0   | 0        | 0         |
| North  | NULL    | 300.00       | 1   | 0        | 1         |
| South  | NULL    | 450.00       | 1   | 0        | 1         |
| NULL   | A       | 250.00       | 2   | 1        | 0         |
| NULL   | B       | 500.00       | 2   | 1        | 0         |
| NULL   | NULL    | 750.00       | 3   | 1        | 1         |
+--------+---------+--------------+-----+----------+-----------+
```

`gid` meaning:

| `gid` | Binary | Description                                      |
| ----- | ------ | ------------------------------------------------ |
| `0`   | `00`   | Grouped by region + product (detail row)         |
| `1`   | `01`   | Subtotal by region (product is aggregated)       |
| `2`   | `10`   | Subtotal by product (region is aggregated)       |
| `3`   | `11`   | Grand total (both dimensions are aggregated)     |

**Filter to a specific level using GROUPING_ID**

```sql
SELECT region, SUM(amount) AS subtotal
FROM doc_sales
GROUP BY GROUPING SETS ((region), ())
HAVING GROUPING_ID(region) = 0;
```

```
+--------+----------+
| region | subtotal |
+--------+----------+
| North  | 300.00   |
| South  | 450.00   |
+--------+----------+
```

Only rows where `gid = 0` are kept — subtotals grouped by region — excluding the grand total row.

#### Notes

* Arguments to `GROUPING_ID` must be columns or expressions that actually appear in the `GROUP BY` clause; otherwise an error is raised.
* Argument order affects bit-weight: the first argument maps to the most significant bit. Changing argument order changes the returned integer value without changing semantics — be consistent when interpreting results.
* `NULL` in the result can come from two sources: the original data itself being `NULL`, or a placeholder `NULL` produced when the corresponding dimension is aggregated. Use `GROUPING(col) = 1` or `GROUPING_ID` to distinguish the two.
* Use only in queries that include `GROUPING SETS`, `ROLLUP`, or `CUBE`; calling it in a plain `GROUP BY` is meaningless (all rows return `GROUPING_ID = 0`).

#### Related Documentation

* [GROUPING](grouping.md)
* [GROUP BY GROUPING SETS / ROLLUP / CUBE](../../sql_syntax/groupby-extensions.md)
