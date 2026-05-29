### COVAR_SAMP Function

```
covar_samp(y, x)
```

#### Description

The `COVAR_SAMP` function computes the sample covariance between two numeric columns. Covariance measures the degree to which two variables change together. Sample covariance uses (n-1) as the denominator and is an unbiased estimator of the population covariance.

#### Parameters

* `y`: A numeric expression serving as the dependent variable. Must be a numeric type that can be cast to `DOUBLE`.
* `x`: A numeric expression serving as the independent variable. Must be a numeric type that can be cast to `DOUBLE`.

#### Return Type

* Returns a `DOUBLE` value representing the sample covariance.
  * Positive value: x and y tend to change in the same direction (positive correlation)
  * Negative value: x and y tend to change in opposite directions (negative correlation)
  * Close to 0: weak correlation between variables

#### Notes

* During computation, `NULL` values are ignored.
* If there are fewer than 1 valid data point, returns `NULL`.
* Sample covariance uses the formula with denominator (n-1) and is an unbiased estimator of the population covariance. With small sample sizes, the variability (variance) of sample covariance tends to be larger.
* When n is large, the difference between sample covariance and population covariance is negligible.

#### Examples

1. Basic usage: compute sample covariance

```sql
SELECT covar_samp(c1, c2)
FROM VALUES (1, 1), (2, 2), (2, 2), (3, 3) AS tab(c1, c2);
+--------------------+
| covar_samp(c1, c2) |
+--------------------+
| 0.6666666666666666 |
+--------------------+
```

2. Comparison with population covariance

```sql
SELECT covar_pop(c1, c2), covar_samp(c1, c2)
FROM VALUES (1, 1), (2, 2), (2, 2), (3, 3) AS tab(c1, c2);
+-------------------+--------------------+
| covar_pop(c1, c2) | covar_samp(c1, c2) |
+-------------------+--------------------+
| 0.5               | 0.6666666666666666 |
+-------------------+--------------------+
```

3. Perfect positive correlation data

```sql
SELECT covar_samp(x, y)
FROM VALUES (1, 2), (2, 4), (3, 6), (4, 8) AS t(x, y);
+--------------------+
| covar_samp(x, y)   |
+--------------------+
| 3.3333333333333335 |
+--------------------+
```

4. Perfect negative correlation data

```sql
SELECT covar_samp(x, y)
FROM VALUES (1, 8), (2, 6), (3, 4), (4, 2) AS t(x, y);
+---------------------+
| covar_samp(x, y)    |
+---------------------+
| -3.3333333333333335 |
+---------------------+
```

5. NULL values are ignored

```sql
SELECT covar_samp(x, y)
FROM VALUES (1, 1), (2, NULL), (3, 3), (NULL, 4), (5, 5) AS t(x, y);
+-------------------+
| covar_samp(x, y)  |
+-------------------+
| 4.0               |
+-------------------+
```

6. Compute sample covariance by group

```sql
SELECT
  product,
  covar_samp(price, sales_volume) as price_sales_covar
FROM VALUES
  ('A', 10, 100),
  ('A', 20, 80),
  ('A', 30, 60),
  ('B', 15, 50),
  ('B', 25, 40),
  ('B', 35, 30)
AS sales(product, price, sales_volume)
GROUP BY product;
+---------+--------------------+
| product | price_sales_covar  |
+---------+--------------------+
| A       | -200.0             |
| B       | -100.0             |
+---------+--------------------+
```
