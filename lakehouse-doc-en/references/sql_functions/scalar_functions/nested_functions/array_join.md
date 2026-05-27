###  ARRAY_JOIN

####  Description
The primary purpose of the `ARRAY_JOIN` function is to concatenate the elements of a string array into a single string using a specified delimiter. If there are `NULL` values in the array and the `nullReplacement` parameter is specified, these `NULL` values will be replaced with the string specified by this parameter. If the `nullReplacement` parameter is not provided, the `NULL` values will not be included in the final concatenated result.

#### Parameter Description
* `array`: The input string array, type `array<string>`.
* `delimiter`: The delimiter used between array elements, type `string`.
* `nullReplacement` (optional): The string used to replace `NULL` values in the array, type `string`.

#### Return Type
* Returns a string that contains the concatenated array elements.

#### Example
1. Without using the `nullReplacement` parameter:
```sql
SELECT ARRAY_JOIN(ARRAY('apple', 'banana', 'cherry'), ', ');
```
Results:
```
apple, banana, cherry
```
2. Using the `nullReplacement` parameter:
```sql
SELECT ARRAY_JOIN(ARRAY('apple', NULL, 'cherry'), ', ', 'missing');
```
Results:
```
apple, missing, cherry
```
3. Ignore `NULL` values:
```sql
SELECT ARRAY_JOIN(ARRAY('a', NULL, 'b', NULL), '-');
```
Results:
```
a-b
```
4. Handling arrays containing all `NULL` values:
```sql
SELECT ARRAY_JOIN(ARRAY(NULL, NULL, NULL), ', ', 'N/A');
```
Results:
```
N/A, N/A, N/A 
```
Through the above examples, you can see the usage and results of the `ARRAY_JOIN` function in different scenarios. This function is very useful when you need to merge multiple string elements into a single string, especially when dealing with arrays that contain `NULL` values. It allows you to flexibly choose whether to include these values or replace them with other strings.