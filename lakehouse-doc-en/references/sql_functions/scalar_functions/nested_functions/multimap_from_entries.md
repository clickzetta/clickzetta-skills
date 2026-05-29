###  MULTIMAP_FROM_ENTRIES
``` sql
multimap_from_entries(array)
```

#### Description
Creates a multimap (a map where a single key can correspond to multiple values) from an array. The array format follows that of the `map_entries` function.
Unlike `map_from_entries`, when duplicate keys exist, `multimap_from_entries` aggregates all corresponding values into an array instead of throwing an error or overwriting.

#### Parameters
* array: `array<struct<key:K, value:V>>`

#### Returns
`map<K, array<V>>`

#### Examples
```sql
select multimap_from_entries(array(struct(1, 'a'), struct(2, 'b'), struct(1, 'c')));
-- Result: {1:["a","c"],2:["b"]}
```

```sql
select multimap_from_entries(array(struct(1, 'a'), struct(2, 'b'), struct(3, 'c')));
-- Result: {1:["a"],2:["b"],3:["c"]}
```

```sql
select multimap_from_entries(array(struct(1, 'a'), struct(1, 'b'), struct(1, 'c')));
-- Result: {1:["a","b","c"]}
```

```sql
select multimap_from_entries(array(struct('a', 1), struct('a', 2), struct('b', 3)));
-- Result: {"a":[1,2],"b":[3]}
```

```sql
select multimap_from_entries(array(struct(1, 'a'), struct(2, null), struct(1, 'b')));
-- Result: {1:["a","b"],2:[null]}
```

```sql
select multimap_from_entries(array(struct('x', 1), struct('y', 2), struct('x', 3)));
-- Result: {"x":[1,3],"y":[2]}
```

#### Notes
* Keys cannot be null, otherwise an exception will be thrown
* Values can be null
* Preserves the first-appearance order of keys
