### FORALL 

#### Description
The FORALL function is used to determine whether all elements in an array meet a specified condition. This function takes an array and a single-parameter lambda expression as input and returns a boolean result.

#### Syntax
``` sql
FORALL(array, x -> expr)
```
#### Parameter Description
- `array`: The input array, of type `array<T>`.
- `x -> expr`: A single-parameter lambda expression, where `x` corresponds to an element in the array, and `expr` is an expression that needs to return a boolean value.

#### Return Result
- Returns a boolean value indicating whether all elements in the array satisfy the condition specified by the lambda expression.

####  Example

1. Determine if all elements in the array are less than or equal to 3:
   ``` sql
   SELECT FORALL(array(1, 2, 3, 4, 5), x -> x <= 3) AS result;
   ```
Result: 
   ```
   result
   -------
   false
   ```
2. Determine if all elements in the array are greater than 10:
   ``` sql
   SELECT FORALL(array(1, 20, 30, 4), x -> x > 10) AS result;
   ```
Result: 
   ```
   result
   -------
   false
   ```
3. Determine if all non-null elements in an array containing null values are less than or equal to 3:
   ``` sql
   SELECT FORALL(array(1, null, 3), x -> IF(x IS NOT NULL, x <= 3, true)) AS result;
   ```
Result: 
   ```
   result
   -------
   true
   ```
4. Determine if all even elements in the array are greater than or equal to 2:
   ``` sql
   SELECT FORALL(array(1, 2, 3, 4, 6), x -> MOD(x, 2) = 0 AND x >= 2) AS result;
   ```
Result: 
   ```
   result
   -------
   false
   ```
#### Notes
- When the array is empty, the FORALL function will return a `NULL` value.
- When the condition in the lambda expression is not satisfied by all elements, the function returns `false`.
- When the condition in the lambda expression is satisfied by all elements, the function returns `true`.