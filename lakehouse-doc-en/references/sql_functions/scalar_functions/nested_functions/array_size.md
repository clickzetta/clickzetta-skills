### ARRAY_SIZE

#### Description
The `ARRAY_SIZE` function is used to get the number of elements in an array, i.e., the size of the array. This function can handle arrays of various data types, including numbers, strings, booleans, etc.

#### Syntax
```
ARRAY_SIZE(array)
```
#### Parameter Description
* `array`: `array<T>` type, represents the array whose size is to be calculated.

#### Return Type
* Returns an integer, representing the number of elements in the array.

#### Usage Example
1. Calculate the size of a numeric array:
```sql
SELECT ARRAY_SIZE(array(1, 2, 3, 4, 5));
-- Return result: 5
```
2. Calculate the size of the string array:
```sql
SELECT ARRAY_SIZE(array('apple', 'banana', 'cherry'));
-- Return result：3
```
3. Calculate the size of an array containing boolean values:
```sql
SELECT ARRAY_SIZE(array(true, false, true, false, true));
-- Return result: 5
```