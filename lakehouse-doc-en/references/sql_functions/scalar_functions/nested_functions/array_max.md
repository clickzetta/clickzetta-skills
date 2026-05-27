### ARRAY_MAX
#### Description
The `array_max` function is used to find the maximum value from the input array. This function will automatically ignore null values in the array.

#### Syntax
```
array_max(array)
```
#### Parameters
- `array`: `array<T>`, represents the input array, where T is the data type of the array elements.

#### Return Value
- The return type is automatically inferred based on the element type of the input array, i.e., `T <- array<T>`.

#### Usage Example
1. Find the maximum value in an integer array:
```
SELECT array_max(array(1, 2, 3, 4, 5));
```
Results:
```
5
```
2. Find the maximum value in an array of floating-point numbers:
```
SELECT array_max(array(1.2, 2.5, 3.7, 4.4, 5.1));
```
Results:
```
5.1
```
3. Find the maximum value in a string array (lexicographically):
```
SELECT array_max(array('apple', 'banana', 'cherry', 'orange'));
```
Results:
```
'orange'
```
4. Handling Arrays with Null Values:
```
SELECT array_max(array(1, 2, null, 4));
```
Results:
```
4
```
#### Precautions
- When the input array is empty, the `array_max` function will return null.
- If all elements in the array are null, the function will also return null.

With the above examples and explanations, you can use the `array_max` function more effectively to handle the maximum value problem in arrays.