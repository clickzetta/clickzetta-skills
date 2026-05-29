### Higher-Order Functions
Higher-order functions are those that accept one or more lambda functions as parameters. In SQL language, lambda functions are typically used to handle complex data types such as arrays and maps, as well as to perform calculations in subqueries.

#### Lambda Function Syntax
The syntax format for a lambda function is `arg -> expr` or `(arg1, arg2) -> expr`:
1. The left side of `->` is the parameter list, which can represent elements in an array or key-value pairs in a map. The specific meaning of the parameter binding depends on the semantics of the higher-order function.
2. The right side of `->` is the computation body of the lambda function, which performs calculations on the parameters. In the expression `expr`, you can reference column names from the outer query or subquery.

#### Usage Example
1. Array element processing:
``` sql
SELECT transform(array(1, 2, 3), x -> x + 1);
-- Result: [2, 3, 4]
```
In the above example, we apply the lambda function `x -> x + 1` to each element `x` in the array `[1, 2, 3]`, resulting in a new array `[2, 3, 4]`.

2. Mapping Element Processing:
``` sql
SELECT transform(map('a', 1, 'b', 2), (k, v) -> k || ' : ' || v);
-- Result: {'a' : 'a : 1', 'b' : 'b : 2'}
```
In this example, we apply the lambda function `(k, v) -> k || ' : ' || v` to each key-value pair `(k, v)` in the map `{'a' : 1, 'b' : 2}`, resulting in a new map `{'a' : 'a : 1', 'b' : 'b : 2'}`.

3. Capture external columns:
``` sql
SELECT transform(array(1, 2, 3), x -> x + a) FROM (SELECT 100 AS a) AS sub;
-- Result: [101, 102, 103]
```
In this example, we capture the value of column `a` from the subquery and add it to the elements `x` in the array `[1, 2, 3]`, resulting in a new array `[101, 102, 103]`.

#### Notes
1. The parameter list of the lambda function should match the expected parameter types and quantities of the higher-order function.
2. In the lambda function, you can reference column names from external queries or subqueries, but ensure their readability and correctness.
3. The specific usage and semantics of higher-order functions vary by function, so please read the relevant documentation carefully before use.