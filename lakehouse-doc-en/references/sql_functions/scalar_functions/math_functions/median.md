####  Description

The `median` function is used to calculate the median of a set of values. The median is the number that is in the middle of a set of values when they are arranged in order. If the set has an even number of values, the median is the average of the two middle numbers. The `median` function automatically ignores `NULL` values.

#### Syntax
```Plain
median(col)
```
#### Parameters

* `col`: The column for which the median needs to be calculated.

#### Return Results

* Returns the median of the specified column.

#### Usage Example
```SQL
SELECT median(col) FROM VALUES (1), (2), (2), (3), (4), (NULL) AS tab(col);
```
In this example, the `median` function calculates the median of a set of values provided by the `VALUES` clause. Since `NULL` values are ignored, the actual values involved in the calculation are `1, 2, 2, 3, 4`. These values are ordered as `1, 2, 2, 3, 4`, and the middle values are `2` and `3`, so the returned median is the average of these two numbers, which is `2.5`.