### array_filter_doris
#### Description
Filters array elements based on a condition, returning a new array composed of elements that satisfy the condition. The function supports two calling modes: a higher-order function form using a lambda expression, and a direct filtering form using a boolean array.

#### Syntax
```sql
array_filter_doris(lambda, array1, ...)
array_filter_doris(array1, array<boolean> filter_array)
```
#### Parameters
* `lambda`: A lambda expression used to evaluate array elements, returning true/false or an expression convertible to a boolean value
* `array1, ...`: One or more ARRAY<T> type parameters
* `filter_array`: ARRAY<BOOLEAN> type, a boolean array used for filtering

#### Returns
Return type: ARRAY<T>

Return value semantics:

* Returns a new array composed of all elements that satisfy the filter condition
* NULL: if the input array is NULL
* Empty array: if no elements satisfy the condition

Usage notes:

* Lambda form: The number of lambda expression parameters must match the number of array parameters
* Boolean array form: The lengths of `array1` and `filter_array` should ideally be identical. If the boolean array is longer, extra boolean values are ignored; if the boolean array is shorter, only elements at corresponding positions in the boolean array are processed
* Supports filtering on multiple arrays and complex-type arrays
* Empty arrays return an empty array, NULL arrays return NULL
* Lambda can use any scalar expression but not aggregate functions
* For null values in array elements: null elements are passed to the lambda expression for processing; the lambda can evaluate null values

#### Examples
```sql
CREATE TABLE array_filter_test (
    id INT,
    int_array ARRAY<INT>,
    double_array ARRAY<DOUBLE>,
    string_array ARRAY<STRING>
);

INSERT INTO array_filter_test VALUES
(1, [1, 2, 3, 4, 5], [1.1, 2.2, 3.3, 4.4, 5.5], ['a', 'bb', 'ccc', 'dddd', 'eeeee']),
(2, [10, 20, 30], [10.5, 20.5, 30.5], ['x', 'yy', 'zzz']),
(3, [], [], []),
(4, NULL, NULL, NULL);
```
* Filter elements in double_array greater than or equal to 3 using a lambda expression:
```sql
SELECT array_filter_doris(x -> x >= 3, double_array) FROM array_filter_test WHERE id = 1;
```
![](/.topwrite/assets/image_1775630159834.png)
* Filter elements in string_array with length greater than 2 using a lambda expression:
```sql
SELECT array_filter_doris(x -> length(x) > 2, string_array) FROM array_filter_test WHERE id = 1;
```
![](/.topwrite/assets/image_1775630265289.png)
* Empty array returns an empty array:
```sql
SELECT array_filter_doris(x -> x > 0, int_array) FROM array_filter_test WHERE id = 3;
```
![](/.topwrite/assets/image_1775630549279.png)
* NULL array returns NULL: when the input array is NULL, NULL is returned without throwing an error
```sql
SELECT array_filter_doris(x -> x > 0, int_array) FROM array_filter_test WHERE id = 4;
```
![](/.topwrite/assets/image_1775630649836.png)
* Array containing nulls, lambda can evaluate null:
```sql
 select array_filter_doris(x -> x is not null, [null, 1, null, 2, null]);
```
![](/.topwrite/assets/image_1775630740260.png)

* Nested array filtering, filtering sub-arrays with length greater than 2:
```sql
SELECT array_filter_doris(x -> size(x) > 2, [[1,2], [3,4,5], [6], [7,8,9,10]]);
```
![](/.topwrite/assets/image_1775630892764.png)
