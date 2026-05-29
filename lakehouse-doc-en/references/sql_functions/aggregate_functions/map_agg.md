### MAP_AGG Function

```
map_agg(key, value)
```

#### Description

The `MAP_AGG` function aggregates key-value pairs into a `MAP` data structure. It collects all key-value pairs and combines them into a Map, where each key corresponds to a value.

#### Parameters

* `key`: An expression of any comparable primitive type, used as the Map key.
  * `NULL` keys are ignored.
  * For duplicate keys, the first occurring value is retained.
* `value`: An expression of any type, used as the Map value.
  * `value` can be `NULL`.

#### Return Type

* Returns `map<key_type, value_type>` type (non-null).
* Returns a Map containing all key-value pairs.

#### Notes

* If all `key` values are `NULL`, an empty Map `{}` is returned.
* If the input is an empty set, an empty Map `{}` is returned.
* The order of keys in the Map is non-deterministic; do not rely on ordering.
* Behavior for duplicate keys may vary by implementation; avoid using duplicate keys where possible.

#### Examples

1. Basic usage: aggregate key-value pairs into a Map

```sql
SELECT map_agg(id, name)
FROM VALUES (1, 'Alice'), (2, 'Bob'), (3, 'Charlie') AS t(id, name);
+---------------------------------+
| map_agg(id, name)               |
+---------------------------------+
| {1:"Alice",2:"Bob",3:"Charlie"} |
+---------------------------------+
```

2. NULL keys are ignored

```sql
SELECT map_agg(a, b)
FROM VALUES (1, 'apple'), (2, 'hi'), (NULL, 'good'), (3, NULL) AS t(a, b);
+--------------------------------+
| map_agg(a, b)                  |
+--------------------------------+
| {1:"apple",2:"hi",3:null}      |
+--------------------------------+
```

3. Duplicate keys: the first value is retained

```sql
SELECT map_agg(a, b)
FROM VALUES (1, 'apple'), (2, 'hi'), (1, 'pie') AS t(a, b);
+-------------------------+
| map_agg(a, b)           |
+-------------------------+
| {1:"apple",2:"hi"}      |
+-------------------------+
```

4. All keys are NULL: returns an empty Map

```sql
SELECT map_agg(a, b)
FROM VALUES (NULL, 'apple'), (NULL, 'banana') AS t(a, b);
+----------------+
| map_agg(a, b)  |
+----------------+
| {}             |
+----------------+
```
