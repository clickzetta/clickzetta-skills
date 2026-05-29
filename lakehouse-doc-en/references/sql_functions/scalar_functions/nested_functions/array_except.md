### ARRAY_EXCEPT
```
array_except(array1, array2)
```
####  Description
The ARRAY_EXCEPT function is used to compute the difference between two arrays, i.e., to find the elements that exist only in the first array (array1) and remove duplicate elements from the result. This function is very useful when performing set operations, helping users quickly identify the differences between two arrays.

#### Parameter Description
- array1: `array<T>` type, representing the first input array.
- array2: `array<T>` type, representing the second input array.

#### Return Result
Returns a result set of type `array<T>`, which contains elements that exist only in the first array, with no duplicate elements in the result set.

####  Example
1. Find the difference between two integer arrays:
```sql
SELECT array_except(array(1, 2, 3, 4, 5), array(3, 4, 6, 7));
```
Results:
```
[1, 2, 5]
```
2. Find the difference between two string arrays:
```sql
SELECT array_except(array('apple', 'banana', 'orange'), array('banana', 'grape', 'orange'));
```
Results:
```
['apple']
```
Through the above example, it can be seen that the ARRAY_EXCEPT function is very effective in handling array differences. Users can flexibly use this function for set operations according to their needs.