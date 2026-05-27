### ARRAY_AGGREGATE Function

#### Overview

ARRAY_AGGREGATE is a higher-order array aggregation function, similar to the `reduce` / `fold` operation in functional programming. It receives an array, an initial value, and a merge lambda expression. Starting from the initial value, it sequentially merges each element of the array with the accumulator using the merge lambda, ultimately returning the aggregated result.

#### Syntax

```
array_aggregate(array, initial_value, merge_lambda)
```

#### Parameters

* `array`: The input array, of type `ARRAY<E>`, where E can be any data type.
* `initial_value`: The initial value for aggregation (initial accumulator state), of type `R`, which can be any data type.
* `merge_lambda`: The merge lambda expression, in the format `(acc, x) -> expr`, where `acc` is the current accumulator value (type `R`), `x` is the current element in the array (type `E`), and `expr` is the new accumulator value (type `R`).

#### Returns

The return type matches the type of `initial_value` (type `R`), i.e., the return type of the merge lambda expression.

#### Examples

1. Compute the sum of array elements:

    ```sql
    SELECT array_aggregate(array(1, 2, 3), 0, (acc, x) -> acc + x);
    -- Result: 6
    ```

2. Merge nested arrays into a single deduplicated array:

    ```sql
    SELECT array_aggregate(a, array(date '1999-01-01'), (acc, x) -> array_union(acc, x))
    FROM VALUES
    (array(array(date '2020-10-10', date '2020-10-10'), array(date '2011-11-11'))),
    (array(array(date '2020-11-11')))
    AS t(a);
    -- Result:
    -- [1999-01-01,2020-10-10,2011-11-11]
    -- [1999-01-01,2020-11-11]
    ```

3. Count the total number of distinct elements across nested arrays:

    ```sql
    SELECT array_aggregate(a, 0, (acc, x) -> acc + array_size(array_distinct(x)))
    FROM VALUES
    (array(array(date '2020-10-10', date '2020-10-10'), array(date '2011-11-11'))),
    (array(array(date '2020-11-11')))
    AS t(a);
    -- Result:
    -- 2
    -- 1
    ```

4. Use a boolean accumulator to check if all array elements satisfy a condition:

    ```sql
    SELECT array_aggregate(a, true,
      (acc, x) -> acc AND (x > date '1990-01-01') AND (year(x) % 2 == 0)
    )
    FROM VALUES
    (array(date '2020-10-10', date '1998-01-01'))
    AS t(a);
    -- Result: true
    ```

5. When array elements contain uncastable values, NULL propagates through the lambda:

    ```sql
    SELECT array_aggregate(a, 0L,
      (acc, x) -> acc + coalesce(cast(x AS BIGINT), NULL)
    )
    FROM VALUES
    (array('123', 'abc', '456'))
    AS t(a);
    -- Result: NULL
    ```

#### Notes

* Before using the ARRAY_AGGREGATE function, JIT code generation must be enabled: `SET cz.sql.codegen.enable = TRUE;`.
* When the input array is NULL, the result is NULL.
* When the array is empty, the initial value `initial_value` is returned.
* If the merge lambda produces a NULL value, NULL will continue to participate in subsequent iterations, potentially causing the final result to be NULL. It is recommended to use functions like `COALESCE` in the lambda to handle NULL values.
* The type of the initial value determines the type of the accumulator and the final return value. Ensure the return type of the merge lambda is compatible with the initial value type.
