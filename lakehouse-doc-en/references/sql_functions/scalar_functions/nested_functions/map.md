### MAP Function

#### Function Description
The MAP function is used to create a collection of key-value pairs, where each key corresponds to a value. This function allows multiple key-value pairs to be inserted at once, making it convenient for users to quickly construct a map-type data structure.

#### Syntax Format
```
MAP(k1, v1, ..., kN, vN)
```
#### Parameter Description
- k1, ..., kN : Represents the key parameters of the function, of type `K`.
- v1, ..., vN : Represents the value parameters of the function, of type `V`.

#### Return Type
- Returns an object of type `map<K, V>`.

#### Usage Example
1. Create a map containing two key-value pairs:
```sql
SELECT MAP("name", "Alice", "age", '25');
// Returns: {"name":"Alice","age":"25"}
```
2. Construct a map containing three key-value pairs, where one key has the same name but different values:
```sql
SELECT MAP("fruit", "apple", "fruit", "banana", "color", "green");
// Returns: {"fruit":"banana","color":"green"}
```
3. Insert different types of key-value pairs (strings and integers) into the map:
```sql
SELECT MAP("width", 100, "height", 200);
// Returns: {"width":100,"height":200}
```
4. Create an empty map object:
```sql
SELECT MAP();
// Returns: {}
```
#### Notes
- Ensure that the number of provided keys and values appear in pairs, otherwise the function execution will fail.
- If there are duplicate keys, the later key-value pairs will overwrite the earlier ones.
- The MAP function can accept keys and values of any type, but the keys must be of a comparable type to facilitate lookup in the map.