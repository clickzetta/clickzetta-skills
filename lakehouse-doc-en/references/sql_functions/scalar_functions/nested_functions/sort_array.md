# SORT_ARRAY

## Overview

Sorts the elements of an array and returns a new sorted array. NULL values are always placed at the beginning.

## Syntax

```Plain
SORT_ARRAY(<array> [, <asc>])
```

## Parameters

- `<array>`: ARRAY&lt;T&gt; type, the array to sort.
- `<asc>`: BOOLEAN type, optional, defaults to `true` (ascending order); pass `false` for descending order. NULL values are placed at the beginning regardless of sort direction.

## Examples

```sql
SELECT sort_array(array(2, 1, 3));
-- [1,2,3]

SELECT sort_array(array(null, 4, 3, null, 5, 6));
-- [null,null,3,4,5,6]

SELECT sort_array(array(2, 1, 3), false);
-- [3,2,1]
```

## Related Documentation

- [ARRAY_SORT](array_sort.md) — alias with identical functionality
- [REVERSE](reverse.md) — reverses the order of array elements
