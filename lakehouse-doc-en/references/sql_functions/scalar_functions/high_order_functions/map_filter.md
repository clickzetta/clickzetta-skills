### MAP_FILTER 

#### Description
The MAP_FILTER function is used to filter elements of the map type based on a given lambda expression. This function takes two parameters: the first parameter is map type data, and the second parameter is a lambda expression with two arguments, corresponding to the key (k) and value (v) in the map. The lambda expression needs to return a boolean value to determine whether the current key-value pair should be retained in the result.

#### Parameters
- map: Input data of type map<K, V>.
- (k, v) -> expr: A lambda expression with two arguments, where k and v represent the key and value in the map, respectively. The expr needs to return a boolean value indicating whether the current key-value pair should be retained.

#### Return Value
Returns a new map<K, V> type data that only includes key-value pairs that meet the conditions of the lambda expression.

#### Example Usage
1. Filter elements in the map where the key value is less than or equal to 2:
```sql
SELECT `map_filter`(map(2, 'a', 1, 'b', 3, 'c'), (k, v) -> k <= 2);
// Result: {2: "a", 1: "b"}
```
2. Filter elements in the map that are less than or equal to 'b':
```sql
SELECT `map_filter`(map(2, 'a', 1, 'b', 3, 'c'), (k, v) -> v <= 'b');
// Result: {2: "a", 1: "b"}
```
3. Filter elements in the map where the key is an even number:
```sql
SELECT `map_filter`(map(2, 'a', 1, 'b', 4, 'c'), (k, v) -> k % 2 = 0);
// Result: {2: "a", 4: "c"}
```
4. Filter elements in the map with value length greater than 1:
```sql
SELECT `map_filter`(map(2, 'a', 1, 'bb', 3, 'c'), (k, v) -> LENGTH(v) > 1);
// Result: {1: "bb"}
```