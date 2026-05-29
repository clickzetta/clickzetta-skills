# MAP_FROM_ARRAYS

## Overview

Constructs a MAP type using two arrays as keys and values respectively. The two arrays must have strictly equal lengths.

> ⚠️ **Note**: Integer keys appear as strings in JSON output (e.g., `{"1":"a"}`). This is normal behavior per the JSON specification; the internal MAP type is unchanged.

## Syntax

```Plain
MAP_FROM_ARRAYS(<keys>, <values>)
```

## Parameters

- `<keys>`: ARRAY&lt;K&gt; type, the array of keys.
- `<values>`: ARRAY&lt;V&gt; type, the array of values. Must have the same length as `<keys>`; values may be NULL. If either argument is NULL, the result is NULL.

## Examples

```sql
SELECT map_from_arrays(array(1, 2, 3), array('a', 'b', 'c'));
-- {"1":"a","2":"b","3":"c"}

SELECT map_from_arrays(array(1, 2, 3), array('a', NULL, 'c'));
-- {"1":"a","2":null,"3":"c"}

SELECT map_from_arrays(NULL, array('a', 'b', 'c'));
-- NULL

SELECT map_from_arrays(array(1, 2, 3), NULL);
-- NULL
```

## Related Documentation

- [MAP_FROM_ENTRIES](map_from_entries.md) — Construct a MAP from an array of key-value pairs
- [MAP_KEYS](map_keys.md) — Extract the key array from a MAP
- [MAP_VALUES](map_values.md) — Extract the value array from a MAP
