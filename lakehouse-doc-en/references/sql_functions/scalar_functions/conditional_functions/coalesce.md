### COALESCE 

#### Description

The `COALESCE` function is used to return the first non-null expression value in its list of arguments. If all arguments are null, it returns null.

#### Syntax
```sql
COALESCE(expr1 [, ...])
```
#### Parameters

* `exprN`: The expression to be validated, with a variable number of parameters, but at least one is required. The parameter types can be different, and the return type is the same as the first non-null parameter.

#### Return Value

* Returns the value of the first non-null expression in the parameter list. If all parameters are null, it returns null.

####  Example

**Example 1: Basic Usage**
```sql
 SELECT COALESCE(null, 'A', null, 'B', 'C') as res;
+-----+
| res |
+-----+
| A   |
+-----+
```
In this example, the `COALESCE` function returns the first non-null argument `'A'`.

**Example 2: Handling multiple fields that may be null**
```sql
SELECT COALESCE(column1, column2, column3) AS non_null_value
FROM table_name;
```
Assume `column1`, `column2`, and `column3` may all contain null values. This query will return the first non-null value among these three fields.

#### Notes

* The `COALESCE` function stops checking subsequent parameters once it finds the first non-null value.
* When all parameters are null, the `COALESCE` function returns null without raising an error.
* When comparing parameter values, `NULL` is considered equal to `NULL`, but it is not considered equal to any other value, including itself. This means that even if there are two `NULL` values, `COALESCE` will not consider them equal.