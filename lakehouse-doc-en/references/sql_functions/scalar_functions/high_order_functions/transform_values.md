### TRANSFORM_VALUES

#### Function Description
The `transform_values` function is used to perform value transformation operations on input map type data based on a specified lambda expression. This function accepts two parameters: the first parameter is map type data, and the second parameter is a lambda expression in the form of two arguments, corresponding to the key and value in the map, respectively. The return value of the lambda expression will be returned as the new value.

#### Parameter Description
1. map: Input map type data, formatted as `map<K, V>`, where K represents the type of the key and V represents the type of the value.
2. (k, v) -> expr: A lambda expression in the form of two arguments, used to define the logic of value transformation. k corresponds to the key in the map, and v corresponds to the value in the map. expr is an expression whose return value type will be used as the value type in the new map.

#### Return Type
Returns a new map type data, formatted as `map<R, V>`, where R is the return value type of the lambda expression.

#### Usage Example
1. Example 1: Calculate string length
```sql
SELECT transform_values(map(1, 'hello', 2, NULL, 3, 'world'), (k, v) -> LENGTH(v));
```
Return result:`{1:5, 2:null, 3:5}`
2. Example 2: Convert string to uppercase
```sql
SELECT transform_values(map(1, 'hello', 2, 'sql', 3, 'world'), (k, v) -> UPPER(v));
```
Return result: `{1:'HELLO', 2:'SQL', 3:'WORLD'}`
3. Example 3: Add a suffix to each key-value pair
```sql
SELECT transform_values(map(1, 'hello', 2, 'world'), (k, v) -> CONCAT(v, '_suffix'));
```
Return result:`{1:'hello_suffix', 2:'world_suffix'}`

#### Notes
1. When the values in the input map type data are NULL, the lambda expression needs to handle NULL values, otherwise it may cause the function to fail.
2. Please ensure that the return type of the lambda expression is consistent with the expected value type of the new map type data.

By using the `transform_values` function, you can flexibly perform various transformation operations on map type data to meet different business needs.