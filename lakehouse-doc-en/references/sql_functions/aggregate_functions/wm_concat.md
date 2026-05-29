### WM\_CONCAT

#### Overview

The `WM_CONCAT` function is used to concatenate a column of values with a specified delimiter. This function can handle string type data and can choose to either remove duplicates or retain all values during concatenation.

#### Syntax
```
wm_concat([distinct] separator, col)
```
#### Parameter Description

* `separator`: A string constant used as a delimiter for concatenated values.
* `col`: A string representing the column to be concatenated.

#### Return Result

Returns a string value containing the concatenated result. If the `distinct` keyword is set, the calculation will be performed on the deduplicated set; otherwise, all values will be retained. `null` values are not included in the calculation.

####  Example

1. Concatenation using &&
```
SELECT wm_concat('&&', col) FROM VALUES ('row1'), (null), ('row3') AS t(col);
+----------------------+
| wm_concat('&&', col) |
+----------------------+
| row1&&row3           |
+----------------------+
```
2. Connections with Separators:
```
SELECT wm_concat(',', col) FROM VALUES (1), (null), (3) AS t(col);
+---------------------+
| wm_concat(',', col) |
+---------------------+
| 1,3                 |
+---------------------+
```
3. Deduplicate Connections and Group:

```
SELECT k, wm_concat(DISTINCT '|', v)
  FROM VALUES
      (1, 'ALLEN'),
      (1,  null),
      (1, 'ALLEN'),
      (2, 'KING'),
      (2, 'ALEX') AS t(k, v) GROUP BY k;
+---+----------------------------+
| k | wm_concat(DISTINCT '|', v) |
+---+----------------------------+
| 1 | ALLEN                      |
| 2 | KING|ALEX                  |
+---+----------------------------+
```

4. Handling spaces and special characters when connecting:

```
SELECT wm_concat(' - ', col) FROM VALUES ('John Doe'), ('Jane Smith'), (null), ('Alice Jones') AS t(col);
+-------------------------------------+
|        wm_concat(' - ', col)        |
+-------------------------------------+
| John Doe - Jane Smith - Alice Jones |
+-------------------------------------+
```
#### Notes

* When the values in the `col` column are `null`, the `WM_CONCAT` function will not include them in the result.
* If the columns to be concatenated contain spaces or special characters, make sure to use appropriate delimiters to avoid ambiguity.
* Using the `distinct` keyword can effectively remove duplicate string values, but be aware that this may affect performance. Use this option with caution when handling large amounts of data.