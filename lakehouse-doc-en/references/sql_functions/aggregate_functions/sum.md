### SUM Function

```sql
sum([DISTINCT] expr) [FILTER (WHERE condition)]
```

#### Description

The `SUM` function calculates and returns the total sum of a set of numeric data. If the `DISTINCT` keyword is specified, the sum of the distinct set of values is calculated.

#### Parameter Description

* `expr`: The numeric type field to be summed, which can be of type `TINYINT`, `SMALLINT`, `INT`, `BIGINT`, `FLOAT`, `DOUBLE`, or `DECIMAL`.

#### Return Type

* For `DECIMAL` type data, a `DECIMAL` type result is returned. In other cases, a `DOUBLE` type result is returned.
* When the `DISTINCT` keyword is specified, the sum of the distinct set of values is returned.
* If the expression contains `NULL` values, the `NULL` values will not participate in the calculation.

#### Usage Examples

1. Calculate the total sum of all values:

```sql
SELECT sum(col) FROM VALUES (5), (10), (10), (15), (NULL) AS tab(col);
+------------+
| `sum`(col) |
+------------+
| 40         |
+------------+
```

2. Calculate the sum of the deduplicated set of values:

```sql
SELECT sum(DISTINCT col) FROM VALUES (5), (10), (10), (15), (NULL) AS tab(col);
+---------------------+
| `sum`(DISTINCT col) |
+---------------------+
| 30                  |
+---------------------+
```

3. Use the FILTER clause to conditionally calculate the sum:

```sql
SELECT sum(col) FILTER (WHERE col > 10) FROM VALUES (5), (10), (15), (20) AS tab(col);
+---------------------------------------+
| `sum`(col) FILTER (WHERE (col > 10))  |
+---------------------------------------+
| 35                                    |
+---------------------------------------+
```

4. Combine the FILTER clause and DISTINCT to calculate the deduplicated conditional sum:

```sql
SELECT sum(DISTINCT col) FILTER (WHERE col >= 10) FROM VALUES (5), (10), (10), (15), (20) AS tab(col);
+------------------------------------------------------+
| `sum`(DISTINCT col) FILTER (WHERE (col >= 10))       |
+------------------------------------------------------+
| 45                                                   |
+------------------------------------------------------+
```

With the above examples, you can better understand the usage and application scenarios of the `SUM` function. Please adjust the parameters and expressions according to your actual needs.
