### Population Standard Deviation (STDDEV_POP)

```sql
stddev_pop([DISTINCT] expr) [FILTER (WHERE condition)]
```

#### Description

The `STDDEV_POP` function calculates the population standard deviation of a set of numeric data. Standard deviation is a statistical measure of data dispersion, used to indicate the degree to which values in a dataset deviate from the mean.

#### Parameter Description

* `expr`: The numeric data for which the standard deviation needs to be calculated. Can be of type `TINYINT`, `SMALLINT`, `INT`, `BIGINT`, `FLOAT`, `DOUBLE`, or `DECIMAL`.
* `DISTINCT`: Optional parameter indicating whether to calculate the standard deviation of the distinct set. If `DISTINCT` is set, the function only calculates the standard deviation of non-duplicate data.

#### Return Result

* Returns a `DOUBLE` type value representing the calculation result.
* If all input values are `NULL`, returns `NULL`.

#### Usage Examples

**Example 1**: Calculate the population standard deviation of a set of numeric data

```sql
SELECT stddev_pop(col) FROM VALUES (1), (2), (3), (3), (NULL) AS tab(col);
+-------------------+
| `stddev_pop`(col) |
+-------------------+
| 0.82915619758885  |
+-------------------+
```

**Example 2**: Calculate the population standard deviation after deduplication

```sql
SELECT stddev_pop(DISTINCT col) FROM VALUES (1), (2), (3), (3), (NULL) AS tab(col);
+----------------------------+
| `stddev_pop`(DISTINCT col) |
+----------------------------+
| 0.816496580927726          |
+----------------------------+
```

**Example 3**: Use the FILTER clause to conditionally calculate the population standard deviation

```sql
SELECT stddev_pop(col) FILTER (WHERE col > 1) FROM VALUES (1), (2), (3), (4) AS tab(col);
+----------------------------------------------+
| `stddev_pop`(col) FILTER (WHERE (col > 1))   |
+----------------------------------------------+
| 0.816496580927726                            |
+----------------------------------------------+
```

**Example 4**: Combine FILTER clause and DISTINCT to calculate the conditional population standard deviation

```sql
SELECT stddev_pop(DISTINCT col) FILTER (WHERE col <= 3) FROM VALUES (1), (2), (3), (3), (4) AS tab(col);
+-----------------------------------------------------------+
| `stddev_pop`(DISTINCT col) FILTER (WHERE (col <= 3))      |
+-----------------------------------------------------------+
| 0.816496580927726                                         |
+-----------------------------------------------------------+
```

With the above examples, you can flexibly use the `STDDEV_POP` function to calculate the population standard deviation of a dataset according to your actual needs.
