### VAR_POP Function

```sql
VAR_POP([DISTINCT] expr) [FILTER (WHERE condition)]
```

#### Description

The `VAR_POP` function calculates the population variance of a set of numeric data. Variance is a statistical measure of data dispersion used to reflect the degree of volatility in the data. By calculating population variance, we can understand the data's volatility, allowing for deeper analysis.

#### Parameter Description

* `expr`: Numeric type, can be `TINYINT`, `SMALLINT`, `INT`, `BIGINT`, `FLOAT`, `DOUBLE`, or `DECIMAL`.
* `DISTINCT`: Optional parameter indicating the calculation of the variance of the set after deduplication. If this parameter is not set, the variance of the set including duplicate values is calculated.

#### Return Result

* The return type is `DOUBLE`.
* If all input values are `NULL`, returns `NULL`.

#### Usage Examples

1. Calculate the variance of the set including duplicate values:

```sql
SELECT VAR_POP(col) FROM VALUES (1), (2), (3), (3), (NULL) AS tab(col);
+----------------+
| `VAR_POP`(col) |
+----------------+
| 0.6875         |
+----------------+
```

2. Calculate the variance of the deduplicated set:

```sql
SELECT VAR_POP(DISTINCT col) FROM VALUES (1), (2), (3), (3), (NULL) AS tab(col);
+-------------------------+
| `VAR_POP`(DISTINCT col) |
+-------------------------+
| 0.6666666666666666      |
+-------------------------+
```

3. Use the FILTER clause to conditionally calculate the population variance:

```sql
SELECT VAR_POP(col) FILTER (WHERE col > 1) FROM VALUES (1), (2), (3), (4) AS tab(col);
+-------------------------------------------+
| `VAR_POP`(col) FILTER (WHERE (col > 1))   |
+-------------------------------------------+
| 0.6666666666666666                        |
+-------------------------------------------+
```

4. Combine the FILTER clause and DISTINCT to calculate the conditional population variance:

```sql
SELECT VAR_POP(DISTINCT col) FILTER (WHERE col <= 3) FROM VALUES (1), (2), (3), (3), (4) AS tab(col);
+--------------------------------------------------------+
| `VAR_POP`(DISTINCT col) FILTER (WHERE (col <= 3))      |
+--------------------------------------------------------+
| 0.6666666666666666                                     |
+--------------------------------------------------------+
```
