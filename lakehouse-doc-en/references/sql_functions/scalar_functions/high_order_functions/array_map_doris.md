### array_map_doris
#### Description
Applies a lambda expression to each element in an array, returning a new array. The function applies the lambda expression to every element in the array, returning the corresponding result.

#### Syntax
```sql
array_map_doris(lambda, ARRAY<T> arr1, [ARRAY<T> arr2, ...])
```
#### Parameters
* `lambda`: A lambda expression defining the transformation rule
* `arr1, arr2, ...`: ARRAY type, the arrays to transform. Supports one or more array parameters.

#### Returns
Return type: ARRAY

Return value semantics:

* Returns a new array of the same length as the input array, where each position holds the result of applying the lambda expression to the corresponding element
* NULL: if the input array is NULL

Usage notes:

* The number of parameters in the lambda expression must match the number of array parameters
* When multiple array parameters are provided, all arrays must have the same length
* Lambda can use any scalar expression but not aggregate functions
* Lambda expressions can call other higher-order functions, but the return types must be compatible
* For null values in array elements: null elements are passed to the lambda expression for processing; the lambda can evaluate null values

#### Examples
* Square each element in the array:
```sql
SELECT array_map_doris(x -> x * x, [1, 2, 3, 4, 5]);
```
![](/.topwrite/assets/image_1775631464162.png)
* Round each element in a floating-point array:
```sql
SELECT array_map_doris(x -> round(x), [1.1, 2.7, 3.3, 4.9, 5.5]);
```
![](/.topwrite/assets/image_1775631537666.png)
