### SIZE

####  Description
1. The `SIZE(array)` function is used to calculate and return the number of elements in an array.
2. The `SIZE(map)` function is used to calculate and return the number of key-value pairs in a map.

#### Syntax
```
SIZE(array)
SIZE(map)
```
#### Parameter Description
- `array`: Array type `array<T>`, representing the array whose elements need to be counted.
- `map`: Map type `map<K, V>`, representing the map whose key-value pairs need to be counted.

#### Return Type
Integer (int)

#### Usage Example
1. Count the number of elements in the array:
```
SELECT SIZE(array(1, 2, 3)); -- Result: 3
```
2. Calculate the number of key-value pairs in the map:
```
SELECT SIZE(map("a", 1, "b", 2)); -- Result: 2
```
#### Notes
- When the passed parameter is not an array or map, the function will return an error.
- If the array or map is empty, the function will return 0.