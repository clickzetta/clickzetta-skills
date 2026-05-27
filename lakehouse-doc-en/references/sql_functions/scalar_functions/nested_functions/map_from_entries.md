### MAP\_FROM\_ENTRIES 

#### Description
The `MAP_FROM_ENTRIES` function is used to create a map type from an array. The elements of the input array need to conform to the format of the `map_entries` function, where each element is a struct containing `key` and `value` properties.

#### Parameters
* `array`: Input parameter, type `array<struct<key:K, value:V>>`, representing an array containing multiple structs, each with `key` and `value` properties.

#### Return Value
Returns a result of type `map<K, V>`, where `K` represents the type of the key and `V` represents the type of the value.

#### Example Usage
1. Create an array containing two elements, each of which is a struct with two properties: `key` and `value`.
```sql
SELECT MAP_FROM_ENTRIES(ARRAY(
NAMED_STRUCT('key',1, 'value','a'),
NAMED_STRUCT('key',2, 'value','b')
));

```
Return Results: 
```
{
  1:"a",
  2:"b"
}
```
2. Create an array containing three elements, where the element type is a structure, and the structure contains different types of keys and values.
```sql
SELECT MAP_FROM_ENTRIES(ARRAY(
NAMED_STRUCT('key',1, 'value','apple' ),
NAMED_STRUCT('key',2, 'value','carrot'),
NAMED_STRUCT('key',3, 'value','dog')
));


```
Return Results:
```
{
  1:"apple",
  2:"carrot",
  3:"dog"
}
```
Note: In the above example, the `extra` attribute will not be included in the final map because we only care about the `key` and `value` attributes.

#### Notes
* Each struct in the input array must have `key` and `value` attributes, otherwise the function will fail.
* The type of the key needs to be unique, and there cannot be duplicate key values, otherwise the later key values will overwrite the earlier key values.