### CORR Function

```
corr(y, x)
```

#### Description

The `CORR` function computes the Pearson correlation coefficient between two numeric columns. The correlation coefficient measures the degree of linear relationship between two variables, with values ranging from -1 to 1.

#### Parameters

* `y`: A numeric expression serving as the dependent variable. Must be a numeric type that can be cast to `DOUBLE`.
* `x`: A numeric expression serving as the independent variable. Must be a numeric type that can be cast to `DOUBLE`.

#### Return Type

* Returns a `DOUBLE` value representing the Pearson correlation coefficient, in the range [-1, 1].
  * `1`: Perfect positive correlation (as x increases, y increases)
  * `-1`: Perfect negative correlation (as x increases, y decreases)
  * `0`: No linear correlation
  * Close to `1` or `-1`: Strong correlation
  * Close to `0`: Weak or no correlation

#### Notes

* During computation, `NULL` values are ignored and excluded from the calculation.
* If all x values are identical or all y values are identical (standard deviation is 0), returns `NULL`.
* If there are fewer than 2 valid data points, returns `NULL`.
* Formula: `corr(y, x) = covar_pop(y, x) / (stddev_pop(y) * stddev_pop(x))`, i.e., the covariance divided by the product of the standard deviations of the two variables.

#### Examples

1. Basic usage: compute the correlation coefficient

```sql
SELECT corr(c1, c2)
FROM VALUES (3, 2), (3, 3), (3, 3), (6, 4) AS tab(c1, c2);
+--------------------+
| corr(c1, c2)       |
+--------------------+
| 0.816496580927726  |
+--------------------+
```

2. Perfect positive correlation (y = x)

```sql
SELECT corr(x, y)
FROM VALUES (1, 1), (2, 2), (3, 3), (4, 4) AS t(x, y);
+-------------+
| corr(x, y)  |
+-------------+
| 1.0         |
+-------------+
```

3. Perfect negative correlation (y = -x)

```sql
SELECT corr(x, y)
FROM VALUES (1, -1), (2, -2), (3, -3), (4, -4) AS t(x, y);
+-------------+
| corr(x, y)  |
+-------------+
| -1.0        |
+-------------+
```

4. No correlation (x and y are independent)

```sql
SELECT corr(x, y)
FROM VALUES (1, 1), (2, 1), (3, 1), (4, 1) AS t(x, y);
+-------------+
| corr(x, y)  |
+-------------+
| NULL        |
+-------------+
```

5. Compute correlation coefficient by group

```sql
SELECT
  category,
  corr(price, quantity) as price_quantity_corr
FROM VALUES
  ('A', 10, 100),
  ('A', 20, 80),
  ('A', 30, 60),
  ('B', 15, 50),
  ('B', 25, 40),
  ('B', 35, 30)
AS sales(category, price, quantity)
GROUP BY category;
+----------+----------------------+
| category | price_quantity_corr  |
+----------+----------------------+
| A        | -1.0                 |
| B        | -1.0                 |
+----------+----------------------+
```
