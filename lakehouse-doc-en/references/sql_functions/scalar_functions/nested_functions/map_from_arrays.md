### MAP_FROM_ARRAYS
```sql
map_from_arrays(k, v)
```

#### Function
Create a map from two arrays, where the keys and values in the map correspond to the elements in the input arrays by their order. The lengths of the two arrays must be strictly identical.

#### Parameters
- `k`: `array<K>`
- `v`: `array<V>`

#### Return Value
- `map<K, V>`

#### Example
```sql
> SELECT map_from_arrays(k, v)
FROM VALUES
    (ARRAY[1, 2, 3], ARRAY['a', 'b', 'c']),
    (ARRAY[1, 2, 3], ARRAY['a', NULL, 'c']),
    (NULL, ARRAY['a', 'b', 'c']),
    (ARRAY[1, 2, 3], NULL) AS t(k, v);
{1:"a",2:"b",3:"c"}
{1:"a",2:null,3:"c"}
NULL
NULL
```