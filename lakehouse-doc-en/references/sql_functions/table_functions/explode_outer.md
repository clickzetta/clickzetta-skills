### EXPLODE_OUTER Function

#### Description

The `EXPLODE_OUTER` function is used to expand array or map type expressions into multiple rows. Unlike `EXPLODE`, when the input is NULL or an empty array/empty map, `EXPLODE_OUTER` retains the original row and outputs NULL values, whereas `EXPLODE` directly discards that row.

This function can be used directly or in combination with `LATERAL VIEW`.

#### Syntax

```sql
EXPLODE_OUTER(expr)
```

#### Parameters

* `expr`: The input array (`ARRAY<T>`) or map (`MAP<K, V>`) expression.

#### Return Results

* For array type input, each element in the returned result has the type `T`.
* For map type input, the returned result contains two columns, representing the key (`key`) and value (`value`), with types `K` and `V` respectively.
* When the input is NULL or an empty array/empty map, outputs one row of NULL values.

#### Examples

1. Expand an array, including NULL input cases:

    ```sql
    SELECT id, col
    FROM VALUES (1, array(10, 20)), (2, NULL), (3, array()) AS t(id, arr)
    LATERAL VIEW EXPLODE_OUTER(arr) lv AS col;
    +----+------+
    | id | col  |
    +----+------+
    | 1  | 10   |
    | 1  | 20   |
    | 2  | NULL |
    | 3  | NULL |
    +----+------+
    ```

2. Comparison with `EXPLODE` (discards NULL and empty array rows):

    ```sql
    -- When using EXPLODE: NULL and empty array rows are discarded
    SELECT id, col
    FROM VALUES (1, array(10, 20)), (2, NULL), (3, array()) AS t(id, arr)
    LATERAL VIEW EXPLODE(arr) lv AS col;
    +----+-----+
    | id | col |
    +----+-----+
    | 1  | 10  |
    | 1  | 20  |
    +----+-----+
    ```

3. Expand a map type, including NULL input:

    ```sql
    SELECT id, key, value
    FROM VALUES (1, map('a', 1, 'b', 2)), (2, NULL) AS t(id, m)
    LATERAL VIEW EXPLODE_OUTER(m) lv AS key, value;
    +----+------+-------+
    | id | key  | value |
    +----+------+-------+
    | 1  | a    | 1     |
    | 1  | b    | 2     |
    | 2  | NULL | NULL  |
    +----+------+-------+
    ```

#### Notes

* When the input is NULL, `EXPLODE_OUTER` retains the original row and outputs NULL, whereas `EXPLODE` discards that row.
* When the input is an empty array `array()` or empty map `map()`, the behavior is the same as NULL: retains the original row and outputs NULL.
* `EXPLODE_OUTER` is commonly used in LEFT JOIN semantic scenarios, ensuring that the main table rows are not lost even if the array/map is empty or NULL.
* This function can be used directly in SELECT or in combination with `LATERAL VIEW`.
