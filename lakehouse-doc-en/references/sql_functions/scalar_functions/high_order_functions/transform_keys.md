### TRANSFORM_KEYS 

#### Description
The TRANSFORM_KEYS function is used to perform key transformation operations on map-type inputs based on the provided lambda expression. This function will traverse the input map and use the lambda expression to compute new key values, thereby generating a new map.

#### Parameters
- map: The input map-type data, formatted as `map<K, V>`, where K represents the original key type and V represents the original value type.
- (k, v) -> expr: A two-parameter lambda expression, where k corresponds to the key in the original map, and v corresponds to the value in the original map. expr is the return value of the lambda expression, representing the new key type. Note that the return type of expr should match the original key type K.

#### Return Type
The function returns a new map-type data, formatted as `map<K', V>`, where K' is the new key type transformed by the lambda expression, and V is the original value type.

#### Example Usage

**Example 1: Increase the integer value of the key**
```sql
SELECT transform_keys(map(1, 'hello', 2, NULL, 3, 'world'), (k, v) -> CAST(k + 1 AS string));
```
Results:
```
{"2":"hello","3":NULL,"4":"world"}
```
**Example 2: Convert Key to String Type**
```sql
SELECT transform_keys(map(1, 'hello', 2, NULL, 3, 'world'), (k, v) -> CAST(k AS string));
```
Results:
```
{"1":"hello","2":NULL,"3":"world"}
```
**Example 3: Transforming Keys Based on Values in Key-Value Pairs**
```sql
SELECT transform_keys(map(1, 'hello', 2, 'hi', 3, 'world'), (k, v) -> IF(v = 'hello', 'greeting', 'other'));
```
Results:
```
{"greeting":"hello","other":"hi","other":"world"}
```
#### Notes
- Please ensure that the new key type returned by the lambda expression matches the original key type K, otherwise the function will fail to execute.
- When the input map is empty, the function will return an empty map.
- Please ensure that the functions and operators used in the lambda expression are available in the current environment to avoid errors.