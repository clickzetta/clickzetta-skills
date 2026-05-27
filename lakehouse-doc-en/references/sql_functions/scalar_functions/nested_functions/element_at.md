###  ELEMENT_AT
``` sql
element_at(array, index)
element_at(map, key)
```

#### Description
For array type, returns the element at the given index (1-based).
For map type, returns the value corresponding to the key; returns NULL if the key does not exist.

#### Parameters
* array: `array<T>`
* index: bigint
* map: `map<K, V>`
* key: K

#### Returns
* Array variant derived from input: `T <- array<T>`
* Map variant derived from input: `V <- map<K, V>`

#### Examples
```sql
SELECT element_at(array(1, 2, 3), 2);
-- Result: 2
```

```sql
SELECT try_element_at(array(1, 2, 3), 5);
-- Result: NULL
```

```sql
SELECT element_at(map(1, 'a', 2, 'b'), 2);
-- Result: b
```

```sql
SELECT element_at(map(1, 'a', 2, 'b'), 3);
-- Result: NULL
```
