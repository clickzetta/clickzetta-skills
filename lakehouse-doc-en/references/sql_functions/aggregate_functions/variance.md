### VARIANCE Function

```
variance([DISTINCT] expr)
```

#### Description

The `VARIANCE` function is an alias of `VAR_SAMP` and computes the sample variance of a set of numeric data. Variance is a statistical measure of data dispersion, reflecting the degree of variability in the data.

#### Parameters

* `expr`: A numeric type, which can be `TINYINT`, `SMALLINT`, `INT`, `BIGINT`, `FLOAT`, `DOUBLE`, or `DECIMAL`.
* `DISTINCT` (optional): specifies that the variance should be computed on the deduplicated set. If this parameter is not set, the variance is computed on the set including duplicates.

#### Return Type

* Returns a `DOUBLE` value representing the computed sample variance.

#### Notes

* If the input contains `NULL` values, they are excluded from computation.
* The `VARIANCE` function is fully identical to `VAR_SAMP` and the two can be used interchangeably.

#### Examples

1. Compute the sample variance including duplicates

```sql
SELECT variance(col) FROM VALUES (1), (2), (3), (3), (NULL) AS tab(col);
+--------------------+
| `variance`(col)    |
+--------------------+
| 0.9166666666666666 |
+--------------------+
```

2. Compute the sample variance on deduplicated values

```sql
SELECT variance(DISTINCT col) FROM VALUES (1), (2), (3), (3), (NULL) AS tab(col);
+--------------------------+
| `variance`(DISTINCT col) |
+--------------------------+
| 1.0                      |
+--------------------------+
```

3. Use FILTER clause to conditionally compute variance

```sql
SELECT variance(col) FILTER (WHERE col > 1) FROM VALUES (1), (2), (3), (4) AS tab(col);
+--------------------------------------+
| variance(col) FILTER (WHERE col > 1) |
+--------------------------------------+
| 1.0                                  |
+--------------------------------------+
```

4. Compute variance by group

```sql
SELECT c, variance(col)
FROM VALUES ('a', 1), ('a', 2), ('a', 3), ('b', 10), ('b', 20) AS tab(c, col)
GROUP BY c;
+---+--------------------+
| c | variance(col)      |
+---+--------------------+
| a | 1.0                |
| b | 50.0               |
+---+--------------------+
```
