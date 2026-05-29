### ARRAY_SORT_REVERSE

####  Description
The `ARRAY_SORT_REVERSE` function is used to sort the input array in descending order. This function accepts an array as a parameter and returns a new array with elements sorted from largest to smallest.

#### Parameter Description
- `array`: Input parameter, type `array<T>`, representing the array to be sorted.

#### Return Result
Returns a new array of type `array<T>`, with elements sorted in descending order.

#### Usage Example
1. Sort an integer array in descending order:
```sql
SELECT array_sort_reverse(array(2, 1, 3));
-- Result: [3, 2, 1]
```
2. Sort the floating-point number array in descending order:
```sql
SELECT array_sort_reverse(array(1.5, 3.2, 2.8));
-- Result: [3.2, 2.8, 1.5]
```
3. Sort the array of strings in descending order according to the dictionary order of the strings:
```sql
SELECT array_sort_reverse(array('banana', 'apple', 'cherry'));
-- Result: ['cherry', 'banana', 'apple']
```
#### Precautions
- The element types in the input array must be consistent.
- This function is sensitive to `NULL` values in the array, and `NULL` values will be placed at the end of the returned array.