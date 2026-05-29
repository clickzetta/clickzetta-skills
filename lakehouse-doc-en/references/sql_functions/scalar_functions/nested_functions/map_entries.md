### MAP_ENTRIES

#### Description
The `MAP_ENTRIES` function is used to convert input data of Map type into an array, where each element in the array is a struct that contains two fields corresponding to the key and value in the Map.

#### Syntax
```
MAP_ENTRIES(map<K, V>)
```
#### Parameters
- `map`: Input Map type data, where `K` represents the type of the key, and `V` represents the type of the value.

#### Return Result
Returns an array, where each element in the array is a struct containing two fields: `key` and `value`, corresponding to the key and value in the Map respectively.

####  Example
1. Basic usage:
   ```sql
   SELECT MAP_ENTRIES(map(1, 'a', 2, 'b'));
   ```
Return Results:
   ```
   [{"key":1,"value":"a"},{"key":2,"value":"b"}]
   ```
2. Use in conjunction with other functions:
   ```sql
   SELECT MAP_ENTRIES(map_filter(map(1, 'a', 2, 'b'), (key,v)->key > 1));
   ```
Return Results:
   ```
   [{"key":2,"value":"b"}]
   ```
3. Nested Map Conversion:
   ```sql
   SELECT MAP_ENTRIES(map(map(1, 'a'), map(2, 'b')));
   ```
Return Results:
   ```
   [{"key":{1:"a"},"value":{2:"b"}}] 
   ```