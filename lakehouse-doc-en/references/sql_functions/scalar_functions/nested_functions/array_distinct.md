###  ARRAY_DISTINCT

####  Description
The `ARRAY_DISTINCT` function is used to remove duplicate elements from an array, returning an array without duplicates. This function can handle arrays of any type, including integers, floating-point numbers, strings, etc.

#### Syntax
```
ARRAY_DISTINCT(array)
```
#### Parameter Description
- `array`: `array<T>` type, represents the array that needs to be deduplicated.

#### Return Result
Returns a result of type `array<T>`, which contains the deduplicated array elements.

#### Usage Example
1. Remove duplicates from an integer array:
```sql
SELECT ARRAY_DISTINCT(ARRAY(1, 2, 2, 3));
-- Return result：[1, 2, 3]
```
2. Remove duplicates from an array of floating-point numbers:
```sql
SELECT ARRAY_DISTINCT(ARRAY(3.14, 2.71, 2.71, 1.41));
-- Return result: [3.14, 2.71, 1.41]
```
3. Remove duplicates from a string array:
```sql
SELECT ARRAY_DISTINCT(ARRAY('apple', 'orange', 'apple', 'banana'));
-- Return result: ['apple', 'orange', 'banana']
```
4. Remove duplicates from a mixed-type array:
```sql
SELECT ARRAY_DISTINCT(ARRAY(1, 'a', 2, 'b', 1, 'a', 3));
-- Return result: [1,null,2,3]
```
#### Notes
- When the array is empty, the `ARRAY_DISTINCT` function will return an empty array.