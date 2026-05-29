### STD Function

```
std([DISTINCT] expr)
```

#### Description

The `STD` function is an alias of `STDDEV_SAMP` and computes the sample standard deviation of a set of numeric data. Standard deviation is a statistical measure of dispersion, used to indicate how spread out the values in a dataset are.

#### Parameters

* `expr`: A numeric column or expression, which can be of type `TINYINT`, `SMALLINT`, `INT`, `BIGINT`, `FLOAT`, `DOUBLE`, or `DECIMAL`.
* `DISTINCT`: An optional parameter. When `DISTINCT` is specified, the function computes the standard deviation of the deduplicated set. If `DISTINCT` is not set, the standard deviation is computed on the set including duplicates.

#### Return Type

* Returns a `DOUBLE` value representing the sample standard deviation of the dataset.

#### Notes

* If the input dataset contains `NULL` values, they are excluded from computation.
* The `STD` function is fully identical to `STDDEV_SAMP` and the two can be used interchangeably.

#### Examples

1. Basic usage

```sql
SELECT std(col) FROM VALUES (1), (2), (3), (3), (NULL) AS tab(col);
+--------------------+
| `std`(col)         |
+--------------------+
| 0.9574271077563381 |
+--------------------+
```

2. Using the DISTINCT keyword

```sql
SELECT std(DISTINCT col) FROM VALUES (1), (2), (3), (3), (NULL) AS tab(col);
+----------------------+
| `std`(DISTINCT col)  |
+----------------------+
| 1.0                  |
+----------------------+
```

3. Using the FILTER clause to conditionally compute standard deviation

```sql
SELECT std(col) FILTER (WHERE col > 1) FROM VALUES (1), (2), (3), (4) AS tab(col);
+----------------------------------+
| std(col) FILTER (WHERE col > 1)  |
+----------------------------------+
| 1.0                              |
+----------------------------------+
```

4. Compute standard deviation by group

```sql
SELECT c, std(col)
FROM VALUES ('a', 1), ('a', 2), ('a', 3), ('b', 10), ('b', 20) AS tab(c, col)
GROUP BY c;
+---+--------------------+
| c | std(col)           |
+---+--------------------+
| a | 1.0                |
| b | 7.0710678118654755 |
+---+--------------------+
```
