# MAP_CONCAT_ARRAY

## Overview

Merges an ARRAY of multiple MAPs into a single MAP. Keys from later MAPs in the array overwrite keys with the same name from earlier MAPs.

## Syntax

```Plain
MAP_CONCAT_ARRAY(<array_of_maps>)
```

## Parameters

- `<array_of_maps>`: `ARRAY<MAP<K, V>>` type. **Note: you must pass a single array containing multiple MAPs, not multiple MAP arguments directly.**

## Examples

```sql
-- Merge multiple MAPs in an array; later entries overwrite earlier ones for duplicate keys
SELECT map_concat_array(array(map('a',1,'b',2), map('b',3,'c',4)));
-- {"a":1,"b":3,"c":4}

-- Incorrect usage: passing multiple MAP arguments directly will cause an error
-- SELECT map_concat_array(map('a',1), map('b',2)); -- error
```

## Related Documentation

- [MAP_CONCAT](sql_functions/scalar_functions/nested_functions/map_concat.md) — merges multiple MAP arguments passed directly
