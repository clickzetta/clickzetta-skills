### MAP_VALUES 

####  Description
The MAP_VALUES function is used to extract all the values from the input key-value map and return an array containing these values.

#### Syntax
```
MAP_VALUES(map<K, V>)
```
#### Parameter Description
- map<K, V>: The input key-value mapping, where K represents the type of the key and V represents the type of the value.

#### Return Type
This function returns an array, where the element type in the array is the same as the value type V of the input mapping.

#### Usage Example

**Example 1**: Extracting values from a string key-value mapping
```sql
SELECT MAP_VALUES(map('apple', 5, 'banana', 3, 'orange', 8));
```
Return Results:
```
[5, 3, 8]
```
**Example 2**: Extracting values from complex type key-value mappings
```sql
SELECT MAP_VALUES(map('id', 101, 'name', 'John', 'age', 25));
```
Return Results:
```
[101, null, 25]
```
**Example 3**: Extracting values from an empty map
```sql
SELECT MAP_VALUES(map());
```
Return Results: 
```
[]
```