# TRY_ELEMENT_AT

## Overview

Retrieves a value from an ARRAY or MAP by index or key. Returns NULL instead of throwing an error when the index is out of bounds or the key does not exist. Difference from `ELEMENT_AT`: `ELEMENT_AT` throws an error on out-of-bounds access; `TRY_ELEMENT_AT` returns NULL.

## Syntax

```Plain
TRY_ELEMENT_AT(<array>, <index>)
TRY_ELEMENT_AT(<map>, <key>)
```

## Parameters

- `<array>`: ARRAY type. Uses 1-based positive integer indexing; `-1` refers to the last element.
- `<map>`: MAP type. Uses a key to access the corresponding value.
- `<index>`: BIGINT type. 1-based index; negative values are supported (`-1` is the last element).
- `<key>`: Must match the MAP key type.

## Examples

```sql
-- ARRAY indexing (1-based)
SELECT try_element_at(array(10,20,30), 1);
-- 10

SELECT try_element_at(array(10,20,30), 3);
-- 30

-- Negative index: -1 is the last element
SELECT try_element_at(array(10,20,30), -1);
-- 30

-- Out-of-bounds returns NULL (no error)
SELECT try_element_at(array(10,20,30), 10);
-- NULL

-- MAP key not found returns NULL
SELECT try_element_at(map('a',1,'b',2), 'c');
-- NULL
```

## Related Documentation

- [ELEMENT_AT](../high_order_functions/element_at.md) — version that throws an error on out-of-bounds access
