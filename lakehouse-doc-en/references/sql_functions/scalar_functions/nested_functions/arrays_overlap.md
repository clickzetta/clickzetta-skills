### ARRAYS_OVERLAP

####  Description
The `arrays_overlap` function is used to check if there is at least one common element between two arrays. Specifically, the function has the following features:
1. If `array1` and `array2` have at least one common element, the function returns `true`.
2. If the two arrays do not intersect, but at least one array contains a `null` value and both arrays are not empty, the function returns `null`.
3. In other cases, the function returns `false`.

#### Parameter Description
- `array1`, `array2`: The two arrays to be compared, of type `array<T>`, where `T` can be any data type supported by the database.

#### Return Type
- The return type is `boolean` or `null`.

#### Usage Example
1. Check if two arrays intersect:
```sql
SELECT arrays_overlap(array(1, 2, 3), array(3, 4, 5)); -- Returns true
```
2. When the array contains `null`:
```sql
SELECT arrays_overlap(array(1, 2, 3), array(null, 4, 5)); -- Returns null
```
3. Two non-empty arrays with no intersection:
```sql
SELECT arrays_overlap(array(1, 2, 3), array(4, 5, 6)); -- Returns false
```
4. A situation where an array is empty:
```sql
SELECT arrays_overlap(array(), array(1, 2, 3)); -- Returns false
```
5. The case where both arrays are empty:
```sql
SELECT arrays_overlap(array(), array()); -- Returns false
```
#### Notes
- When using the `arrays_overlap` function, please note that the types of array elements need to be consistent, otherwise the comparison may fail.
- If the array contains `null` values, the behavior of the function will be different, which needs special attention when using it.