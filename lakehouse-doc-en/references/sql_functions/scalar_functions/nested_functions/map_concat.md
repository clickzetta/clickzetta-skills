### MAP_CONCAT 

####  Description
The `MAP_CONCAT` function is used to merge key-value pairs from multiple `map` type parameters into a new `map`. This function is very useful when dealing with multiple data sources and needing to integrate their data into a single data structure.

#### Syntax
```
MAP_CONCAT(map1, map2, ..., mapN)
```
#### Parameter Description
- `map1` ~ `mapN`: Input `map` type parameters, which can be two or more. Each parameter is of type `map<K, V>`, where `K` represents the type of the key and `V` represents the type of the value.

#### Return Type
Returns a new `map<K, V>` type that contains all the key-value pairs from the input `map` parameters.

####  Example
1. Basic usage:
```sql
SELECT MAP_CONCAT(map('key1', 'value1'), map('key2', 'value2'));
// Return result: {"key1":"value1","key2":"value2"}
```
In this example, two `map` are merged into one, containing two key-value pairs.

2. Merging multiple parameters:
```sql
SELECT MAP_CONCAT(map('a', 1), map('b', 2), map('c', 3));
// Returns result: {"a":1,"b":2,"c":3}
```
Three `map` are merged into one, forming a new `map` containing three key-value pairs.

3. Handling of duplicate keys:
```sql
SELECT MAP_CONCAT(map('key', 'original'), map('key', 'override'));
// Return result: {"key":"override"}
```
When multiple `map` contain the same key, the value in the latter `map` will overwrite the value in the former `map`.