##  Description

The `PERCENT_RANK` function is used to calculate the percentile rank. It returns the relative position of a value within a set of values.

## Syntax
```SQL
PERCENT_RANK()
```
## Parameter Description

* **column**: The column used to calculate the percentile rank.

## Return Result

Returns a value between 0 and 1, indicating the relative position of the data point within the dataset.

## Example
```SQL
SELECT a, b, percent_rank(b) OVER (PARTITION BY a ORDER BY b)
    FROM VALUES ('A1', 2), ('A1', 1), ('A1', 3), ('A1', 6), ('A1', 7), ('A1', 7), ('A2', 3), ('A1', 1) tab(a, b);
+----+---+-------------------------------------------------------+
| a  | b | `percent_rank`() OVER (PARTITION BY a ORDER BY b ASC) |
+----+---+-------------------------------------------------------+
| A1 | 1 | 0.0                                                   |
| A1 | 1 | 0.0                                                   |
| A1 | 2 | 0.3333333333333333                                    |
| A1 | 3 | 0.5                                                   |
| A1 | 6 | 0.6666666666666666                                    |
| A1 | 7 | 0.8333333333333334                                    |
| A1 | 7 | 0.8333333333333334                                    |
| A2 | 3 | 0.0                                                   |
+----+---+-------------------------------------------------------+
```