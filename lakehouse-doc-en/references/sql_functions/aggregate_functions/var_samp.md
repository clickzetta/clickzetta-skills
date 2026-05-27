### VAR_SAMP Function

```sql
var_samp([DISTINCT] expr) [FILTER (WHERE condition)]
```

#### Description

The `VAR_SAMP` function calculates the sample variance of a set of numeric data. Variance is a statistical measure of data dispersion that reflects the magnitude of data volatility. By calculating variance, we can understand the range and trends of data fluctuations.

#### Parameter Description

* `expr`: Numeric type, can be `TINYINT`, `SMALLINT`, `INT`, `BIGINT`, `FLOAT`, `DOUBLE`, or `DECIMAL`.
* `DISTINCT` (optional): Indicates the calculation of the variance of the set after deduplication. If this parameter is not set, the variance of the set including duplicate values is calculated.

#### Return Result

* Returns a `DOUBLE` type value representing the calculated sample variance.
* If the input parameters contain `NULL` values, the `NULL` values are not included in the calculation.

#### Usage Examples

1. Calculate the sample variance including duplicate values:

```sql
SELECT var_samp(col) FROM VALUES (1), (2), (3), (3), (NULL) AS tab(col);
+--------------------+
|  `var_samp`(col)   |
+--------------------+
| 0.9166666666666666 |
+--------------------+
```

2. Calculate the sample variance after deduplication:

```sql
SELECT var_samp(DISTINCT col) FROM VALUES (1), (2), (3), (3), (NULL) AS tab(col);
+--------------------------+
| `var_samp`(DISTINCT col) |
+--------------------------+
| 1                      |
+--------------------------+
```

3. Use the FILTER clause to conditionally calculate the sample variance:

```sql
SELECT var_samp(col) FILTER (WHERE col > 1) FROM VALUES (1), (2), (3), (4) AS tab(col);
+--------------------------------------------+
| `var_samp`(col) FILTER (WHERE (col > 1))   |
+--------------------------------------------+
| 1                                        |
+--------------------------------------------+
```

4. Combine the FILTER clause and DISTINCT to calculate the conditional sample variance:

```sql
SELECT var_samp(DISTINCT col) FILTER (WHERE col <= 3) FROM VALUES (1), (2), (3), (3), (4) AS tab(col);
+-------------------------------------------------------+
| `var_samp`(DISTINCT col) FILTER (WHERE (col <= 3))    |
+-------------------------------------------------------+
| 1                                                   |
+-------------------------------------------------------+
```
