### MAP_CONTAINS_KEY 

####  Description
The MAP_CONTAINS_KEY function is used to determine whether a given map type data contains an entry that matches the specified key. When the specified key exists in the map, the function returns true; otherwise, it returns false.

#### Syntax
```
MAP_CONTAINS_KEY(map: map<K, V>, key: K): boolean
```
#### Parameters
- map: The map type data to be checked, where K represents the type of the key, and V represents the type of the value.
- key: The key to be queried, its type should match the key type K in the map.

#### Return Value
Returns a boolean value indicating whether the map contains the specified key.

####  Example
1. Determine if the map contains the key 'a':
```sql
SELECT MAP_CONTAINS_KEY(map('a', 1), 'a'); -- Returns true
```
2. Determine if the map contains the key 'b':
```sql
SELECT MAP_CONTAINS_KEY(map('a', 1), 'b'); -- Returns false
```
3. Suppose there is a map type data with key-value pairs ('name', 'Alice') and ('age', 25), determine if the map contains the key 'name':
```sql
SELECT MAP_CONTAINS_KEY(map('name', 'Alice', 'age', 25), 'name');-- Returns true
```
4. Similarly, check if the above map contains the key 'gender':
```sql
SELECT MAP_CONTAINS_KEY(map('name', 'Alice', 'age', 25), 'gender'); -- Returns false
```