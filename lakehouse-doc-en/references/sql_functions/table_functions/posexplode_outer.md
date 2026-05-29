### POSEXPLODE_OUTER Function

#### Description

The `POSEXPLODE_OUTER` function is used to expand array or map type expressions into multiple rows and adds a position column for each row. Unlike `POSEXPLODE`, when the input is NULL or an empty array/empty map, `POSEXPLODE_OUTER` retains the original row and outputs NULL values, whereas `POSEXPLODE` directly discards that row.

This function can be used directly or in combination with `LATERAL VIEW`.

#### Syntax

```sql
POSEXPLODE_OUTER(expr)
```

#### Parameters

* `expr`: The input array (`ARRAY<T>`) or map (`MAP<K, V>`) expression.

#### Return Results

* For array type input, returns two columns: `pos` (INT) and `col` (T).
* For map type input, returns three columns: `pos` (INT), `key` (K), and `value` (V).
* When the input is NULL or an empty array/empty map, outputs one row with all columns being NULL.

#### Examples

1. Expand an array, including NULL input cases:

    ```sql
    SELECT id, pos, col
    FROM VALUES (1, array(10, 20)), (2, NULL), (3, array()) AS t(id, arr)
    LATERAL VIEW POSEXPLODE_OUTER(arr) lv AS pos, col;
    +----+------+------+
    | id | pos  | col  |
    +----+------+------+
    | 1  | 0    | 10   |
    | 1  | 1    | 20   |
    | 2  | NULL | NULL |
    | 3  | NULL | NULL |
    +----+------+------+
    ```

2. Comparison with `POSEXPLODE` (discards NULL and empty array rows):

    ```sql
    -- When using POSEXPLODE: NULL and empty array rows are discarded
    SELECT id, pos, col
    FROM VALUES (1, array(10, 20)), (2, NULL), (3, array()) AS t(id, arr)
    LATERAL VIEW POSEXPLODE(arr) lv AS pos, col;
    +----+-----+-----+
    | id | pos | col |
    +----+-----+-----+
    | 1  | 0   | 10  |
    | 1  | 1   | 20  |
    +----+-----+-----+
    ```

3. Expand a map type, including NULL input:

    ```sql
    SELECT id, pos, key, value
    FROM VALUES (1, map('a', 1, 'b', 2)), (2, NULL) AS t(id, m)
    LATERAL VIEW POSEXPLODE_OUTER(m) lv AS pos, key, value;
    +----+------+------+-------+
    | id | pos  | key  | value |
    +----+------+------+-------+
    | 1  | 0    | a    | 1     |
    | 1  | 1    | b    | 2     |
    | 2  | NULL | NULL | NULL  |
    +----+------+------+-------+
    ```

#### Notes

* When the input is NULL, `POSEXPLODE_OUTER` retains the original row and outputs NULL (including the pos column), whereas `POSEXPLODE` discards that row.
* When the input is an empty array `array()` or empty map `map()`, the behavior is the same as NULL: retains the original row and outputs NULL.
* `POSEXPLODE_OUTER` is commonly used in LEFT JOIN semantic scenarios, ensuring that the main table rows are not lost even if the array/map is empty or NULL.
* This function can be used directly in SELECT or in combination with `LATERAL VIEW`.
