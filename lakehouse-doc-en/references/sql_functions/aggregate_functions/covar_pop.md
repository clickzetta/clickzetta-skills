### COVAR_POP Function

```
covar_pop(y, x)
```

#### Description

The `COVAR_POP` function computes the population covariance between two numeric columns. Covariance measures the degree to which two variables change together, and is a statistical measure of variable correlation.

#### Parameters

* `y`: A numeric expression serving as the dependent variable. Must be a numeric type that can be cast to `DOUBLE`.
* `x`: A numeric expression serving as the independent variable. Must be a numeric type that can be cast to `DOUBLE`.

#### Return Type

* Returns a `DOUBLE` value representing the population covariance.
  * Positive value: x and y tend to change in the same direction (positive correlation)
  * Negative value: x and y tend to change in opposite directions (negative correlation)
  * Close to 0: weak correlation between variables

#### Notes

* During computation, `NULL` values are ignored.
* If there are fewer than 1 valid data point, returns `NULL`.
* Population covariance uses the formula with denominator n, whereas sample covariance uses (n-1), so population covariance is typically smaller than sample covariance.

#### Examples

1. Basic usage: compute population covariance

```sql
SELECT covar_pop(c1, c2)
FROM VALUES (1, 1), (2, 2), (2, 2), (3, 3) AS tab(c1, c2);
+-------------------+
| covar_pop(c1, c2) |
+-------------------+
| 0.5               |
+-------------------+
```

2. Comparison with sample covariance

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
SELECT covar_pop(x, y)
FROM VALUES (1, 2), (2, 4), (3, 6), (4, 8) AS t(x, y);
+------------------+
| covar_pop(x, y)  |
+------------------+
| 2.5              |
+------------------+
```

4. Perfect negative correlation data

```sql
SELECT covar_pop(x, y)
FROM VALUES (1, 8), (2, 6), (3, 4), (4, 2) AS t(x, y);
+------------------+
| covar_pop(x, y)  |
+------------------+
| -2.5             |
+------------------+
```

5. Uncorrelated data

```sql
SELECT covar_pop(x, y)
FROM VALUES (1, 5), (2, 5), (3, 5), (4, 5) AS t(x, y);
+------------------+
| covar_pop(x, y)  |
+------------------+
| 0.0              |
+------------------+
```
