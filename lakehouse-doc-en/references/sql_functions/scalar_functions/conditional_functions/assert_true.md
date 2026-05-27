### ASSERT_TRUE Function

```sql
assert_true(expr)
assert_true(expr, message)
```

#### Description

The `ASSERT_TRUE` function validates whether a boolean expression is true. If the expression is `true`, it returns `NULL`; if the expression is `false` or `NULL`, it throws an exception. The optional `message` parameter allows a custom error message.

This function is commonly used for data quality checks, unit testing, and runtime assertion validation.

#### Parameters

* `expr`: A boolean expression, required. The condition to validate.
* `message`: A string value, optional. A custom error message displayed when the assertion fails. If not specified or `NULL`, the default error message `"ASSERT_TRUE expr is not true!"` is used.

#### Returns

* When `expr` is `true`: Returns `NULL`.
* When `expr` is `false` or `NULL`: Throws an exception with the error message.

#### Examples

1. Basic usage - assertion succeeds, returns NULL:

    ```sql
    SELECT assert_true(1 = 1);
    +---------------------+
    | assert_true(1 = 1)  |
    +---------------------+
    | NULL                |
    +---------------------+
    ```

2. Using a custom error message - assertion succeeds:

    ```sql
    SELECT assert_true(10 > 5, 'Ten is greater than five');
    +--------------------------------------------------+
    | assert_true(10 > 5, 'Ten is greater than five')  |
    +--------------------------------------------------+
    | NULL                                             |
    +--------------------------------------------------+
    ```

3. Assertion fails - throws default error message:

    ```sql
    SELECT assert_true(1 > 2);
    -- Error: ASSERT_TRUE expr is not true!
    ```

4. Assertion fails - throws custom error message:

    ```sql
    SELECT assert_true(1 > 2, 'One should be greater than two');
    -- Error: One should be greater than two
    ```

5. Input is NULL - treated as assertion failure:

    ```sql
    SELECT assert_true(NULL);
    -- Error: ASSERT_TRUE expr is not true!
    ```

#### Notes

* When `expr` is `NULL`, it is treated as an assertion failure and throws an exception (rather than returning NULL).
* When `message` is `NULL`, the default error message `"ASSERT_TRUE expr is not true!"` is used.
* This function is compatible with Spark's `assert_true` semantics.
* This function is not subject to constant folding optimization, ensuring that assertion checks are always executed at runtime.
