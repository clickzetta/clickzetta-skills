### ARRAY_REMOVE

####  Description
The `ARRAY_REMOVE` function is used to remove all items equal to the specified element `element` from the given array `array`. This function accepts two parameters: the first parameter is the array to be operated on, and the second parameter is the element to be removed. After execution, it returns a new array that does not contain items equal to the specified element.

#### Parameter Description
- `array`: `array<T>` type, representing the array to be operated on.
- `element`: T type, representing the element to be removed from the array.

#### Return Result
Returns a new `array<T>` type array that does not contain items equal to the specified element `element`.

#### Usage Example
1. Remove element `1` from an array containing integers:
```sql
SELECT array_remove(array(1, 2, 3), 1);
```
Return Results:
```
[2, 3]
```
2. Remove the element `"apple"` from an array containing strings:
```sql
SELECT array_remove(array("apple", "banana", "cherry", "apple"), "apple");
```
Return Results:
```
["banana", "cherry"]
```
Through the above examples, you can see the application of the `ARRAY_REMOVE` function in different scenarios. This function can be conveniently used to handle array data, meeting your needs in data cleaning, filtering, and other aspects.