### ARRAY_SORT

####  Description
The `ARRAY_SORT` function is used to sort the input array. This function sorts the elements in the array in natural order and places all `null` values at the end of the array.

####  Syntax
```
ARRAY_SORT(array: array<T>);
```
#### Parameter Description
- `array`: The input array, which can be of any type, including but not limited to integers, floats, strings, etc.

#### Return Result
Returns a new, sorted array. The elements in the array will be arranged in ascending order, with all `null` values moved to the end of the array.

#### Usage Example
1. Sort an array of integers:
```sql
SELECT ARRAY_SORT(array(2, 1, 3));
// Result: [1, 2, 3]
```
2. Sort an array containing `null` values:
```sql
SELECT ARRAY_SORT(array(null, 4, 3, null, 5, 6));
// Result: [3, 4, 5, 6, null, null]
```
3. Sort the string array:
```sql
SELECT ARRAY_SORT(array('banana', 'apple', 'cherry'));
// Result: ['apple', 'banana', 'cherry']
```
4. Sorting an array of floating-point numbers:
```sql
SELECT ARRAY_SORT(array(3.14, 2.71, 1.41));
// Result: [1.41, 2.71, 3.14]
```
5. Sorting an array of mixed types:
```sql
SELECT ARRAY_SORT(array('2019', 2, null, '2020', 1));
// Result: [1, 2, '2019', '2020', null]
```
#### Notes
- When the array contains elements of non-comparable types, it may lead to unexpected sorting results.
- If the element types in the array are inconsistent, the sorting operation may follow implicit type conversion rules, which could affect the accuracy of the sorting results.