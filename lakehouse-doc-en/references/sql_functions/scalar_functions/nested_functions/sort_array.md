### SORT_ARRAY 

####  Description
The `SORT_ARRAY` function is used to sort the elements of an array. During the sorting process, `null` values will be placed at the beginning of the array. This function is very useful when dealing with arrays containing multiple data types.

#### Parameter Description
- `array`: `array<T>` type, representing the array to be sorted.
- `asc`: Optional parameter, boolean value, indicating whether to sort in ascending order. The default value is `true`, which means ascending order by default.

#### Return Type
- Returns a sorted array of type `array<T>`.

#### Usage Example
```sql
-- Example 1: Sort an integer array in ascending order
SELECT sort_array(array(2, 1, 3)); -- Return result: [1, 2, 3]

-- Example 2: Sort an array containing null values in ascending order
SELECT sort_array(array(null, 4, 3, null, 5, 6)); -- Return result: [null, null, 3, 4, 5, 6]

-- Example 3: Sort an integer array in descending order
SELECT sort_array(array(2, 1, 3), false); -- Return result: [3, 2, 1]
```