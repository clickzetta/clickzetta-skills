### MAP_KEYS Function

#### Overview
The `MAP_KEYS` function is used to extract all the key values from the input map type data and return them in the form of an array.

#### Syntax
```
MAP_KEYS(map)
```
#### Parameters
- **map**: The input map data type, where K is the key type and V is the value type.

#### Return Value
Returns an array containing all the key values, of type `array<K>`.

#### Example Usage
1. Extract keys from a simple key-value map:
```sql
SELECT MAP_KEYS(map("Apple", 2, "Banana", 3, "Orange", 4));
-- Return result: ["Apple", "Banana", "Orange"]
```
2. Extract key from nested map:
```sql
SELECT MAP_KEYS(map(map("a", 1, "b", 2), map("c", 3, "d", 4)));
-- Return result: [{"a":1,"b":2}]
```
3. Extract key from an empty map:
```sql
SELECT MAP_KEYS(map());
-- Return result: []
```
#### Notes
- If the input map is empty, the `MAP_KEYS` function will return an empty array.
- The `MAP_KEYS` function does not change the order of keys in the original map.