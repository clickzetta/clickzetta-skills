### MAP_ZIP_WITH 

####  Description
The MAP_ZIP_WITH function can pair and compute elements with the same key values from two map type data based on a given lambda expression. During the computation, if a key does not have a corresponding value in one of the maps, a NULL value will be supplemented. Ultimately, this function returns a new map that contains the original key values and the new values calculated based on the lambda expression.

#### Parameter Description
- map1, map2: The two input map type data, with the type `map<K, V>`.
- (k, v1, v2) -> expr: A lambda expression in the form of three parameters, where k is the same key value, v1 is the corresponding value in map1, and v2 is the corresponding value in map2. The return type of the lambda expression is not limited.

#### Return Type
Returns a new map type data, with the type `map<K, R>`, where R is the value type calculated by the lambda expression.

#### Usage Example
1. Calculate the sum of the values corresponding to the same key in two maps and return a new map:
```sql
SELECT map_zip_with(map(1, 2, 3, 4), map(2, 3, 4, 5), (k, x, y) -> x + y);
```
Results:
```
{1:null,3:null,2:null,4:null} 
```
2. Convert the values corresponding to the same key in the two maps to strings and concatenate them, returning a new map:
```sql
SELECT map_zip_with(map(1, "a", 2, "b"), map(1, "A", 2, "B"), (k, x, y) -> CONCAT(x, y));
```
Results:
```
{1:"aA", 2:"bB"}
```
3. Perform type conversion and addition on the values corresponding to the same key in two maps, and return a new map:
```sql
SELECT map_zip_with(map(1, 2), map(1, 100, 3, 300), (k, x, y) -> CAST((x + y) AS string));
```
Results:
```
{1:"102", 3:null}
```
#### Notes
- When a key does not have a corresponding value in a map, a NULL value will be added for calculation.
- Ensure that the parameter names in the lambda expression match the order of the actual parameters passed in.
- In the returned new map, the order of the key values may differ from the order in the original map.

Through the above description and examples, you can better understand and use the MAP_ZIP_WITH function. In practical applications, this function can help you flexibly operate and calculate two map-type data.