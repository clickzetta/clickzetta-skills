# ARRAY\_POSITION

##  Description

The `array_position` function is used to find the position of an element `element` in a given array `array`. If the element is found, the function returns its starting position in the array (position counting starts from 1); if the element is not found, it returns 0.

## Parameter Description

* `array`: `array<T>` type, representing the array to be searched.
* `element`: T type, representing the element to be searched for.

## Return Value

* Returns an integer representing the position of the element in the array (counting starts from 1). If the element does not exist, it returns 0.

## Usage Example

Here are some examples of using the `array_position` function:

1. Find the position of the number 1 in the array `(1, 2, 3)`:
```sql
SELECT array_position(array(1, 2, 3), 1);
-- Result: 1
```
2. Find the position of the number 4 in the array `(1, 2, 3)`, the expected result is 0 (because 4 does not exist in this array):
```sql
SELECT array_position(array(1, 2, 3), 4);
-- Result: 0
```
3. Find the element "apple" in an array containing strings:
```sql
SELECT array_position(array('banana', 'apple', 'cherry'), 'apple');
-- Result: 2
```
4. Try to find the element "orange" in an empty array, the expected result is 0:
```sql
SELECT array_position(array(), 'orange');
-- Result: 0
```
5. Find the position of the number 3 in an array containing duplicate elements `(1, 2, 3, 3)`:
```sql
SELECT array_position(array(1, 2, 3, 3), 3);
-- Result: 3
```