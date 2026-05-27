### AVG Function

```
avg([DISTINCT] expr) [FILTER (WHERE condition)]
```

#### Description

The `AVG` function calculates the arithmetic mean of a specified expression across a set of data. When the `DISTINCT` keyword is specified, the average is calculated on deduplicated values.

#### Parameters

* `expr`: A numeric expression of type `TINYINT`, `SMALLINT`, `INT`, `BIGINT`, `FLOAT`, `DOUBLE`, or `DECIMAL`.

#### Return Type

* For `DECIMAL` type expressions, the `AVG` function returns a `DECIMAL` type result. The return value's precision and scale may increase to accommodate the calculation result.
* For other numeric type expressions, the `AVG` function returns a `DOUBLE` type result.

#### Notes

* During calculation, `NULL` values are ignored and do not participate in the average calculation.

#### Examples

1. Calculate the average of a numeric column (excluding `NULL` values):

```sql
SELECT avg(col) FROM VALUES (1), (2), (3), (4), (NULL) AS tab(col);
+------------+
| `avg`(col) |
+------------+
| 2.5        |
+------------+
```

2. Calculate the average of a numeric column with deduplication:

```sql
SELECT avg(DISTINCT col) FROM VALUES (1), (1), (2), (3), (4), (NULL) AS tab(col);
+---------------------+
| `avg`(DISTINCT col) |
+---------------------+
| 2.5                 |
+---------------------+
```

3. Use the FILTER clause for conditional average calculation:

```sql
SELECT avg(col) FILTER (WHERE col > 2) FROM VALUES (1), (2), (3), (4), (NULL) AS tab(col);
+---------------------------------------+
| `avg`(col) FILTER (WHERE (col > 2))   |
+---------------------------------------+
| 3.5                                   |
+---------------------------------------+
```

4. Combine FILTER clause and DISTINCT for deduplicated conditional average:

```sql
SELECT avg(DISTINCT col) FILTER (WHERE col <= 3) FROM VALUES (1), (1), (2), (3), (4) AS tab(col);
+------------------------------------------------------+
| `avg`(DISTINCT col) FILTER (WHERE (col <= 3))        |
+------------------------------------------------------+
| 2.0                                                  |
+------------------------------------------------------+
```
