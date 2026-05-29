#### Description

The `multiIf` function is a conditional logic function that allows you to write `CASE` statement-like logic more compactly in queries. This function evaluates multiple conditions in the specified order and returns the value corresponding to the first true condition. If none of the conditions are met, it returns the value of the last `else` expression.

#### Syntax
```Plain
multiIf(cond_1, then_1, cond_2, then_2, ..., else)
```
#### Parameters

* `cond_N`: The N-th condition to be evaluated.
* `then_N`: The value returned when the N-th condition is true.
* `else`: The value returned if none of the conditions are met.

#### Return Value

* Returns the value of any `then_N` expression, or the value of the `else` expression if none of the conditions are met.

#### Example Usage
```SQL

SELECT    name,
          score,
          multiIf (
          score >= 90,
          'A',
          score >= 80,
          'B',
          score >= 70,
          'C',
          score >= 60,
          'D'        
          ) AS grade
FROM     
VALUES    ('Alice', 92),('Bob', 85),('Charlie', 77),('David', 63),('Eve', 58) students (name, score);
+---------+-------+-------+
|  name   | score | grade |
+---------+-------+-------+
| Alice   | 92    | A     |
| Bob     | 85    | B     |
| Charlie | 77    | C     |
| David   | 63    | D     |
| Eve     | 58    |       |
+---------+-------+-------+
```
#### Notes

* If the `multiIf` function does not include the `else` part, the function will return `NULL` when all conditions are not met.