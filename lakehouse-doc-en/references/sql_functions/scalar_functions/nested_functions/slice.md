### SLICE

#### Overview
The SLICE function is used to extract a subset from an array. Based on the specified starting position (start) and the desired number of elements (limit), the function will return a new array containing up to limit elements. If the specified starting position is a negative number, the position is calculated from the end of the array.

#### Syntax
```
slice(array, start, limit)
```
#### Parameters
- `array`: Type `array<T>`, represents the array to be sliced.
- `start`: Type int, indicates the starting position of the slice. Counting starts from 1. If start is negative, counting starts from the end of the array.
- `limit`: Type int, indicates the number of elements to extract. If this parameter is omitted, all elements from the start position will be returned.

#### Return 
Returns a new array containing up to limit elements starting from the start position.

#### Example 

1. Extract the first two elements from the array:
```
SELECT slice(array(1, 2, 3, 4), 1, 2);
```
Results:
```
[1, 2]
```
2. Extract an element starting from the third element of the array:
```
SELECT slice(array(1, 2, 3, 4), 3, 1);
```
Results:
```
[3]
```
#### Notes
- If the values of start and limit exceed the array range, the function will return an empty array.