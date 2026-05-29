### ARRAY_INTERSECT

####  Description
The `ARRAY_INTERSECT` function is used to calculate the intersection of two arrays and remove duplicate elements. This function is very useful when processing datasets, especially when you need to find common elements between two datasets.

#### Syntax
```
array_intersect(array1, array2)
```
#### Parameter Description
- `array1` and `array2`: The two arrays for which the intersection needs to be calculated. The array type is `array<T>`, where `T` can be any data type.

#### Return Type
The function returns a new array containing the intersection elements of the two input arrays. The array type is also `array<T>`.

#### Usage Example
1. Calculate the intersection of two integer arrays:
```sql
SELECT array_intersect(array(1, 2, 3, 4), array(3, 4, 5, 6));
```
Return result: `[3, 4]`

2. Calculate the intersection of two string arrays:
```sql
SELECT array_intersect(array('apple', 'banana', 'cherry'), array('banana', 'date', 'cherry'));
```
Return result: `['banana', 'cherry']`

3. Calculate the intersection of two date arrays:
```sql
SELECT array_intersect(array('2021-01-01', '2021-01-02'), array('2021-01-02', '2021-01-03'));
```
Return result：`['2021-01-02']`

#### Notes
- When the two input arrays contain elements of different types, it may cause the function to fail or return unexpected results. Please ensure that the data types of the input arrays are consistent.
- If there are no common elements in both arrays, the function will return an empty array.

By using the `ARRAY_INTERSECT` function, you can easily find the common elements of two arrays, thereby obtaining more accurate results in data analysis and processing.