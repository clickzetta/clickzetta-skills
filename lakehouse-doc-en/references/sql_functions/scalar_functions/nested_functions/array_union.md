### ARRAY_UNION
```
array_union(array1, array2)
```
####  Description
The ARRAY_UNION function is used to compute the union of two arrays, i.e., it merges all elements from array1 and array2 and removes duplicates. This function can handle arrays containing any data type, including integers, floats, strings, etc.

#### Parameter Description
- `array1`: `array<T>` type, representing the first input array.
- `array2`: `array<T>` type, representing the second input array.

#### Return Result
Returns a new array containing all unique elements from array1 and array2.

#### Usage Example
1. Compute the union of two integer arrays:
```sql
SELECT array_union(array(2, 1, 3, 3), array(3, 5));
-- Return result: [2, 1, 3, 5]
```
2. Find the union of two string arrays:
```sql
SELECT array_union(array('apple', 'orange', 'banana'), array('banana', 'grape', 'apple'));
-- Return result: ['apple', 'orange', 'banana', 'grape']
```
3. Find the union of two arrays of floating-point numbers:
```sql
SELECT array_union(array(1.2, 2.5, 3.7), array(3.7, 4.6, 5.3));
-- Return result: [1.2, 2.5, 3.7, 4.6, 5.3]
```
#### Notes
- If the input array is empty, the ARRAY_UNION function will return an empty array.