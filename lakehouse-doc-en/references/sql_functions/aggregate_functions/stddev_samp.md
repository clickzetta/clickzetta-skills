### STDDEV_SAMP (Sample Standard Deviation)

```sql
stddev_samp([DISTINCT] expr) [FILTER (WHERE condition)]
```

#### Description

The `STDDEV_SAMP` function calculates the sample standard deviation of a set of numeric data. Standard deviation is a statistical measure of data dispersion, used to indicate the degree of variation in a set of values. This function can handle various numeric types including `TINYINT`, `SMALLINT`, `INT`, `BIGINT`, `FLOAT`, `DOUBLE`, and `DECIMAL`.

#### Parameter Description

* `expr`: A column or expression of numeric type, including `TINYINT`, `SMALLINT`, `INT`, `BIGINT`, `FLOAT`, `DOUBLE`, or `DECIMAL`.
* `DISTINCT`: Optional parameter. When set to `DISTINCT`, the function calculates the standard deviation of the distinct set. If `DISTINCT` is not set, the function calculates the standard deviation of the set including duplicate values.

#### Return Result

* Returns a `DOUBLE` type value representing the sample standard deviation of the dataset.
* If the input dataset contains `NULL` values, the `NULL` values will not participate in the calculation.

#### Usage Examples

**Example 1: Basic usage**

```sql
SELECT stddev_samp(col) FROM VALUES (1), (2), (3), (3), (NULL) AS tab(col);
+--------------------+
| `stddev_samp`(col) |
+--------------------+
| 0.9574271077563381 |
+--------------------+
```

**Example 2: Using the DISTINCT keyword**

```sql
SELECT stddev_samp(DISTINCT col) FROM VALUES (1), (2), (3), (3), (NULL) AS tab(col);
+-----------------------------+
| `stddev_samp`(DISTINCT col) |
+-----------------------------+
| 1                         |
+-----------------------------+
```

**Example 3: Using the FILTER clause to conditionally calculate the sample standard deviation**

```sql
SELECT stddev_samp(col) FILTER (WHERE col > 1) FROM VALUES (1), (2), (3), (4) AS tab(col);
+-----------------------------------------------+
| `stddev_samp`(col) FILTER (WHERE (col > 1))   |
+-----------------------------------------------+
| 1                                           |
+-----------------------------------------------+
```

**Example 4: Combining FILTER clause and DISTINCT to calculate the conditional sample standard deviation**

```sql
SELECT stddev_samp(DISTINCT col) FILTER (WHERE col <= 3) FROM VALUES (1), (2), (3), (3), (4) AS tab(col);
+------------------------------------------------------------+
| `stddev_samp`(DISTINCT col) FILTER (WHERE (col <= 3))      |
+------------------------------------------------------------+
| 1                                                        |
+------------------------------------------------------------+
```

With the above examples, you can better understand the usage and application scenarios of the `STDDEV_SAMP` function. In actual data analysis, this function can help you quickly assess the dispersion of data, thereby providing a basis for decision-making.
